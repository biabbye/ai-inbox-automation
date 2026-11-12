from uuid import uuid4

import httpx
import pytest

from auth import InvalidAccessTokenError, verify_access_token


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_verify_access_token_returns_the_verified_user_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = uuid4()
    monkeypatch.setenv("SUPABASE_URL", "http://supabase.test")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "test-publishable-key")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "http://supabase.test/auth/v1/user"
        assert request.headers["authorization"] == "Bearer test-access-token"
        assert request.headers["apikey"] == "test-publishable-key"

        return httpx.Response(200, json={"id": str(user_id)})

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        authenticated_user_id = await verify_access_token(
            "test-access-token",
            client=client,
        )

    assert authenticated_user_id == user_id

@pytest.mark.anyio
async def test_verify_access_token_rejects_an_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_URL", "http://supabase.test")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "test-publishable-key")

    transport = httpx.MockTransport(
        lambda _request: httpx.Response(401)
    )

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(InvalidAccessTokenError):
            await verify_access_token(
                "invalid-access-token",
                client=client,
            )
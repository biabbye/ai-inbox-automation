import os
from uuid import UUID
from typing import Annotated
from fastapi import Header, HTTPException, status
import httpx


class InvalidAccessTokenError(Exception):
    pass


class AuthenticationServiceUnavailableError(Exception):
    pass


async def verify_access_token(
    access_token: str,
    *,
    client: httpx.AsyncClient,
) -> UUID:
    supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
    publishable_key = os.environ["SUPABASE_PUBLISHABLE_KEY"]

    try:
        response = await client.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": publishable_key,
            },
        )
    except httpx.RequestError as error:
        raise AuthenticationServiceUnavailableError from error

    if response.status_code in {401, 403}:
        raise InvalidAccessTokenError

    if response.status_code != 200:
        raise AuthenticationServiceUnavailableError

    try:
        return UUID(response.json()["id"])
    except (KeyError, TypeError, ValueError):
        raise InvalidAccessTokenError


def _unauthorized_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> UUID:
    if authorization is None:
        raise _unauthorized_error()

    scheme, separator, access_token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not separator or not access_token.strip():
        raise _unauthorized_error()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            return await verify_access_token(
                access_token.strip(),
                client=client,
            )
    except InvalidAccessTokenError:
        raise _unauthorized_error()
    except AuthenticationServiceUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable.",
        )
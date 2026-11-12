import { NextResponse } from "next/server";

import { createClient } from "@/lib/supabase/server";

type RouteContext = {
  params: Promise<{ organizationId: string }>;
};

export async function GET(
  _request: Request,
  { params }: RouteContext,
) {
  const { organizationId } = await params;
  const backendApiUrl = process.env.BACKEND_API_URL;

  if (!backendApiUrl) {
    return NextResponse.json(
      { detail: "Backend API URL is not configured." },
      { status: 500 },
    );
  }

  const supabase = await createClient();
  const { data: claimsData } = await supabase.auth.getClaims();

  if (!claimsData?.claims) {
    return NextResponse.json(
      { detail: "Authentication is required." },
      { status: 401 },
    );
  }

  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    return NextResponse.json(
      { detail: "Authentication session is unavailable." },
      { status: 401 },
    );
  }

  try {
    const backendResponse = await fetch(
      `${backendApiUrl}/organizations/${organizationId}/tickets`,
      {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
        cache: "no-store",
        signal: AbortSignal.timeout(5_000),
      },
    );

    const responseBody = await backendResponse.json().catch(() => ({
      detail: "Backend returned an invalid response.",
    }));

    return NextResponse.json(responseBody, {
      status: backendResponse.status,
    });
  } catch {
    return NextResponse.json(
      { detail: "Backend service is unavailable." },
      { status: 503 },
    );
  }
}
import { NextResponse } from "next/server";

import { createClient } from "@/lib/supabase/server";


export async function GET() {
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
      `${backendApiUrl}/organizations`,
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

export async function POST(request: Request) {
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

  let requestBody: unknown;

  try {
    requestBody = await request.json();
  } catch {
    return NextResponse.json(
      { detail: "Request body must be valid JSON." },
      { status: 400 },
    );
  }

  try {
    const backendResponse = await fetch(
      `${backendApiUrl}/organizations`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
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
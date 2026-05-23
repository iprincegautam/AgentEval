import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  let body: { repo_url?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.repo_url?.trim()) {
    return NextResponse.json({ error: "repo_url is required" }, { status: 400 });
  }

  try {
    const res = await fetch(`${BACKEND_URL}/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: body.repo_url.trim() }),
    });

    const data = await res.json();
    if (!res.ok) {
      return NextResponse.json(
        { error: data.detail || "Backend evaluation failed" },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Failed to reach evaluation backend";
    return NextResponse.json(
      {
        error: `${message}. Is the FastAPI server running at ${BACKEND_URL}?`,
      },
      { status: 502 }
    );
  }
}

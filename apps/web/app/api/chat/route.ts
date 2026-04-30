import { NextRequest, NextResponse } from "next/server";

import { chatRequestSchema } from "@/lib/chat-schema";
import { runAgent } from "@/lib/agent-core";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = chatRequestSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json({ error: "Invalid request" }, { status: 400 });
    }

    const agentResponse = runAgent(result.data.message, result.data.messages);
    return NextResponse.json(agentResponse);
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

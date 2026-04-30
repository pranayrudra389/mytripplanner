import type { ChatMessage, ChatResponse, Intent } from "./chat-schema";

function classifyIntent(message: string): Intent {
  const text = message.toLowerCase();

  if (['plan', 'trip', 'road trip', 'travel', 'visit', 'days'].some((kw) => text.includes(kw))) {
    return 'CREATE_TRIP';
  }

  if (["change", "replace", "remove", "add", "make it", "relaxed", "packed"].some((kw) => text.includes(kw))) {
    return 'MODIFY_TRIP';
  }

  return 'ASK_QUESTION';
}

function buildResponse(intent: Intent): string {
  switch(intent) {
    case 'CREATE_TRIP':
      return "Great, let's plan your trip! Where are you starting from, and what are your travel dates?";
    case 'MODIFY_TRIP':
      return "Sure, I can adjust that. What would you like to change?";
    case "ASK_QUESTION":
      return "I can help with trip planning, itineraries, and travel suggestions. What would you like to know?";
  }
}

export function runAgent(message: string, history: ChatMessage[]): ChatResponse {
  const intent = classifyIntent(message);
  const content = buildResponse(intent);

  return {
    message: {
      id: `assistant-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      role: 'assistant',
      content,
      createdAt: new Date().toISOString(),
    },
    intent,
  };
}

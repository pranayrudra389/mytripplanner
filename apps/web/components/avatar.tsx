import { Bot, User } from "lucide-react";

import type { ChatMessage } from "@/lib/chat-schema";
import { cn } from "@/lib/utils";

export function Avatar({ role }: { role: ChatMessage["role"] }) {
  const Icon = role === "assistant" ? Bot : User;

  return (
    <div
      className={cn(
        "mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
        role === "assistant"
          ? "bg-accent text-accent-foreground"
          : "bg-secondary text-secondary-foreground",
      )}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
    </div>
  );
}

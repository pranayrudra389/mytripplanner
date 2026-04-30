import type { ChatMessage } from "@/lib/chat-schema";
import { cn, formatTime } from "@/lib/utils";

import { Avatar } from "./avatar";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser ? <Avatar role="assistant" /> : null}
      <div className={cn("max-w-[82%]", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "rounded-lg px-4 py-3 text-sm leading-6",
            isUser
              ? "bg-primary text-primary-foreground"
              : "border bg-background text-foreground",
          )}
        >
          {message.content}
        </div>
        <p className={cn("mt-1 text-xs text-muted-foreground", isUser ? "text-right" : "text-left")}>
          {formatTime(message.createdAt)}
        </p>
      </div>
      {isUser ? <Avatar role="user" /> : null}
    </div>
  );
}

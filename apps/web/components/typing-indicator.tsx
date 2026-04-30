import { Avatar } from "./avatar";

export function TypingIndicator() {
  return (
    <div className="flex justify-start gap-3">
      <Avatar role="assistant" />
      <div className="rounded-lg border bg-background px-4 py-3">
        <div className="flex items-center gap-1" aria-label="Assistant is typing">
          <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.2s]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.1s]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
        </div>
      </div>
    </div>
  );
}

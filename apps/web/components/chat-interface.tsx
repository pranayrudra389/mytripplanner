"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Bot, CalendarDays, MapPinned, Send, Sparkles, User } from "lucide-react";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const chatMessageSchema = z.object({
  id: z.string(),
  role: z.enum(["assistant", "user"]),
  content: z.string().min(1),
  createdAt: z.date(),
});

type ChatMessage = z.infer<typeof chatMessageSchema>;
type ActivePanel = "chat" | "itinerary";

const starterPrompts = [
  "Plan a 3-day road trip to San Diego from Phoenix.",
  "I want beaches, Indian food, and easy parking.",
  "Make the trip relaxed with hidden gems.",
];

const assistantReplies = [
  "That sounds like a great start. For Feature 1 I am using a stub response, but this is where I will ask follow-up travel questions next.",
  "Got it. I would normally collect dates, travelers, budget, food preferences, and pace before building the itinerary.",
  "I can help shape that into a day-by-day plan once the agent and itinerary generation features are connected.",
];

function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return chatMessageSchema.parse({
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    content,
    createdAt: new Date(),
  });
}

function formatTime(date: Date) {
  return new Intl.DateTimeFormat("en", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    createMessage(
      "assistant",
      "Hi, I am your trip planning assistant. Tell me where you want to go, how long you have, and what kind of trip you want.",
    ),
  ]);
  const [activePanel, setActivePanel] = useState<ActivePanel>("chat");
  const [input, setInput] = useState("");
  const [isAssistantTyping, setIsAssistantTyping] = useState(false);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);
  const replyIndex = useMemo(() => messages.filter((message) => message.role === "user").length, [messages]);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isAssistantTyping]);

  function sendMessage(content: string) {
    const trimmed = content.trim();

    if (!trimmed || isAssistantTyping) {
      return;
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      createMessage("user", trimmed),
    ]);
    setInput("");
    setIsAssistantTyping(true);

    window.setTimeout(() => {
      setMessages((currentMessages) => [
        ...currentMessages,
        createMessage(
          "assistant",
          assistantReplies[replyIndex % assistantReplies.length],
        ),
      ]);
      setIsAssistantTyping(false);
    }, 850);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    sendMessage(input);
  }

  return (
    <main className="h-dvh overflow-hidden px-4 py-4 text-foreground sm:px-6 lg:px-8">
      <div className="mx-auto grid h-full min-h-0 max-w-7xl grid-rows-[auto_minmax(0,1fr)] gap-4 lg:auto-rows-fr lg:grid-cols-[minmax(0,0.95fr)_minmax(360px,0.65fr)] lg:grid-rows-none">
        <div className="grid self-start lg:hidden">
          <div className="grid grid-cols-2 rounded-lg border bg-card p-1 shadow-sm">
            <button
              className={cn(
                "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                activePanel === "chat"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
              onClick={() => setActivePanel("chat")}
              type="button"
            >
              Chat
            </button>
            <button
              className={cn(
                "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                activePanel === "itinerary"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
              onClick={() => setActivePanel("itinerary")}
              type="button"
            >
              Itinerary
            </button>
          </div>
        </div>

        <section
          className={cn(
            "min-h-0 flex-col overflow-hidden rounded-lg border bg-card shadow-panel lg:flex",
            activePanel === "chat" ? "flex" : "hidden",
          )}
        >
          <header className="flex shrink-0 items-center justify-between border-b px-4 py-3 sm:px-5">
            <div className="flex min-w-0 items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <Sparkles className="h-5 w-5" aria-hidden="true" />
              </div>
              <div className="min-w-0">
                <h1 className="truncate text-base font-semibold">MyTripPlanner</h1>
                <p className="truncate text-sm text-muted-foreground">Chat-first trip planning</p>
              </div>
            </div>
            <div className="hidden items-center gap-2 rounded-md border bg-muted px-3 py-1.5 text-xs font-medium text-muted-foreground sm:flex">
              <span className="h-2 w-2 rounded-full bg-primary" />
              Stub assistant
            </div>
          </header>

          <div className="min-h-0 flex-1 overflow-y-auto px-4 py-5 sm:px-5">
            <div className="space-y-5">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}

              {isAssistantTyping ? <TypingIndicator /> : null}
              <div ref={scrollAnchorRef} />
            </div>
          </div>

          <div className="shrink-0 border-t bg-card px-4 py-4 sm:px-5">
            <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
              {starterPrompts.map((prompt) => (
                <button
                  className="shrink-0 rounded-md border bg-background px-3 py-2 text-left text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                  disabled={isAssistantTyping}
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  type="button"
                >
                  {prompt}
                </button>
              ))}
            </div>

            <form className="flex items-end gap-3" onSubmit={handleSubmit}>
              <Textarea
                aria-label="Message"
                className="max-h-40 min-h-12 resize-none"
                disabled={isAssistantTyping}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage(input);
                  }
                }}
                placeholder="Tell me about your trip..."
                value={input}
              />
              <Button
                aria-label="Send message"
                className="shrink-0"
                disabled={!input.trim() || isAssistantTyping}
                size="icon"
                type="submit"
              >
                <Send className="h-4 w-4" aria-hidden="true" />
              </Button>
            </form>
          </div>
        </section>

        <ItineraryPreview
          className={cn(
            "min-h-0 shadow-panel lg:flex",
            activePanel === "itinerary" ? "flex" : "hidden",
          )}
        />
      </div>
    </main>
  );
}

function ItineraryPreview({ className }: { className?: string }) {
  return (
    <aside className={cn("flex-col overflow-hidden rounded-lg border bg-card", className)}>
      <div className="shrink-0 border-b px-5 py-4">
        <p className="text-sm font-semibold">Itinerary Preview</p>
        <p className="mt-1 text-sm text-muted-foreground">Your structured trip plan will appear here in a later feature.</p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-5">
        <div className="flex min-h-full flex-col justify-start gap-4 lg:justify-center">
          <div className="rounded-lg border bg-background p-4">
            <div className="flex items-center gap-3">
              <MapPinned className="h-5 w-5 text-primary" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium">Destination</p>
                <p className="text-sm text-muted-foreground">Waiting for trip details</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="flex items-center gap-3">
              <CalendarDays className="h-5 w-5 text-primary" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium">Day-by-day plan</p>
                <p className="text-sm text-muted-foreground">Generated itinerary cards come next</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
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

function Avatar({ role }: { role: ChatMessage["role"] }) {
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

function TypingIndicator() {
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

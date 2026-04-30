"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";

import type { ChatMessage, Intent } from "@/lib/chat-schema";
import { INITIAL_GREETING, STARTER_PROMPTS } from "@/lib/constants";
import { cn, createMessage } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ItineraryPreview } from "./itinerary-preview";
import { MessageBubble } from "./message-bubble";
import { TypingIndicator } from "./typing-indicator";

type ActivePanel = "chat" | "itinerary";

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    createMessage("assistant", INITIAL_GREETING),
  ]);
  const [activePanel, setActivePanel] = useState<ActivePanel>("chat");
  const [input, setInput] = useState("");
  const [isAssistantTyping, setIsAssistantTyping] = useState(false);
  const [lastIntent, setLastIntent] = useState<Intent | null>(null);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isAssistantTyping]);

  async function sendMessage(content: string) {
    const trimmed = content.trim();

    if (!trimmed || isAssistantTyping) {
      return;
    }

    const updatedMessages = [...messages, createMessage("user", trimmed)];
    setMessages(updatedMessages);
    setInput("");
    setIsAssistantTyping(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, messages: updatedMessages }),
      });

      if (!res.ok) {
        throw new Error(`API error ${res.status}`);
      }

      const data = await res.json();
      setMessages((current) => [...current, data.message]);
      setLastIntent(data.intent);
    } catch {
      setMessages((current) => [
        ...current,
        createMessage("assistant", "Sorry, something went wrong. Please try again."),
      ]);
    } finally {
      setIsAssistantTyping(false);
    }
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
              {lastIntent ? `Intent: ${lastIntent}` : "Agent ready"}
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
              {STARTER_PROMPTS.map((prompt) => (
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

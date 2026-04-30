import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

import type { ChatMessage } from "./chat-schema";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function formatTime(date: string) {
  return new Intl.DateTimeFormat("en", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(date));
}

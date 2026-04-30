import { z } from 'zod';

export const intentSchema = z.enum([
  'CREATE_TRIP',
  'MODIFY_TRIP',
  'ASK_QUESTION'
]);

export const chatMessageSchema = z.object({
  id: z.string(),
  role: z.enum(['assistant', 'user']),
  content: z.string().min(1),
  createdAt: z.string(),
});

export const chatRequestSchema = z.object({
  message: z.string().trim().min(1).max(5000),
  messages: z.array(chatMessageSchema),
});

export const chatResponseSchema = z.object({
  message: chatMessageSchema,
  intent: intentSchema,
});

export type Intent = z.infer<typeof intentSchema>;
export type ChatMessage = z.infer<typeof chatMessageSchema>
export type ChatRequest = z.infer<typeof chatRequestSchema>
export type ChatResponse = z.infer<typeof chatResponseSchema>

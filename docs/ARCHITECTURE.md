# 🏗️ MyTripPlanner – Architecture Plan

---

## 1. Overview

**MyTripPlanner** is a **chat-first AI travel concierge** that generates, customizes, and manages trips conversationally.

It is designed with a **modular agent architecture** so the same core can later support:

- Travel
- Restaurants
- Forms
- Other domains

---

## 2. Architecture Principles

- Chat-first (not form-heavy)
- Structured data (not plain text)
- Modular (Agent Core + Plugins)
- Scalable (future domains)
- Voice-ready (future expansion)
- API-driven
- UI + AI tightly integrated

---

## 3. High-Level Architecture

```

Frontend (Next.js)
↓
API Layer (Node.js / Next API)
↓
Agent Core (AI Orchestration)
↓
Travel Plugin (Domain Logic)
↓
Tools + Database + External APIs

```

---

## 4. Frontend Layer

### Tech Stack
- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS

### Core Components

#### 1. Chat UI
- Conversational interface
- Sends messages to `/api/chat`
- Streams responses (SSE/WebSocket)

#### 2. Itinerary View (Split Screen)
- Day-wise cards
- Structured layout

Each item includes:
- Place name
- Address
- Time
- Parking
- Tickets
- Reservations
- Cost
- Notes

#### 3. Trip Dashboard
- View saved trips
- Resume planning

#### 4. Trip Wizard
- Structured input (first-time setup)

#### 5. Map View (Phase 4)
- Pins
- Routes
- Nearby search

#### 6. Voice UI (Future)
- Mic input
- Read-aloud

---

## 5. Backend Layer

### Tech Stack
- Node.js
- TypeScript
- Express OR Next.js API Routes

---

### Responsibilities

#### 1. Chat API
```

POST /api/chat

```
- Receives user input
- Calls Agent Core
- Streams response

---

#### 2. Trip APIs
```

POST   /api/trips
GET    /api/trips
GET    /api/trips/:id
PUT    /api/trips/:id
DELETE /api/trips/:id

```

---

#### 3. Itinerary APIs
```

POST /api/trips/:id/generate
POST /api/trips/:id/customize
POST /api/trips/:id/replan

```

---

#### 4. AI APIs
```

POST /api/ai/intent
POST /api/ai/extract
POST /api/ai/recommend
POST /api/ai/enrich

```

---

#### 5. Voice APIs (Future)
```

POST /api/voice/transcribe
POST /api/voice/speak
POST /api/voice/session

```

---

## 6. Agent Architecture (Core Design)

```

User Message
↓
Intent Detection
↓
Entity Extraction
↓
Router
↓
Agent Module
↓
Tool Calls / DB / APIs
↓
Response Generator
↓
UI Update

```

---

## 7. Agent Core Responsibilities

- Intent detection
- Entity extraction
- Routing
- Conversation memory
- Guardrails
- Logging

---

## 8. Core Intents

```

CREATE_TRIP
CUSTOMIZE_TRIP
ADD_PLACE
REMOVE_PLACE
REPLACE_PLACE
MOVE_PLACE
ADD_RESTAURANT
ADD_PARKING_DETAILS
ADD_TICKET_DETAILS
MAKE_RELAXED
MAKE_PACKED
REDUCE_COST
REPLAN_DAY
ASK_TRIP_QUESTION
EXPORT_TRIP
VOICE_COMMAND

```

---

## 9. Agent Modules

| Agent | Responsibility |
|------|--------|
| Triage Agent | Intent detection |
| Entity Extractor | Structured data |
| Trip Generator | Create itinerary |
| Recommendation Agent | Rank places |
| Place Enrichment Agent | Add details |
| Parking Agent | Parking info |
| Ticket Agent | Ticket/reservation info |
| Food Agent | Restaurants |
| Budget Agent | Cost |
| Replanning Agent | Modify itinerary |
| Trip Q&A Agent | Answer questions |
| Voice Agent | Voice interaction |

---

## 10. Travel Plugin

Handles domain-specific logic:

- Trip generation
- Itinerary structuring
- Category handling
- Customization actions

---

## 11. Data Layer

### Database: PostgreSQL

---

### Tables

#### users
```

id, name, email, created_at

```

#### traveler_profiles
```

user_id, preferences, budget, interests

```

#### trips
```

id, user_id, origin, destination, dates

```

#### trip_days
```

trip_id, day_number, summary

```

#### itinerary_items
```

trip_day_id, place_id, time, cost

```

#### places
```

name, category, location, parking, tickets

```

#### restaurants
```

name, cuisine, location

```

#### conversations
```

user_id, trip_id

```

#### messages
```

conversation_id, role, content

```

#### itinerary_versions
```

trip_id, snapshot

```

---

## 12. AI Layer

### Components

- LLM (OpenAI / Ollama)
- LangChain / LangGraph (optional future)
- Prompt system
- Tool calling

---

### Tools

- search_places
- search_restaurants
- enrich_parking
- enrich_tickets
- get_weather
- estimate_budget

---

## 13. External Integrations

- Google Maps / Places
- Weather API
- (Future) Restaurant APIs
- (Future) Booking APIs

---

## 14. Streaming Design

- Use SSE or WebSockets
- Token-by-token streaming
- Tool calls pause streaming

---

## 15. Deployment Architecture

### Dev

- Monorepo
- Docker Compose
- Local PostgreSQL

---

### Production

- Frontend: Vercel
- Backend: Node server / container
- DB: Supabase / RDS
- Cache: Redis

---

## 16. Security

- Prompt injection protection
- Rate limiting
- Input validation
- HTTPS
- Confirmation for destructive actions

---

## 17. Guardrails

Require confirmation for:

- Regenerate full trip
- Delete items
- Replace itinerary
- Export/share

---

## 18. Observability

- Logs
- Metrics
- AI feedback
- User actions

---

## 19. Extensibility (Future)

Plugin-based system:

```

/plugins
/travel
/restaurant
/forms

```

Each plugin defines:

- intents
- tools
- prompts
- workflows

---

## 20. Voice Architecture (Future)

```

Voice Input → STT → Agent Core → Response → TTS → Audio Output

```

---

## 21. Key Strengths of This Architecture

- Modular
- Scalable
- Reusable
- Chat-first
- Voice-ready
- Production-friendly

---

## 22. Summary

> MyTripPlanner is built as a **modular AI concierge platform**, not just a trip generator.

It enables:

- Structured itineraries
- Real-time customization
- Trip reasoning
- Future voice support
- Multi-domain expansion

---

```

---

## 🚀 What you should do next

1. Save this as:

```
/docs/ARCHITECTURE.md
```

2. Also create (next step I can help you):

```
/docs/API_DESIGN.md
/docs/DATABASE_SCHEMA.md
/docs/AI_AGENT_DESIGN.md
/docs/ROADMAP.md
```

---

## 💡 Small but important insight

You’re not building:

> “a travel app”

You’re building:

> **a reusable AI concierge system with travel as the first domain**

This is exactly the same pattern used by Holland America’s AI concierge (Anna)  — but you’re doing it as a startup-grade platform.

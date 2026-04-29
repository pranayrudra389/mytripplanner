# Architecture Plan for MyTripPlanner

This document outlines the high‑level architecture for MyTripPlanner, a chat‑first AI travel concierge that generates structured itineraries and supports real‑time customization. It is designed around a reusable agent core with domain‑specific plugins, so future domains (e.g. restaurant ordering or form replacement) can reuse the same foundation.

## High‑Level Overview

The system consists of three major layers:

- Presentation Layer – A Next.js web application that provides a chat interface and a live itinerary preview.
- Application Layer – A Node.js/TypeScript backend exposing API routes, orchestrating the agent, and managing business logic.
- Data & AI Layer – Databases and AI services used to store data, run the agent, and retrieve external information.

These layers communicate over secure HTTP/WebSocket interfaces. The backend exposes a REST/GraphQL API for CRUD operations on trips and uses streaming endpoints for real‑time agent responses. It also houses the agent core and domain plugins, built with LangGraph.

## Frontend (Presentation Layer)

The frontend is a Next.js application using React and Tailwind CSS. It includes:

- Chat UI – Users converse with the travel assistant. Messages are sent to /api/chat and responses are streamed back via Server‑Sent Events or WebSockets for immediate feedback.
- Itinerary Viewer – A split‑screen panel shows the generated itinerary. It displays day cards with details such as address, timings, costs, parking and ticket info. Users can edit items inline.
- Trip Dashboard – Stores and lists saved trips, allowing users to reopen and continue planning.
- Forms & Modals – Used for confirmations (guardrails) when regenerating or deleting trips.
- Reusable Components – Buttons, modals, cards and tables built with Tailwind CSS and shadcn/ui to maintain a consistent look and feel.

## Client/Server Communication

The frontend communicates with the backend via:

- HTTP API – For creating, reading, updating and deleting trips, as well as loading saved trips.
- Streaming Endpoint – A long‑lived connection (SSE or WebSocket) for agent responses so users can see the assistant typing in real time.
- Authentication Middleware – V1 can run unauthenticated, but the architecture is ready for adding JWT or session‑based auth later.

## Backend (Application Layer)

The backend is built in Node.js using TypeScript and exposes API routes (or an Express server). Its responsibilities include:

- Agent Invocation – It receives chat messages, invokes the agent core, manages the agent state and returns streaming responses.
- Trip Management API – CRUD endpoints under /api/trips for saving, retrieving and updating itineraries.
- Travel Plugin Logic – Domain‑specific logic for trip creation, customization and enrichment lives here.
- Guardrail Enforcement – Confirmation middleware prompts users before destructive changes (regenerate, delete, overwrite, export).
- External Integrations – Connects to external APIs (hotel search, attractions, weather) via defined tools when the agent requests them.

## Modular Architecture

The backend is designed around a plugin architecture:

- Agent Core – Provides intent detection, entity extraction, state management, and tool routing. It exposes a generic handleMessage function. Only core logic sits here; no domain logic.
- Travel Plugin – Implements domain‑specific functions (createTrip, modifyTrip, addRestaurant, addParking, etc.) and defines prompts and budgets. All travel logic is encapsulated in this plugin. It registers its tools with the agent core.
- Future Plugins – Additional directories (e.g. restaurant, forms) can be created with the same contract (setup, intents, tools). The agent core dynamically loads plugins based on configuration.

## Routing & Orchestration

The agent uses LangGraph, a library for graph‑based LLM orchestration. The travel plugin defines nodes such as:

- Gather – Conversationally collects required preferences (origin, destination, dates, number of travelers, budget, travel pace, interests, must‑visit and avoid lists). It uses prompts.gather from the PRD.
- Extract – Converts the conversation into structured JSON using prompts.extract. The output populates a TripPreferences object.
- Research – Calls external tools (search_hotels, search_attractions, search_transport, get_weather) to gather data. Ensures at least two tool calls per research cycle.
- Build – Generates a day‑by‑day itinerary from research data, enforcing budget constraints and user preferences. It calculates daily budgets and includes hotels, activities and food estimates.
- Reflect – Reviews the itinerary for balance, budget compliance and realism. If issues are found and revision limits are not exceeded, it routes back to Build.
- Present – Converts the itinerary into a markdown format and extracts structured data for the frontend. It provides the final itinerary and cost breakdown.

The routing.py file in the repo defines functions that govern transitions between these nodes and enforce maximum research/revision rounds.

## Streaming Responses

The backend uses the OpenAI ChatCompletion API (or Ollama) with streaming to provide incremental updates. Each new token from the LLM is streamed back to the frontend through SSE/WebSocket. During tool invocation, streaming pauses until the tool returns. The agent core merges tool results into the conversation.

## Data & AI Layer

## Databases

Use PostgreSQL for relational data:

- Users Table – Basic user info (can be expanded later for auth).
- Trips Table – Each trip entry contains metadata (origin, destination, dates, number of travelers, budget, interests) and references to itinerary versions.
- Itineraries Table – Stores JSON structures for each itinerary version. Each entry includes day cards, cost breakdowns, parking/ticket info and notes.
- Chat History Table – Persists the conversation to maintain context across sessions. Useful for analytics and improving the agent.

PostgreSQL can be extended with pgvector if future versions require semantic search across past itineraries or travel information.

## AI Providers

- LLM Provider – Configurable via environment variables (OPENAI_MODEL or OLLAMA_MODEL). The config.py file reads these variables and instantiates the correct model.
- LangGraph & LangChain – Used for agent orchestration and tool integration. Each tool is decorated and registered so the agent can call it at run‑time.
- Vector Database (Optional) – If supporting retrieval‑augmented generation (RAG) in later versions, integrate a vector store (e.g. pgvector or Pinecone) to store embeddings of travel data.

## External Data Sources

Domain‑specific tools call out to external APIs:

- Hotel Search API – Finds hotels within budget and preference categories.
- Attractions API – Searches for things to do based on interests and location.
- Transport API – Retrieves transportation options and costs.
- Weather API – Obtains weather data for the travel period.

These APIs should be abstracted behind functions (search_hotels, search_attractions, search_transport, get_weather) so they can be swapped out with different providers or a caching layer.

## Deployment

## Development Environment

- Monorepo – Use a single repository with apps/web (Next.js) and apps/server (Node.js/Express or Next.js API routes) and packages/agent-core for shared agent logic.
- Containerization – Use Docker Compose to run the web app, server, PostgreSQL and optionally an Ollama LLM locally.
- Environment Variables – Provide .env files for LLM configuration, API keys, database URLs and feature toggles.

## Production

- Hosting – Deploy the web app to Vercel or a similar platform; host the Node.js server on a container orchestration service (AWS ECS, Kubernetes, Railway, etc.).
- Database – Managed PostgreSQL (e.g. Supabase, Neon or AWS RDS).
- Caching – Use Redis or Varnish to cache tool results (hotel search, attractions) and reduce latency.
- Autoscaling – Configure autoscaling for the Node.js server to handle high chat throughput.

## Security & Safety Considerations

- Prompt Injection Mitigation – The agent must separate user messages from system prompts and tool responses. Validate tool inputs and outputs; never allow arbitrary tool invocation from user input.
- Confirmation Guards – Require explicit user confirmation before regenerating an itinerary, deleting items, or overwriting saved trips.
- Rate Limiting – Implement per‑user rate limiting to prevent abusive workloads.
- Sensitive Data Handling – Do not store or transmit personally identifiable information (PII) without encryption. Use HTTPS for all API communication.
- Error Handling – Catch and log errors at each layer; present user‑friendly messages when tools fail or budgets cannot be met.

## Extensibility

The architecture is intentionally modular so that you can plug in new domain skills:

- Define a Plugin Directory – Each domain (e.g. travel, restaurants, forms) lives in its own directory inside packages/plugins. It exports a setup function that registers intents, prompts, tools and workflow graphs.
- Extend the Agent Core – The core loads plugins dynamically based on configuration. It remains agnostic to domain specifics.
- Add Tools – New plugins can define additional tools (e.g. a payment processor for restaurant orders). Tools must implement a typed interface and be registered with LangChain.
- Add UI Modules – The frontend can include additional panels (e.g. order confirmation, form fields) keyed to the active plugin. Use route‑based code splitting to load only what is needed.

## Conclusion

This architecture balances rapid product delivery (chat‑first travel planning) with a scalable, reusable foundation for future domains. It uses a modular agent core, domain plugins and clear boundaries between frontend and backend. By following this plan you can ship the first version quickly and grow the platform to support restaurant ordering, website forms and other conversational workflows without rewriting the core logic.

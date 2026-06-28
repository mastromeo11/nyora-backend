# Frontend to Backend Mapping - Antigravity AI OS

This document maps the Next.js visual frontend screens to the offline FastAPI backend services. It defines which components, Zustand state stores, HTTP API routes, Server-Sent Event (SSE) streams, and WebSocket events are active for each interface view.

---

## 1. Summary Mapping Table

| Screen/Page | Path/Route | Core Store | API Routes | Realtime Event/Streams |
|---|---|---|---|---|
| **Home** | `/` | `useWorkspaceStore`, `useChatStore` | `/ui/dashboard`, `/ui/workspaces` | WS `dashboard_update` |
| **Chat** | `/chat` | `useChatStore` | `/ui/chat/stream`, `/ingest` | SSE `/ui/chat/stream` |
| **Memory** | `/memory` | `useMemoryStore` (Zustand mock state) | `/ui/memory`, `/memory/session`, `/memory/clear` | WS `memory_update` |
| **Graph** | `/graph` | `useGraphStore` | `/ui/graphs`, `/debug/knowledge-graph` | WS `graph_update` |
| **Timeline** | `/timeline` | `useMemoryStore` | `/ui/memory`, `/ui/policies` | WS `timeline_update` |
| **Simulation** | `/simulation` | `useSimulationStore` (mock state) | `/ui/world-model`, `/ui/simulations` | WS `simulation_update` |
| **Analytics**| `/analytics` | `useDashboardStore` | `/ui/analytics` | WS `dashboard_update` |
| **Workspace**| `/workspace` | `useWorkspaceStore` | `/ui/workspaces` | WS `workspace_update` |
| **Voice** | `/voice` | `useVoiceStore` | `/ui/transcribe` | SSE/WS voice updates |
| **Settings** | `/settings` | `useThemeStore` | `/ui/themes` | WS `theme_update` |
| **Developer**| `/developer` | `useDashboardStore` | `/debug/*`, `/ui/dashboard` | WS live logging & status |

---

## 2. Screen-by-Screen Reference

### A. Home Dashboard
* **Purpose:** Initial landing console presenting system health, CPU/memory performance gauges, active thread counts, and fast actions.
* **Core Components:**
  * `MetricGauge`: Circular gauges showing memory usage percentage and query latency.
  * `WorkspaceCard`: Workspace summary nodes containing configured directories.
  * `ActivityFeed`: Lists latest system notifications.
* **Backend API Routes:**
  * `GET /ui/dashboard` (Retrieves telemetry stats)
  * `GET /ui/workspaces` (Retrieves initial configurations)
* **Zustand State Stores:**
  * `useDashboardStore`: Tracks CPU, memory usage stats, and health configurations.
  * `useWorkspaceStore`: Active folders configuration details.
* **Real-time Subscriptions:**
  * WebSocket broadcast updates under event type `dashboard_update`.

---

### B. Conversational Chat
* **Purpose:** Multi-modal chat client rendering response stream tokens, citations, visual candidate VQA outputs, and reasoning steps.
* **Core Components:**
  * `ChatWindow`: Handles message arrays and streaming responses.
  * `AttachmentHandler`: Triggers file uploads via drag-and-drop.
  * `EvidenceTracer`: Displays retrieved text snippets, visual category scores, and claims verification grounding audits.
* **Backend API Routes:**
  * `GET /ui/chat/stream` (SSE text output stream)
  * `POST /ingest` (File uploading)
  * `POST /visual-qa` (Visual evaluation questions)
  * `POST /chat` (Conversational turn logging)
* **Zustand State Stores:**
  * `useChatStore`: Message arrays, active stream tokens, and citation targets.
* **Streaming & Event Feeds:**
  * Server-Sent Events (SSE) `/ui/chat/stream` streams JSON data with key `token` until sending `[DONE]`.

---

### C. Knowledge Graph Visualizer
* **Purpose:** Dynamic node-link graph mapping entities, relationships, summaries, and styles using ReactFlow.
* **Core Components:**
  * `GraphCanvas`: The main ReactFlow canvas panel.
  * `EntityInspector`: Sidebar panel showing entity importance scores, mention levels, and evidence citations.
  * `GraphControls`: Zoom, search, filter widgets.
* **Backend API Routes:**
  * `GET /ui/graphs` (Visual node and edge listings)
  * `GET /debug/knowledge-graph` (Raw DB dump containing mentions, weights)
  * `POST /knowledge/clear` (Graph wipe)
* **Zustand State Stores:**
  * `useGraphStore`: Keeps active ReactFlow nodes, edges, search keywords, and highlights.
* **Real-time Subscriptions:**
  * WebSocket client subscription under type `graph_update`.

---

### D. Memory Timeline
* **Purpose:** Visual timeline tracking conversational turns, summaries, episodes, and pattern clusters.
* **Core Components:**
  * `TimelineFeed`: Chronological card layout showing conversation turns and summaries.
  * `ClusterExplorer`: Grid displaying semantic categories.
  * `EpisodeInspector`: View showing details of an episode.
* **Backend API Routes:**
  * `GET /ui/memory` (Retrieves episodes and clusters)
  * `GET /memory/session` (Short-term memory)
  * `POST /memory/clear` (Session cleanup)
* **Zustand State Stores:**
  * `useMemoryStore` (TypeScript interface matching memory response)
* **Real-time Subscriptions:**
  * WebSocket event type `memory_update` triggers automated timeline card additions.

---

### E. Simulation Playground
* **Purpose:** Sandbox for exploring counterfactual world model states, scenario trees, and forecast risk indicators.
* **Core Components:**
  * `SimulationTree`: Graph mapping projected branch options.
  * `RiskGauge`: Displays security and failure indices.
  * `ScenarioCard`: Individual forecasted parameters.
* **Backend API Routes:**
  * `GET /ui/world-model` (Retrieves current scenarios)
  * `GET /ui/simulations` (Retrieves simulated iterations)
  * `POST /simulation/clear` (Wipes projections)
* **Zustand State Stores:**
  * `useSimulationStore` (Tracks world states and branch options)
* **Real-time Subscriptions:**
  * WebSocket broadcast updates under event type `simulation_update`.

---

### F. Developer Policy Dashboard
* **Purpose:** Leaderboard ranking planning strategies (ReAct, Plan-and-Solve) and tool execution success ratios.
* **Core Components:**
  * `LeaderboardTable`: Lists tools, latency averages, and success parameters.
  * `PolicyChart`: Line graph tracing model routing patterns.
  * `ReflectionLogs`: Displays self-reflection logs.
* **Backend API Routes:**
  * `GET /ui/policies` (Leaderboard updates)
  * `GET /ui/reflections` (Reflection logs)
* **Zustand State Stores:**
  * `useDashboardStore`
* **Real-time Subscriptions:**
  * WebSocket broadcast updates under event type `policy_update`.

---

### G. Voice Workspace
* **Purpose:** Audio interface showing mic state, waveform animations, transcriptions, and speech output controls.
* **Core Components:**
  * `MicButton`: Push-to-talk state wrapper.
  * `AudioWaveform`: Renders input audio signal levels.
  * `VoiceStateIndicator`: Displays text status logs.
* **Backend API Routes:**
  * `POST /ui/transcribe` (Audio translation service)
* **Zustand State Stores:**
  * `useVoiceStore`: Records micro states, transcript outputs, and audio file payloads.

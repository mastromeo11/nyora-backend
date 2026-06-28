# Chat & Execution Modes - Antigravity AI OS

This contract defines the execution modes supported by the RAG PRO system, outlining the target views, backend routes, and visual panel splits for each mode.

---

## 1. System Chat Modes Reference

| Mode | Purpose | Active UI Layout / Split View | Core Backend API Routes | Primary Zustand Store |
|---|---|---|---|---|
| **Standard Chat** | General conversational queries. | Centered chat feed. | `POST /chat`, `GET /ui/chat/stream` | `useChatStore` |
| **Deep Research** | In-depth retrieval spanning multiple documents. | Chat feed + Evidence previewer panel. | `POST /query-unified`, `GET /debug/evidence` | `useChatStore`, `useWorkspaceStore` |
| **Simulation** | Tracing hypothetical branches and forecasted variables. | Chat feed + Simulation tree panel. | `GET /ui/world-model`, `GET /ui/simulations` | `useSimulationStore` |
| **Developer** | Diagnosing system performance metrics and cache occupancy. | Chat feed + Telemetry logging sidebar. | `GET /ui/dashboard`, `GET /debug/*` | `useDashboardStore` |
| **Voice** | Transcribes microphone inputs and responds verbally. | Ripple visual panel. | `POST /ui/transcribe` | `useVoiceStore` |
| **Agent Mode** | Multi-agent swarm query resolution. | Chat feed + Agent reasoning trace. | `POST /agent/chat`, `GET /agent/graph` | `useChatStore`, `useDashboardStore` |
| **Memory Explorer**| Inspects conversation topics and active entities. | Chat feed + Decayed entity scoring panel. | `GET /memory/session`, `GET /memory/entities` | `useMemoryStore` |
| **Workspace Mode**| Managing folders and editing source code. | Workspace explorer + Monaco Code Editor. | `GET /ui/workspaces`, `POST /ui/workspaces` | `useWorkspaceStore` |
| **Code Mode** | Compiles and edits local scripts. | Monaco Editor + Execution terminal panel. | `GET /ui/workspaces` | `useWorkspaceStore` |
| **Timeline Mode** | Tracing conversational turn chronologies. | Scrolling timeline cards view. | `GET /ui/memory`, `GET /episodes` | `useMemoryStore` |
| **Analytics Mode**| Rendering performance graphs and token trends. | Metrics grid panel. | `GET /ui/analytics` | `useDashboardStore` |

---

## 2. Interactive Mode Selection

The client switches modes using the Command Palette or layout dropdown settings. Changing a mode dynamically configures the visual split panes and subscribes to the relevant WebSocket channels.
* **WebSocket Channel Binding:** Changing modes updates the client's WebSocket parameters (e.g. enabling `simulation_update` updates when switching to Simulation mode).
* **SSE Event Modification:** Changing modes updates query parameters (e.g. enabling deep research redirects queries to `/query-unified` and includes grounding reports in the stream).

# Component Registry - Antigravity AI OS

This register documents the core React/Next.js components of the RAG PRO frontend. It describes each component's layout purpose, sub-elements, Zustand store usage, API integration, and user interactions.

---

## 1. Visual Component Registry

### A. Chat Window
* **Purpose:** The central conversational console displaying streamed answers, reasoning timelines, citations, and prompts.
* **Sub-Components:**
  * `MessageBubble`: Renders user prompts and markdown answers.
  * `CitationsBar`: Inline array of clickable reference buttons.
  * `ReasoningTrace Accordion`: Traces tool executions and planning logs.
  * `AttachmentPanel`: Shows drag-and-drop file upload queues.
* **Zustand Store:** `useChatStore`
* **API Integration:** SSE `/ui/chat/stream`, POST `/ingest`

---

### B. Graph Visualizer
* **Purpose:** Renders interactive entity-relation networks on a 2D canvas.
* **Sub-Components:**
  * `ReactFlowCanvas`: Main node-link layout controller.
  * `GraphLegend`: Mappings for node types and colors.
  * `ControlBar`: Zoom, pan, and filter controls.
  * `InspectorPanel`: Sidebar presenting selected node attributes.
* **Zustand Store:** `useGraphStore`
* **API Integration:** GET `/ui/graphs`, GET `/debug/knowledge-graph`

---

### C. Simulation Playground
* **Purpose:** Sandbox for tracing scenario projections, evaluating alternative values, and assessing risk metrics.
* **Sub-Components:**
  * `SimulationTree`: Graph layout of projected state branches.
  * `ParameterSlider`: Interactive sliders to adjust variables.
  * `RiskGauge`: Circular visual gauge mapping failure rates.
* **Zustand Store:** `useSimulationStore`
* **API Integration:** GET `/ui/world-model`, GET `/ui/simulations`

---

### D. Memory Dashboard
* **Purpose:** View showing session topics, entity focus levels, and decay curves.
* **Sub-Components:**
  * `ActiveTopicCard`: Displays active conversation subjects.
  * `EntityDecayChart`: Tracks co-occurrence scoring.
  * `FactsSummaryList`: Scrolling bullet list of confirmed details.
* **Zustand Store:** `useMemoryStore`
* **API Integration:** GET `/memory/session`, GET `/memory/summary`

---

### E. Memory Timeline
* **Purpose:** Chronological log tracking conversational episodes, summaries, and system updates.
* **Sub-Components:**
  * `TimelineCard`: Individual event logs with status colors.
  * `ClusterFilterPanel`: Tag array to filter events by subject cluster.
* **Zustand Store:** `useMemoryStore`
* **API Integration:** GET `/ui/memory`, POST `/episodes/query`

---

### F. Voice Panel
* **Purpose:** Overlay console rendering waveform visualizations and transcription updates.
* **Sub-Components:**
  * `MicButton`: Glowing circular record button.
  * `VoiceWaveform`: Real-time canvas rendering audio frequency levels.
  * `SpeechSettings`: TTS selectors (voice profile, volume, speed).
* **Zustand Store:** `useVoiceStore`
* **API Integration:** POST `/ui/transcribe`

---

### G. Artifact Viewer
* **Purpose:** Sandbox container showing generated rich documents (tables, images, charts).
* **Sub-Components:**
  * `ModalityDispatcher`: Decides which preview component to load based on the artifact type.
  * `DownloadBar`: File export controls.
* **Zustand Store:** `useChatStore`
* **API Integration:** GET `/ui/download/*`, GET `/ui/preview/*`

---

### H. Code Editor
* **Purpose:** Split-screen editor panel hosting code files.
* **Sub-Components:**
  * `MonacoInstance`: Editor core (Monaco Editor) with syntax highlights.
  * `TabManager`: Panel tracking multiple open code documents.
* **Zustand Store:** `useWorkspaceStore`
* **API Integration:** GET `/ui/workspaces`

---

### I. Notification Center
* **Purpose:** Toast alerts and system status feeds.
* **Sub-Components:**
  * `ToastContainer`: Top-right list displaying active notifications.
  * `LogInspector`: Console listing historically generated system alerts.
* **Zustand Store:** `useNotificationStore`
* **API Integration:** GET `/ui/notifications`

---

### J. Developer Mode Panel
* **Purpose:** Sidebar console tracing hardware usage, LRU caches, and reasoning steps.
* **Sub-Components:**
  * `TelemetryGrid`: Visualizes CPU, RAM, and latency statistics.
  * `CacheInspector`: Lists cache sizes, hits, and occupancy.
  * `ToolLeaderboard`: Performance tables for planning tools.
* **Zustand Store:** `useDashboardStore`
* **API Integration:** GET `/debug/*`

---

### K. Analytics Dashboard
* **Purpose:** Visual charts tracking token usage and performance trends.
* **Sub-Components:**
  * `LatencyTrendChart`: Line chart tracing response times.
  * `CacheHitsChart`: Bar graph tracking cache hit rates.
  * `TokenUsageChart`: Traces input/output token counts.
* **Zustand Store:** `useDashboardStore`
* **API Integration:** GET `/ui/analytics`

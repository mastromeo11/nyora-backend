# Zustand Store Mapping Reference - Antigravity AI OS

This reference describes the visual client-side state management layers. It lists the core stores, their local state keys, interactive actions, persistence options, and backend integration patterns.

---

## 1. Core Visual Stores

### A. `chatStore`
* **Purpose:** Handles conversational messages, stream tokens, active chat trees, and citation selections.
* **State Properties:**
  * `messages`: Array of `Message` nodes.
  * `activeSessionId`: Current conversational memory session UUID.
  * `activeStreamingMessage`: Streaming response token content accumulator.
* **Actions:**
  * `addMessage(msg)`: Appends user or completed agent responses to the feed.
  * `updateStreamingMessage(token)`: appends SSE chunks to the tail block.
  * `clearMessages()`: Resets message lists.
* **Persistence:** SessionStorage (cleared on tab close).
* **Sync APIs:**
  * SSE `GET /ui/chat/stream?query=...`
  * POST `/chat`
  * POST `/memory/clear`
* **Cache Rules:** None.

---

### B. `themeStore`
* **Purpose:** Manages dark cyber visual elements, CSS fonts, cards glassmorphism, and color profiles.
* **State Properties:**
  * `activeTheme`: Theme configuration (`dark_cyber`, `matrix_green`, etc.).
  * `lastUpdated`: ISO timestamp tracker.
* **Actions:**
  * `setTheme(themeName)`: Applies specific layout theme.
  * `fetchActiveTheme(userId)`: Resolves active visual layout from backend.
* **Persistence:** LocalStorage (survives browser refresh).
* **Sync APIs:**
  * GET `/ui/themes?user_id=...`
  * POST `/ui/themes?user_id=...&theme=...`
* **Cache Rules:** Server-side LRU Cache invalidates user-theme entries on new POST.

---

### C. `workspaceStore`
* **Purpose:** Syncs configured folders, files, and project directory targets.
* **State Properties:**
  * `workspaces`: List of indexation directories.
  * `activeWorkspaceId`: Target workspace key.
* **Actions:**
  * `addWorkspace(name)`: Submits request to create a new folder target.
  * `loadWorkspaces(userId)`: Resolves indexing list.
* **Persistence:** LocalStorage (remembers active workspace selection).
* **Sync APIs:**
  * GET `/ui/workspaces?user_id=...`
  * POST `/ui/workspaces?user_id=...&name=...`
* **Cache Rules:** UI Workspace Cache is flushed on executing a folder indexation task.

---

### D. `graphStore`
* **Purpose:** Keeps ReactFlow nodes, edges, active node selections, and filter parameters.
* **State Properties:**
  * `nodes`: ReactFlow node elements.
  * `edges`: ReactFlow edge connections.
  * `filterOptions`: Checkbox filters for node categories.
* **Actions:**
  * `setGraphElements(nodes, edges)`: Direct set on the canvas.
  * `highlightNode(nodeId)`: Colors immediate neighbors and edges.
* **Persistence:** In-memory (reset on refresh).
* **Sync APIs:**
  * GET `/ui/graphs`
  * GET `/debug/knowledge-graph`
  * POST `/knowledge/clear`
* **Cache Rules:** Visual Graph Cache invalidates when new document ingestion runs.

---

### E. `memoryStore`
* **Purpose:** Caches recent short-term conversation sessions and pronoun coreferences.
* **State Properties:**
  * `sessionTurns`: Array of `ConversationTurn` items.
  * `summaries`: Array of `ConversationSummary` records.
  * `activeEntities`: Current entities in conversation focus.
* **Actions:**
  * `fetchSessionMemory(sessionId)`: Synchronizes with backend turn history.
  * `clearMemoryState()`: Resets parameters in store.
* **Persistence:** In-memory.
* **Sync APIs:**
  * GET `/memory/session?session_id=...`
  * GET `/memory/summary?session_id=...`
  * POST `/memory/clear?session_id=...`
* **Cache Rules:** Cache decays co-occurring entity focus levels automatically.

---

### F. `timelineStore`
* **Purpose:** Controls episode grids, clusters, and experience replay panels.
* **State Properties:**
  * `episodes`: Array of `EpisodeNode` models.
  * `clusters`: Grouped category records.
* **Actions:**
  * `fetchEpisodes()`: Retreives long-term episodes.
  * `queryEpisodicMemory(query)`: Resolves matching historical chains.
* **Persistence:** In-memory.
* **Sync APIs:**
  * GET `/episodes`
  * GET `/episodes/clusters`
  * POST `/episodes/query`
* **Cache Rules:** Caches episodic hits to avoid vector indexing calls.

---

### G. `simulationStore`
* **Purpose:** Manages scenarios, counterfactual state changes, and branch trees.
* **State Properties:**
  * `worldStates`: Array of projected states.
  * `hypotheses`: Evaluation parameters.
  * `counterfactuals`: Scenario branches.
* **Actions:**
  * `loadWorldModel()`: Fetches current forecast nodes.
  * `triggerSimulationQuery(query)`: Simulates alternate parameters.
* **Persistence:** In-memory.
* **Sync APIs:**
  * GET `/ui/world-model`
  * GET `/ui/simulations`
  * POST `/simulation/query`
* **Cache Rules:** Caches simulation hit paths.

---

### H. `policyStore`
* **Purpose:** Tracks tools latency, planner leaderboards, and reflection statements.
* **State Properties:**
  * `plannerPolicies`: Array of success ratios.
  * `toolLeaderboard`: Latency averages.
* **Actions:**
  * `loadPolicies()`: Syncs with system metrics.
* **Persistence:** In-memory.
* **Sync APIs:**
  * GET `/ui/policies`
  * GET `/ui/reflections`
* **Cache Rules:** Cleared automatically when tool executions return failure outcomes.

---

### I. `preferencesStore`
* **Purpose:** User personalization parameters.
* **State Properties:**
  * `preferences`: Mapped key-value preference values.
* **Actions:**
  * `savePreference(pref)`: Submits parameter update.
  * `loadPreferences()`: Loads profile.
* **Persistence:** LocalStorage.
* **Sync APIs:**
  * GET `/ui/preferences`
  * POST `/ui/preferences`
* **Cache Rules:** Cleared on settings reset.

---

### J. `notificationStore`
* **Purpose:** Renders toast alerts and pipeline system updates.
* **State Properties:**
  * `alerts`: List of active warnings or details.
* **Actions:**
  * `pushNotification(notif)`: Adds alert.
  * `dismissNotification(id)`: Removes alert from UI.
* **Persistence:** In-memory.
* **Sync APIs:**
  * GET `/ui/notifications`
* **Cache Rules:** Auto-dismisses alerts after 5 seconds.

---

### K. `voiceStore`
* **Purpose:** Renders PTT wave levels and transcript updates.
* **State Properties:**
  * `voiceMode`: Current voice state (`idle`, `listening`, `speaking`).
  * `transcript`: Result string.
* **Actions:**
  * `setVoiceMode(mode)`: Updates recording parameters.
* **Persistence:** In-memory.
* **Sync APIs:**
  * POST `/ui/transcribe`
* **Cache Rules:** None.

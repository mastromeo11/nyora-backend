# UI Screen Design Specifications - Antigravity AI OS

This document outlines the premium design specifications, visual structures, component configurations, and interaction behaviors for the RAG PRO AI Operating System interface. It provides Lovable AI with the visual blueprint required to assemble a premium frontend matching the aesthetic standards of Claude, Linear, Apple Vision, and Arc Browser.

---

## 1. Global Visual and Layout Foundations

* **Theme Language:** Glassmorphism overlay systems over harmonic dark cyber or light sand color spaces.
* **Layout Structure:**
  * **Sidebar:** 260px width collapsible layout container containing:
    * Workspace folders list.
    * Navigation routes (Chat, Memory, Graph, Simulations, Developer Console).
    * Connection states and fast settings toggles.
  * **Main Viewport:** Flexible split-pane canvas supporting drag-and-drop sizing configurations.

---

## 2. Screen Specifications

### A. Conversational Chat Screen
* **Layout Structure:** Centered chat feed (max-width: 800px) with inline action buttons and side-dockable retrieval logs.
* **Core Interface Elements:**
  * **Centered Chatbot Input:** A glassy input container supporting multi-line text input, file drag-and-drop drop-zones, and transcription speech triggers.
  * **Streaming Markdown Content:** Renders bold, lists, and tables inline as text tokens flow from `/ui/chat/stream`.
  * **Interactive Citations:** Numbered floating tags placed next to claims (e.g. `[1]`, `[2]`). Clicking a tag highlights the referenced file in the sidebar and opens the segment preview in a split window.
  * **Reasoning Logs Accordion:** A collapsible panel showing live ReAct thoughts:
    ```
    Thinking: Evaluating database replication parameters...
    Tool Invoked: TextRetrievalTool {"query": "replication rules"} -> Success (2 results found)
    ```
  * **Rich Media Rendering Card:** Custom preview boxes for visual graphs (rendered via SVG) and code snippets (with copy triggers).
  * **Branching Answers Toggle:** Lets users fork chat answers to explore multiple reasoning paths or run model comparisons.

---

### B. Memory Timeline Screen
* **Layout Structure:** Vertical chronological timeline feed mapping short-term and long-term memory episodes.
* **Core Interface Elements:**
  * **Chronological Timeline Stream:** Cards representing conversation turns. Each card displays user queries, summaries, timestamp markers, and recalled entities.
  * **Episodic Cards:** Memory nodes matching `/episodes`. Color-coded by importance level (`High` = Crimson border, `Medium` = Orange, `Low` = Slate).
  * **Query Pattern Clusters:** Interactive cards showing clustered search topics. Clicking a cluster group filters the timeline to related conversation items.
  * **Memory Heatmap Panel:** A calendar-style grid showing interaction frequency, recall volumes, and decay profiles over time.

---

### C. Knowledge Graph Visualizer Screen
* **Layout Structure:** Infinite-canvas panel styled with ReactFlow mapping entity nodes and co-occurrence edges.
* **Core Interface Elements:**
  * **ReactFlow Canvas:** Supports interactive zoom, fit-to-view, and canvas panning.
  * **Node Type Filtering sidebar:** Checkbox selectors to filter the graph view by node type (`entity`, `evidence`, `preference`, `task`).
  * **Search & Auto-Focus Input:** Autocomplete search box. Selecting an entity auto-centers the viewport on that node and highlights its immediate connections.
  * **Entity Detail Panel:** Interactive slider displaying importance ratings, frequency levels, and source citations.
  * **Mini Map & Legend:** A bottom-right map overlay showing overall graph density and status indicators.

---

### D. Simulation Playground Screen
* **Layout Structure:** Split screen: Left side shows scenario trees, Right side shows counterfactual branches and risk score cards.
* **Core Interface Elements:**
  * **Scenario Projection Trees:** Interactive node networks mapping projected world states (`ws_1 -> ws_2`). Edge paths are color-coded:
    * Green: Safe execution path.
    * Red/Orange: Risk path indicating forecast exceptions or latency drops.
  * **Counterfactual Parameter Panels:** Interactive sliders to modify variables (e.g., changing `PORT` or adjusting `retrieval_limit`) and run forecast simulations.
  * **Stability & Failure Risk Meters:** Large gauge meters tracking predicted system failure rates and latency indices.
  * **Scenario Summaries Table:** Lists predicted scenario results, success rates, and backup actions.

---

### E. Developer Policy Dashboard Screen
* **Layout Structure:** Grid layout displaying analytical performance charts.
* **Core Interface Elements:**
  * **Tool Efficiency Leaderboards:** Tables sorting system tools by run frequency, average latency, and execution success rates.
  * **Strategy Performance Graphs:** Line charts tracing success trends across planner types (e.g. `ReAct`, `Plan-and-Solve`).
  * **Self-Reflection Log Panel:** A scrolling console log showing meta-cognitive reflections, diagnosed exceptions, and recommended tool changes.
  * **Cache Occupancy Indicators:** Visual progress bars displaying current LRU cache usage levels for database nodes, templates, and patterns.

---

### F. Personalization Dashboard Screen
* **Layout Structure:** Flexbox container containing preference cards.
* **Core Interface Elements:**
  * **Preference Sliders:** Fine-tune response lengths, explanation depths, and target tones.
  * **Writing Style Cards:** Card list displaying extracted writing style patterns.
  * **Preference Drift Chart:** Traces user preference shifts and tone changes over time.
  * **Dissatisfaction Alert Feed:** Lists negative user interactions and abandoned tasks.

---

### G. Workspace Explorer Screen
* **Layout Structure:** Two-column split view: Left column displays file directories, Right column displays a Monaco Code Editor.
* **Core Interface Elements:**
  * **Workspace Directory Tree:** Supports file renaming, file deletion, and direct drag-and-drop uploads.
  * **Monaco Editor Instance:** Full syntax highlighting, auto-saves, and code folding for local source files.
  * **Metadata Inspection Sidebar:** Shows file metadata details, creation dates, character counts, and indexation status.
  * **Pin Panel:** Top bar displaying pinned documents and key configuration files.

---

### H. Voice UI Screen
* **Layout Structure:** Minimal overlay dashboard displaying circular wave animations.
* **Core Interface Elements:**
  * **Push-to-Talk State Toggle:** Large floating mic icon. Pulses with glowing gradient animations when listening or recording.
  * **Waveform Animation Canvas:** Real-time audio frequency wave representations.
  * **Transcription Stream Panel:** Displays the transcribed text stream as the user speaks.
  * **Text-to-Speech Controls:** Audio output configuration options (voice selection, speed, volume).

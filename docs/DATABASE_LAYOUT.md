# Database & Storage Layout - Antigravity AI OS

The Antigravity AI OS is designed for offline execution. All semantic graphs, memory profiles, agentic traces, and simulated branches are stored in local JSON documents and persistent ChromaDB indexes under the `storage/` directory.

---

## 1. Storage Directory Structure

```
storage/
├── db/                       # ChromaDB Vector Store folder containing embedding vectors
├── uploads/                  # Extracted and parsed attachment files (PDF, DOCX, etc.)
├── sessions/                 # Active multi-turn conversation session files
├── memory_cache.json         # Session-specific short-term turns and entity caches
├── episodic_memory.json      # Long-term episodes, chains, and cluster mappings
├── knowledge_graph.json      # Semantic entity-relation graph nodes
├── learning_memory.json      # User correction patterns, feedback, and decay statistics
├── world_models.json         # Projects scenario branches, stability flags, and world states
├── meta_memory.json          # Meta cognitive strategies, reflections, and tool leaderboards
├── personality_memory.json   # Tone custom preferences and extracted writing style guides
├── adaptive_ui_memory.json   # Screen parameters, visual themes, and layout histories
├── swarm_history.json        # Exchanged broker messages, health metrics, and negotiations
├── .vqa_cache.json           # Cached Visual Question Answering (VQA) LLaVA answers
└── .processed_files.json     # Tracking file hashes to prevent redundant parsing
```

---

## 2. Storage File Specifications

### A. `memory_cache.json`
* **Purpose:** Stores active conversation turns, topic parameters, and decayed entity focus arrays.
* **Node Types:** `ConversationTurn`, `EntityMemory`, `PreferenceMemory`, `ConversationSummary`.
* **Size Limits:** Mapped on a per-session scale. Short term turns limit: 10 per session. Summarization intervals default to every 5 turns.
* **Archiving Policy:** Flushed on `/memory/clear` POST request. Auto-decayed entities drop from focus tables after 3 consecutive turns.

---

### B. `episodic_memory.json`
* **Purpose:** Persistent archive for user experiences and historical conversations.
* **Node Types:** `EpisodeNode`, `ExperienceNode`, `ReplayNode`, `TemporalChainNode`, `MemoryClusterNode`.
* **Size Limits:** Max cumulative episodes: 10,000. Pruning triggers run every 100 insertions.
* **Archiving Policy:** Least important episodes (importance weight < 0.3) are decayed by 0.98. Archiving rolls decayed nodes into compressed CSV files.

---

### C. `knowledge_graph.json`
* **Purpose:** Schema repository for the semantic entity relationship network.
* **Node Types:** `EntityNode`, `RelationNode`, `TemporalNode`, `CommunityNode`.
* **Size Limits:** Maximum of 5,000 entities. Relation prune intervals run every 50 updates.
* **Archiving Policy:** Relational edges are decayed by 0.95 and entities by 0.98. Low-weight links are pruned to preserve graph traversal speed.

---

### D. `learning_memory.json`
* **Purpose:** Stores user pattern discovery adjustments, corrections, and query clusters.
* **Node Types:** `LearningNode`, `CorrectionNode`, `QueryCluster`.
* **Size Limits:** Max patterns: 1000. Max failure patterns: 1000.
* **Archiving Policy:** Discovered correction coefficients are decayed by 0.99. Inactive patterns are deleted during prune steps.

---

### E. `world_models.json`
* **Purpose:** Stores simulation scenario logs, counterfactual projections, and predicted failures.
* **Node Types:** `WorldStateNode`, `HypothesisNode`, `ScenarioNode`, `CounterfactualNode`.
* **Size Limits:** Max projected states: 100. Max scenarios: 200.
* **Archiving Policy:** Inactive scenario branches are decayed by 0.98 and world states by 0.99. Historic simulation states are compressed.

---

### F. `meta_memory.json`
* **Purpose:** Stores meta cognitive strategy logs, tool latency averages, and planner policy rankings.
* **Node Types:** `ToolLearningNode`, `PlannerPolicyNode`, `MetaReflectionNode`, `StrategyNode`.
* **Size Limits:** Max tool latency history items: 1000. Max reflections count: 100.
* **Archiving Policy:** Policies are decayed by 0.99 and tools by 0.98. Less effective planner strategies are archived in policy logs.

---

### G. `personality_memory.json`
* **Purpose:** Stores personalized tone configurations and style guidelines.
* **Node Types:** `HumanPreferenceNode`, `NegativePreferenceNode`, `UserStyleNode`, `AdaptivePersonalityNode`.
* **Size Limits:** Max style variations: 1000.
* **Archiving Policy:** Custom preferences are decayed by 0.995. Low-use preferences are archived to JSON files.

---

### H. `adaptive_ui_memory.json`
* **Purpose:** Tracks UI interactions, layout views (split-screen toggles), and active CSS theme profiles.
* **Node Types:** `VisualThemeNode`, `UILayoutNode`, `AdaptiveInterfaceNode`.
* **Size Limits:** Stores up to 50 historical visual configuration updates per user.
* **Archiving Policy:** Flushed on layout reset.

---

### I. `swarm_history.json`
* **Purpose:** Stores broker messages, shared workspace memories, and negotiation logs.
* **Node Types:** Swarm agent message objects.
* **Size Limits:** Maximum of 1,000 active message logs.
* **Archiving Policy:** Cleared on swarm reset.

---

### J. `db/` (ChromaDB Vector Store)
* **Purpose:** Stores embedding vectors for textual paragraphs and CLIP representations for images.
* **Node Types:** Dense float array indices mapping to text chunks or file pointers.
* **Size Limits:** Scaled according to local disk capacity.
* **Archiving Policy:** Synchronized with the uploads file system directory. If a file is deleted from uploads, its corresponding vectors are purged from the collections.

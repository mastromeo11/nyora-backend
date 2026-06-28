# API Reference - Antigravity AI OS Backend Contracts (Milestones 1–18)

This document provides a comprehensive API reference for the offline-first backend. It serves as the single source of truth for Lovable AI to construct the frontend screens, data stores, components, and communication layers without requiring access to backend source code.

## Global Configurations

* **Base URL:** `http://localhost:8000`
* **WebSocket Base URL:** `ws://localhost:8000`
* **Protocol:** HTTP/1.1 (REST endpoints), SSE (text/event-stream), RFC 6455 (WebSockets)
* **Default Content-Type:** `application/json` (except file uploads which use `multipart/form-data`)
* **Authentication:** None (Local Offline execution environment)

---

## 1. Chat & Conversational RAG Engine

### POST /chat
* **Purpose:** Multi-turn conversational chat aware of short-term, long-term, and entity memories.
* **Headers:** `Content-Type: application/json`
* **Request Body:**
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | Yes | - | The user message or question. |
| `session_id` | string | Yes | - | Unique UUID for the conversational session. |

* **Response Schema (200 OK):**
| Field | Type | Description |
|---|---|---|
| `answer` | string | Generated LLM answer. |
| `confidence` | string | System confidence level (`High`, `Medium`, `Low`). |
| `confidence_score` | float | Decimal confidence score between `0.0` and `1.0`. |
| `sources` | array of objects | Document or visual citations used in the prompt. |
| `evidence` | array of objects | Serialized `EvidenceNode` list containing modalities, scores, and reasons. |
| `why_this_answer` | array of strings | Semantic explanations of why these chunks were fused. |
| `supporting_modalities`| array of strings | Set of media types that contributed (`text`, `vqa`, `image`, etc.). |

* **Example Request:**
```json
{
  "query": "What are the core parameters of our new database design and did you locate any diagrams of it?",
  "session_id": "sess-99b24-77ac-4a81-9d10"
}
```
* **Example Response:**
```json
{
  "answer": "The database design is centered around strict normalization constraints to optimize retrieval latency under 120ms. I found a schema diagram showing the tables.",
  "confidence": "High",
  "confidence_score": 0.94,
  "sources": [
    {
      "source": "db_design_doc.pdf",
      "page": 4,
      "modality": "text"
    },
    {
      "source": "schema_diagram.png",
      "visual_category": "diagram",
      "modality": "image"
    }
  ],
  "evidence": [
    {
      "evidence_id": "ev_db_001",
      "source": "db_design_doc.pdf",
      "source_type": "pdf",
      "modality": "text",
      "content": "Strict normalization rules apply to all primary and secondary clusters to prevent write lock propagation.",
      "retrieval_score": 0.89,
      "confidence": "High",
      "citation_reason": "Matches semantic text query for database constraints.",
      "metadata": {
        "page": 4
      },
      "timestamp_start": null,
      "timestamp_end": null,
      "visual_category": null,
      "file_path": "/storage/uploads/db_design_doc.pdf",
      "provenance": {
        "retriever": "text_retriever",
        "retrieval_timestamp": "2026-06-24T10:23:00Z",
        "ranking_stage": "stage_1",
        "fusion_stage": "multimodal_fusion"
      }
    },
    {
      "evidence_id": "ev_img_042",
      "source": "schema_diagram.png",
      "source_type": "png",
      "modality": "image",
      "content": "Database ER diagram showing entity relationships and foreign keys.",
      "retrieval_score": 0.78,
      "confidence": "Medium",
      "citation_reason": "Matched visual representation of schema configuration via CLIP query.",
      "metadata": {
        "dimensions": "1024x768"
      },
      "timestamp_start": null,
      "timestamp_end": null,
      "visual_category": "diagram",
      "file_path": "/storage/uploads/schema_diagram.png",
      "provenance": {
        "retriever": "image_retriever",
        "retrieval_timestamp": "2026-06-24T10:23:01Z",
        "ranking_stage": "stage_1",
        "fusion_stage": "multimodal_fusion"
      }
    }
  ],
  "why_this_answer": [
    "Fused high-scoring database design document text with the schema diagram matching CLIP text queries."
  ],
  "supporting_modalities": [
    "text",
    "image"
  ]
}
```
* **Example Error (500 Internal Error):**
```json
{
  "detail": "LLM inference failure: Connection timed out to local engine."
}
```

---

### GET /ui/chat/stream
* **Purpose:** Real-time stream (Server-Sent Events) of query responses with word-by-word token updates and visual references.
* **Query Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | Yes | - | User question to stream answers for. |

* **Headers:** `Accept: text/event-stream`
* **Response Stream Format:**
```
data: {"token": "GeneratedWord "}
data: {"token": "NextWord "}
...
data: [DONE]
```
* **Example Stream Event Output:**
```
data: {"token": "The "}

data: {"token": "system "}

data: {"token": "is "}

data: {"token": "fully "}

data: {"token": "operational. "}

data: [DONE]
```

---

### POST /query-route
* **Purpose:** Unified router endpoint to dynamically dispatch queries to standard text RAG, visual QA, or multimodal retrieval.
* **Request Body:** Same as `QueryRequest` (contains `query` and optional `limit`).
* **Response Schema (200 OK):**
```json
{
  "routed_path": "unified_evidence_rag",
  "confidence": "High",
  "routing_reason": "Query requests multimodal evidence extraction spanning multiple diagrams and texts.",
  "results": {
    "answer": "Factual answer from chosen path.",
    "evidence": []
  }
}
```

---

### POST /query-unified
* **Purpose:** Execute direct Production-Grade Multimodal Unified Evidence RAG query.
* **Request Body:** Same as `QueryRequest`.
* **Response Schema (200 OK):** Same as `EvidenceResponse` (lists answer, evidence array, and sources).

---

### POST /query
* **Purpose:** Legacy text RAG route query returning answer text and retrieved text chunks.
* **Request Body:**
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | Yes | - | User question. |
| `limit` | integer | No | 5 | Limit of text chunks to retrieve. |

* **Response Schema (200 OK):**
```json
{
  "query": "Is there a config variable?",
  "answer": "Yes, PORT defaults to 8000.",
  "retrieved_chunks": [
    {
      "text": "PORT = int(os.getenv('PORT', 8000))",
      "source": "config.py",
      "score": 0.99
    }
  ]
}
```

---

## 2. Documents & File Ingestion

### POST /ingest
* **Purpose:** Upload physical document files (PDF, DOCX, etc.) to trigger parser pipeline extraction.
* **Headers:** `Content-Type: multipart/form-data`
* **Request Body (Multipart Form):**
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | Binary File | Yes | File payload containing PDF, DOCX, or text data. |

* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "filename": "quarterly_financials.pdf",
  "pages_processed": 14,
  "chunks_created": 62,
  "vector_db_ingestion": "completed"
}
```
* **Example Error (400 Bad Request):**
```json
{
  "detail": "Invalid file format. Only PDF and DOCX pipelines are supported."
}
```

---

### POST /search-images
* **Purpose:** Execute CLIP-based visual semantic search over database images.
* **Request Body:**
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | Yes | - | Text query to find similar images. |
| `limit` | integer | No | 5 | Max number of matching images to return. |

* **Response Schema (200 OK):**
```json
[
  {
    "file_path": "/storage/uploads/screenshot_dashboard.png",
    "source": "screenshot_dashboard.png",
    "score": 0.32,
    "visual_category": "ui_screenshot",
    "caption": "A dark cyber dashboard showing graphs and performance metrics."
  }
]
```

---

### POST /search-multimodal
* **Purpose:** Execute dual-pathway text and visual retrieval returning fused context lists.
* **Request Body:**
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | Yes | - | Text query. |
| `text_limit` | integer | No | 3 | Limit for text chunks. |
| `image_limit` | integer | No | 3 | Limit for image chunks. |

* **Response Schema (200 OK):**
```json
{
  "query_intent": "multimodal_search",
  "text_results": [
    {
      "text": "Text snippet content...",
      "source": "design.txt",
      "score": 0.72
    }
  ],
  "image_results": [
    {
      "file_path": "/storage/uploads/img_1.jpg",
      "source": "img_1.jpg",
      "score": 0.29,
      "visual_category": "nature"
    }
  ],
  "fused_results": [
    {
      "id": "fuse_0",
      "type": "text",
      "content": "Text snippet content...",
      "score": 0.72
    },
    {
      "id": "fuse_1",
      "type": "image",
      "content": "Image file at /storage/uploads/img_1.jpg",
      "score": 0.58
    }
  ]
}
```

---

### POST /visual-qa
* **Purpose:** Submit a visual question answering (VQA) task on the best-fit candidate image.
* **Request Body:**
| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | Yes | The question referring to an image (e.g. \"What is the red value in the chart?\"). |

* **Response Schema (200 OK):**
```json
{
  "answer": "The red bar in the chart represents 450 units of monthly active users.",
  "source_image": "chart_distribution.png",
  "file_path": "/storage/uploads/chart_distribution.png",
  "visual_category": "chart",
  "caption": "Monthly user statistics chart",
  "clip_score": 0.35,
  "confidence": "High",
  "model_used": "llava:7b",
  "citation_reason": "Candidate image selected due to high CLIP correlation score for chart distribution question."
}
```

---

## 3. Conversational Memory

### GET /ui/memory
* **Purpose:** Get compiled UI memory items (episodes, chains, clusters) for the timeline screen.
* **Response Schema (200 OK):**
```json
{
  "episodes": [
    {
      "id": "ep_01a",
      "query": "Explain database replication config",
      "summary": "Detailed query on DB replicas, resulting in configuration guidelines."
    }
  ],
  "chains": [
    {
      "id": "ch_01a",
      "episodes": ["ep_01a"]
    }
  ],
  "clusters": [
    {
      "id": "cl_database",
      "center": "database operations",
      "count": 5
    }
  ]
}
```

---

### GET /memory/session
* **Purpose:** Returns the current list of short-term conversational turns recorded in the active session cache.
* **Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Target session identifier. |

* **Response Schema (200 OK):**
```json
[
  {
    "turn_id": "turn_001",
    "session_id": "session_abc",
    "user_query": "Hello",
    "assistant_answer": "Hello! How can I assist you today?",
    "timestamp": "2026-06-24T10:20:00Z",
    "retrieved_sources": [],
    "entities": [],
    "intent_profile": "greeting",
    "confidence": "High"
  }
]
```

---

### GET /memory/entities
* **Purpose:** Returns all accumulated entity attributes and facts compiled during active user chat.
* **Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Active session ID. |

* **Response Schema (200 OK):**
```json
{
  "ChromaDB": {
    "entity_name": "ChromaDB",
    "mentions": 3,
    "last_seen": "2026-06-24T10:22:15Z",
    "sources": ["config.py", "database.py"],
    "supporting_modalities": ["text"],
    "confidence": 0.95
  }
}
```

---

### GET /memory/summary
* **Purpose:** Get summary blocks generated automatically during multi-turn chats.
* **Query Parameters:** Same as `/memory/entities`.
* **Response Schema (200 OK):**
```json
[
  {
    "session_id": "session_abc",
    "summary": "User verified configuration variables for port and local Chroma database parameters.",
    "entity_focus": ["ChromaDB", "PORT"],
    "important_facts": ["Port defaults to 8000", "ChromaDB is stored under storage/db"],
    "timestamp": "2026-06-24T10:22:45Z"
  }
]
```

---

### GET /memory/graph
* **Purpose:** Retrieve structural nodes linking conversation turns, active entities, preferences, and sources.
* **Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | Yes | Current user query filter. |
| `session_id` | string | Yes | Conversational session identifier. |

* **Response Schema (200 OK):**
```json
{
  "nodes": [
    {
      "id": "node_turn_0",
      "label": "Turn 1: Database configurations",
      "type": "turn_node",
      "importance": 0.70
    },
    {
      "id": "node_entity_chroma",
      "label": "Entity: ChromaDB",
      "type": "entity_node",
      "importance": 0.85
    }
  ],
  "edges": [
    {
      "id": "edge_0",
      "source": "node_turn_0",
      "target": "node_entity_chroma",
      "weight": 0.90
    }
  ]
}
```

---

### GET /memory/cache
* **Purpose:** Get raw cache values containing topic details and session preferences.
* **Query Parameters:** Same as `/memory/entities`.
* **Response Schema (200 OK):** Raw JSON dump of the session cache.

---

### GET /memory/active-entity
* **Purpose:** Get entity context markers displaying current focus decays.
* **Query Parameters:** Same as `/memory/entities`.
* **Response Schema (200 OK):**
```json
{
  "current_entity_focus": "ChromaDB",
  "previous_entity_focus": "Ollama"
}
```

---

### POST /memory/clear
* **Purpose:** Erases memory logs and caches for the given session ID.
* **Query Parameters:** Same as `/memory/entities`.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared memory for session sess-99b24-77ac-4a81-9d10"
}
```

---

## 4. Episodic Memory (Long-term)

### GET /episodes
* **Purpose:** Retrieve all stored long-term memory episodes.
* **Response Schema (200 OK):** Array of serialized `EpisodeNode` nodes.
```json
[
  {
    "episode_id": "ep_101",
    "session_id": "session_abc",
    "summary": "User set local application port to 9090",
    "importance": 0.78,
    "timestamp": "2026-06-24T10:00:00Z",
    "confidence": 0.90,
    "metadata": {}
  }
]
```

---

### GET /episodes/replays
* **Purpose:** Get episodic interaction replays used for self-improvement and user pattern reinforcement.
* **Response Schema (200 OK):** List of replay models containing query summaries and outcomes.

---

### GET /episodes/chains
* **Purpose:** Get chronological chains of episodes representing user flows.
* **Response Schema (200 OK):** List of episodic chains.

---

### GET /episodes/clusters
* **Purpose:** Get grouped nodes clustering related episodic memories.
* **Response Schema (200 OK):** List of memory clusters.

---

### GET /episodes/cache
* **Purpose:** Retrieve cache efficiency metrics for episodic storage.
* **Response Schema (200 OK):**
```json
{
  "hit_rate": 0.81,
  "occupancy": 15,
  "cache_size": 100
}
```

---

### POST /episodes/query
* **Purpose:** Search over long-term episodic nodes, chains, and cluster structures.
* **Request Body:** `QueryRequest` (contains `query` and optional `limit`).
* **Response Schema (200 OK):**
```json
{
  "episodes": [],
  "replays": [],
  "chains": [],
  "clusters": [],
  "summaries": []
}
```

---

### POST /episodes/clear
* **Purpose:** Wipe out long-term episodic databases and caches.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared all episodic memory state."
}
```

---

## 5. Knowledge Graph

### GET /ui/graphs
* **Purpose:** Retrieve visualized react-flow node and edge representations representing personalization elements.
* **Response Schema (200 OK):**
```json
{
  "nodes": [
    {
      "id": "n_pref_1",
      "type": "preference",
      "data": {
        "label": "Strict Formatting"
      }
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "n_pref_1",
      "target": "n_style_1",
      "animated": true
    }
  ]
}
```

---

### GET /debug/knowledge-graph
* **Purpose:** Get direct DB mapping details of the entire semantic knowledge graph.
* **Response Schema (200 OK):**
```json
{
  "entities": [
    {
      "entity_id": "ent_chroma",
      "name": "ChromaDB",
      "canonical_name": "ChromaDB",
      "entity_type": "database",
      "aliases": ["Chroma", "VectorDB"],
      "mentions": 5,
      "confidence": 1.0,
      "sources": ["config.py"],
      "supporting_modalities": ["text"],
      "created_at": "2026-06-24T10:20:00Z",
      "updated_at": "2026-06-24T10:22:00Z",
      "last_seen": "2026-06-24T10:22:00Z",
      "importance_score": 0.85,
      "centrality_score": 0.45,
      "community_id": "comm_data"
    }
  ],
  "relations": [
    {
      "relation_id": "rel_001",
      "source_entity": "ent_chroma",
      "target_entity": "ent_port",
      "relation_type": "configured_with",
      "confidence": 0.95,
      "weight": 0.80,
      "created_at": "2026-06-24T10:20:00Z",
      "updated_at": "2026-06-24T10:20:00Z",
      "evidence_ids": ["ev_db_001"],
      "source_modalities": ["text"],
      "created_by": "relation_extractor",
      "last_confirmed": "2026-06-24T10:20:00Z",
      "confirmation_count": 1
    }
  ]
}
```

---

### POST /knowledge/clear
* **Purpose:** Erases the semantic knowledge graph.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared the semantic knowledge graph store."
}
```

---

### GET /debug/graph-cache
* **Purpose:** Get LRU statistics for graph retrievals.
* **Response Schema (200 OK):**
```json
{
  "hits": 45,
  "misses": 12,
  "hit_rate": 0.789,
  "occupancy": 8
}
```

---

## 6. Multi-Agent Swarms

### GET /swarm/agents
* **Purpose:** Get information on running agent configurations (Planning, Critic, Grounding, Learning, etc.).
* **Response Schema (200 OK):**
```json
{
  "planner_agent": {
    "agent_id": "planner_agent",
    "role": "Planner & Task Decomposer",
    "status": "idle",
    "success_rate": 0.94
  }
}
```

---

### GET /swarm/messages
* **Purpose:** Get message history exchanged between swarm agent processes.
* **Response Schema (200 OK):** Array of objects detailing sender, receiver, message content, and timestamps.

---

### GET /swarm/shared-memory
* **Purpose:** Fetch the key-value dictionary acting as shared workspace among agents.
* **Response Schema (200 OK):** JSON dictionary representing active data points.

---

### GET /swarm/negotiations
* **Purpose:** Return consensus nodes and shared memory arguments representing multi-agent negotiations.
* **Response Schema (200 OK):**
```json
{
  "consensus_nodes": [],
  "shared_memory_negotiations": []
}
```

---

### GET /swarm/graph
* **Purpose:** Visual agent communication flow graph mapping tasks and tool delegations.
* **Response Schema (200 OK):** ReactFlow structured network nodes representing active swarm workflows.

---

### POST /swarm/clear
* **Purpose:** Hard reset on message brokers, agent caches, loads, and health states.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared all multi-agent swarm state and history."
}
```

---

## 7. World Models & Simulations

### GET /ui/world-model
* **Purpose:** Retrieve scenario forecasts, active variables, and counterfactual models.
* **Response Schema (200 OK):**
```json
{
  "world_states": [
    {
      "state_id": "ws_1",
      "summary": "Initial Setup",
      "status": "Success"
    }
  ],
  "hypotheses": [
    {
      "id": "hyp_1",
      "description": "What if ChromaDB is empty",
      "confidence": 0.85
    }
  ],
  "scenarios": [
    {
      "id": "scen_1",
      "summary": "Cache hits drop significantly",
      "success_probability": 0.95
    }
  ],
  "counterfactuals": [
    {
      "id": "cf_1",
      "modified_variable": "retrieval_limit",
      "outcome": "lower accuracy"
    }
  ]
}
```

---

### GET /world-states
* **Purpose:** Retrieve chronological list of predicted world state milestones.
* **Response Schema (200 OK):** Array of `WorldStateNode` items.

---

### GET /hypotheses
* **Purpose:** Retrieve lists of speculative hypotheses evaluated by the simulation engine.
* **Response Schema (200 OK):** Array of `HypothesisNode` objects.

---

### GET /scenarios
* **Purpose:** Get evaluated branches of scenario nodes.
* **Response Schema (200 OK):** Array of `ScenarioNode` items.

---

### GET /counterfactuals
* **Purpose:** Retrieve counterfactual reasoning paths.
* **Response Schema (200 OK):** Array of `CounterfactualNode` items.

---

### GET /simulations
* **Purpose:** Get recorded simulation runs.
* **Response Schema (200 OK):** Array of objects detailing simulation ID, rating, path, and outcomes.

---

### GET /simulation/cache
* **Purpose:** Get world model caching hit rate.
* **Response Schema (200 OK):**
```json
{
  "hit_rate": 0.85
}
```

---

### POST /simulation/query
* **Purpose:** Submit custom query filters over scenarios, state trees, and forecasts.
* **Request Body:** `QueryRequest`.
* **Response Schema (200 OK):** List of scenario structures containing branch outcomes.

---

### POST /simulation/clear
* **Purpose:** Erase simulated state lists, counterfactual branches, and forecast files.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared all simulation/world model state."
}
```

---

### GET /simulation-archives
* **Purpose:** Retrieve compressed archives of historically executed simulations.
* **Response Schema (200 OK):** List of `SimulationArchiveNode` records.

---

## 8. Meta Cognition & Tool Learning

### GET /policies
* **Purpose:** Fetch running strategy structures used to assign tools to questions.
* **Response Schema (200 OK):**
```json
{
  "planner_policies": [
    {
      "policy_id": "pol_react",
      "planner_type": "ReAct",
      "success_rate": 0.92
    }
  ],
  "tool_leaderboard": [
    {
      "tool": "TextRetrievalTool",
      "success_rate": 0.98,
      "latency_ms": 45.0
    }
  ]
}
```

---

### GET /tools
* **Purpose:** List cataloged tools, usage counts, success frequencies, and performance metrics.
* **Response Schema (200 OK):** Array of `ToolLearningNode` records.

---

### GET /reflections
* **Purpose:** Retrieve meta cognitive reflection statements generated on run errors.
* **Response Schema (200 OK):** Array of reflections showing issues detected and recommendations.

---

### GET /strategies
* **Purpose:** List generated planning policies and tool sequences.
* **Response Schema (200 OK):** Array of `StrategyNode` items.

---

### GET /replays
* **Purpose:** Fetch policy similarity replays.
* **Response Schema (200 OK):** Array of `PolicyReplayNode` logs.

---

### GET /tool-failures
* **Purpose:** List specific tool execution failures.
* **Response Schema (200 OK):** Array of `ToolFailureNode` objects.

---

### GET /optimization-failures
* **Purpose:** List parameters that caused planner strategy failures.
* **Response Schema (200 OK):** Array of `OptimizationFailureNode` objects.

---

### GET /policy-failures
* **Purpose:** List planning policies that failed performance indicators.
* **Response Schema (200 OK):** Array of `PolicyFailureNode` objects.

---

### GET /policy-archives
* **Purpose:** Get historically archived policies.
* **Response Schema (200 OK):** Array of `PolicyArchiveNode` objects.

---

### GET /meta-archives
* **Purpose:** Retrieve archived reflections and strategies.
* **Response Schema (200 OK):** Array of `MetaArchiveNode` objects.

---

### GET /meta/cache
* **Purpose:** Get active occupancy size for tools and policies.
* **Response Schema (200 OK):**
```json
{
  "tools_cache_size": 12,
  "policies_cache_size": 4
}
```

---

### POST /meta/query
* **Purpose:** Retrieve context from strategies and reflections.
* **Request Body:** `QueryRequest`.
* **Response Schema (200 OK):**
```json
{
  "tools": [],
  "policies": [],
  "strategies": [],
  "reflections": [],
  "replays": []
}
```

---

### POST /meta/clear
* **Purpose:** Clear the entire meta cognitive policy store.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared all meta-cognition store."
}
```

---

## 9. Personalization & Personality

### GET /ui/preferences
* **Purpose:** Get preference attributes to load in the settings interface.
* **Response Schema (200 OK):**
```json
[
  {
    "preference_id": "pref_theme_dark",
    "user_entities": ["default_user"],
    "preferred_domains": ["engineering"],
    "explanation_depth": "detailed",
    "tone_preference": "professional",
    "response_length": 350,
    "confidence": 0.85,
    "frequency": 12,
    "success_rate": 0.98,
    "timestamp": "2026-06-24T10:00:00Z"
  }
]
```

---

### POST /ui/preferences
* **Purpose:** Update settings preferences.
* **Request Body:** Raw preference key-value values.
* **Response Schema (200 OK):** Status success confirmation.

---

### GET /personality/preferences
* **Purpose:** Retrieve user-specific preferred styles and tones.
* **Response Schema (200 OK):** List of preference models.

---

### POST /personality/preference
* **Purpose:** Save a preference configuration.
* **Request Body:** Serialized `HumanPreferenceNode` schema fields.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "preference": {}
}
```

---

### GET /personality/failures
* **Purpose:** Get a report of interactions where user was dissatisfied.
* **Response Schema (200 OK):** Array of `PersonalityFailureNode` instances.

---

### POST /personality/clear
* **Purpose:** Reset preference logs and active profile configurations.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared personality store."
}
```

---

## 10. UI Operating System Layer

### GET /ui/dashboard
* **Purpose:** Retrieve system metrics (CPU, memory occupancy, and token counts).
* **Response Schema (200 OK):**
```json
{
  "schema_version": 1,
  "cpu_usage_pct": 12.5,
  "ram_usage_mb": 425.0,
  "latency_ms": 115.0,
  "cache_hit_rate": 0.75,
  "episode_count": 42,
  "policies_count": 8,
  "world_states_count": 14,
  "active_threads": 4,
  "requests_total": 1250,
  "timestamp": "2026-06-24T10:23:00Z"
}
```

---

### GET /ui/themes
* **Purpose:** Retrieve theme preferences mapped to UI style profiles.
* **Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | No | Target user identifier. Defaults to `default_user`. |

* **Response Schema (200 OK):**
```json
{
  "theme": "dark_cyber",
  "last_updated": "2026-06-24T10:00:00Z"
}
```

---

### POST /ui/themes
* **Purpose:** Modify visual interface themes.
* **Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | Yes | Target user profile. |
| `theme` | string | Yes | Target theme (`dark_cyber`, `matrix_green`, etc.). |

* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "theme": "matrix_green"
}
```

---

### GET /ui/workspaces
* **Purpose:** Retrieve directory targets configured for indexation.
* **Query Parameters:** Same as `/ui/themes`.
* **Response Schema (200 OK):**
```json
[
  {
    "workspace_id": "ws_default",
    "name": "Default Project",
    "folders": ["Logs", "Code"]
  }
]
```

---

### POST /ui/workspaces
* **Purpose:** Create or configure new indexing folders.
* **Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | Yes | Target user profile. |
| `name` | string | Yes | Workspace folder title name. |

* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "workspace": {
    "workspace_id": "ws_cf8a22bc",
    "name": "Project Apollo",
    "folders": []
  }
}
```

---

### GET /ui/notifications
* **Purpose:** Fetch system status updates and model outputs alerts.
* **Response Schema (200 OK):**
```json
[
  {
    "notification_id": "notif_1",
    "type": "info",
    "message": "Visual Operating System online."
  }
]
```

---

### GET /ui/analytics
* **Purpose:** Get query history patterns, hits, and latencies.
* **Response Schema (200 OK):**
```json
{
  "latency_trends": [120, 115, 110, 125, 115],
  "cache_hits": [0.65, 0.70, 0.75, 0.70, 0.75],
  "token_usage": [1200, 1500, 1400, 1600, 1500]
}
```

---

## 11. Voice UI

### POST /ui/transcribe
* **Purpose:** Transcribe local mic input audio stream and return text response.
* **Headers:** `Content-Type: multipart/form-data`
* **Request Body (Multipart Form):**
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | Binary File | Yes | Audio recording payload (WAV, MP3, M4A). |

* **Response Schema (200 OK):**
```json
{
  "text": "Identify the latest system replication error logs"
}
```

---

## 12. Diagnostics & Developer Mode

### GET /health
* **Purpose:** Return connection state for vector DB and local model agents.
* **Response Schema (200 OK):**
```json
{
  "status": "ok",
  "vector_db": "connected",
  "llm": "connected"
}
```

---

### GET /debug/retrieval
* **Purpose:** Advanced query diagnostics showing raw CLIP and text weights prior to fusion.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):** Details of multimodal query intent, text scores, and visual categories.

---

### GET /debug/vqa
* **Purpose:** Diagnostics for VQA candidate scoring.
* **Query Parameters:** `question` (string, required).
* **Response Schema (200 OK):** Full Candidate listing score matching selected source images.

---

### GET /debug/evidence
* **Purpose:** Unified RAG scoring dashboard returning edges, compressing factors, and source rankings.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):** Graph representations matching why this answer was given.

---

### GET /debug/graph
* **Purpose:** Semantic graph view containing nodes and edge layouts.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):** JSON containing ReactFlow nodes and edges parameters.

---

### GET /debug/context
* **Purpose:** Detailed list of retrieved text chunks compressed via query context compilers.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):**
```json
{
  "query": "Who configured PORT?",
  "context": "[Source: config.py]\nPORT = int(os.getenv('PORT', 8000))"
}
```

---

### GET /debug/grounding
* **Purpose:** Claim validator factual consensus details.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):**
```json
{
  "query": "port variable",
  "answer": "The application is running on port 8000.",
  "grounding_report": {
    "num_claims": 1,
    "claims_verified": 1,
    "factual_accuracy": 1.0,
    "issues": []
  }
}
```

---

### GET /debug/entities
* **Purpose:** Entity consensus resolution facts.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):** Normalized properties for duplicate entity logs.

---

### GET /debug/relevance
* **Purpose:** Pruned and irrelevant node diagnostic lists.
* **Query Parameters:** `query` (string, required).
* **Response Schema (200 OK):** Logs of nodes pruned because of low semantic correlation.

---

### GET /debug/memory
* **Purpose:** Flattened conversation logs containing turns, entities, and summaries.
* **Query Parameters:** `session_id` (string, required).
* **Response Schema (200 OK):** List of memory nodes.

---

### GET /debug/followup
* **Purpose:** pronoun resolution diagnostic mappings.
* **Response Schema (200 OK):** Debug logs for coreference tracking.

---

### GET /debug/session
* **Purpose:** Fetch the latest 10 conversation steps inside active session cache.
* **Query Parameters:** `session_id` (string, required).
* **Response Schema (200 OK):** List of conversation turns.

---

### GET /debug/entity-focus
* **Purpose:** Entity decay values.
* **Query Parameters:** `session_id` (string, required).
* **Response Schema (200 OK):** Topic scoring lists.

---

### GET /debug/memory-explanation
* **Purpose:** Structured memory usage reasons.
* **Response Schema (200 OK):** Textual debug updates.

---

### GET /debug/metrics
* **Purpose:** Memory score statistics.
* **Response Schema (200 OK):** Detailed metrics mapping successes and hits.

---

### POST /agent/chat
* **Purpose:** Single-agent ReAct query pipeline execute.
* **Request Body:** `AgentChatRequest` (contains `query` and `session_id`).
* **Response Schema (200 OK):** Standard agent RAG output mapping goals and plans.

---

### GET /agent/goals
* **Purpose:** Fetch running agent goals list.
* **Response Schema (200 OK):** List of target goal schemas.

---

### GET /agent/plans
* **Purpose:** Fetch active planning steps.
* **Response Schema (200 OK):** List of plan nodes.

---

### GET /agent/tasks
* **Purpose:** Retrieve active plan sub-tasks.
* **Response Schema (200 OK):** List of task nodes.

---

### GET /agent/observations
* **Purpose:** Retrieve observations recorded by agent tools.
* **Response Schema (200 OK):** List of observation nodes.

---

### GET /agent/reflections
* **Purpose:** Retrieve agent self-reflection logs.
* **Response Schema (200 OK):** List of reflection nodes.

---

### GET /agent/traces
* **Purpose:** Retrieve overall execution trace schemas.
* **Response Schema (200 OK):** Complete trace node dictionary.

---

### GET /agent/graph
* **Purpose:** Get semantic graph displaying planning chains.
* **Query Parameters:** `session_id` (string, required).
* **Response Schema (200 OK):** ReactFlow structured network nodes.

---

### GET /debug/agent
* **Purpose:** Summary counts of plan states.
* **Response Schema (200 OK):**
```json
{
  "goal": {},
  "plan": {},
  "tasks_count": 4,
  "executed_tools_count": 2,
  "observations_count": 2,
  "reflections_count": 0
}
```

---

### GET /debug/react
* **Purpose:** ReAct observation debug logs.
* **Response Schema (200 OK):** List of observed states.

---

### GET /debug/tools
* **Purpose:** Execution metrics for tools.
* **Response Schema (200 OK):** List of tools runs.

---

### POST /agent/reset
* **Purpose:** Wipe out reasoning execution state in agent caches.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared agent reasoning trace states."
}
```

---

### GET /debug/graph-explanation
* **Purpose:** Knowledge Graph explanation logs.
* **Response Schema (200 OK):** Explanation update.

---

### GET /learning/patterns
* **Purpose:** Retrieve user behavior patterns discovered during active learning.
* **Response Schema (200 OK):** List of learning pattern nodes.

---

### GET /learning/corrections
* **Purpose:** Get self-learning factual adjustments.
* **Response Schema (200 OK):** List of corrections models.

---

### GET /learning/clusters
* **Purpose:** Retrieve query pattern clusters.
* **Response Schema (200 OK):** List of clustered topics.

---

### GET /learning/failures
* **Purpose:** Get failure pattern models compiled to prevent repeated errors.
* **Response Schema (200 OK):** List of failure pattern models.

---

### GET /learning/cache
* **Purpose:** Get self-learning cache hit scores.
* **Response Schema (200 OK):** Cache capacity usage numbers.

---

### POST /learning/query
* **Purpose:** Submit keyword filter over discovered patterns.
* **Request Body:** `LearningQueryRequest` (contains `query`).
* **Response Schema (200 OK):** Context logs matching query.

---

### POST /learning/clear
* **Purpose:** Reset self-learning databases.
* **Response Schema (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared the self-learning memory store."
}
```

---

### GET /debug/patterns
* **Purpose:** Directly load running patterns (alias route for diagnostics).
* **Response Schema (200 OK):** List of pattern objects.

---

### GET /debug/corrections
* **Purpose:** Directly load active corrections models.
* **Response Schema (200 OK):** List of correction objects.

---

### GET /debug/clusters
* **Purpose:** Directly load query pattern clusters.
* **Response Schema (200 OK):** List of clusters.

---

### GET /debug/failures
* **Purpose:** Directly load failure models.
* **Response Schema (200 OK):** List of failure models.

---

### GET /debug/learning-graph
* **Purpose:** Retrieve complete learning graph extending the base knowledge graph.
* **Response Schema (200 OK):** ReactFlow structured network nodes containing base, pattern, correction, cluster, and failure nodes.

---

### GET /debug/world-model
* **Purpose:** Fetch raw JSON representation of the simulation world model database.
* **Response Schema (200 OK):** Full raw JSON storage state.

---

### GET /policy-failures
* **Purpose:** Fetch failures detected during policy simulation.
* **Response Schema (200 OK):** Array of policy failure objects.

---

### GET /debug/meta
* **Purpose:** Get raw strategy, reflection, and replay database states.
* **Response Schema (200 OK):** Full meta database state.

---

### GET /debug/personality
* **Purpose:** Get raw database status of the personality engine.
* **Response Schema (200 OK):** Full user style and preference settings state.

---

## 13. UI WebSockets Connection

### GET/WS /ui/ws
* **Protocol:** WebSocket (RFC 6455)
* **Message Protocol:** JSON
* **Message Types:**
  - **Ping Message (Client to Server):**
    ```json
    { "type": "ping" }
    ```
  - **Pong Message (Server to Client):**
    ```json
    { "type": "pong", "timestamp": "2026-06-24T10:23:15.123Z" }
    ```
  - **Other Messages (Echo Broadcast):** Sends payload data directly back to client.

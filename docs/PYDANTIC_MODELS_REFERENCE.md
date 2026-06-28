# Pydantic Models Reference - Antigravity AI OS (Milestones 1–18)

This reference documents the system's Pydantic model configurations. Lovable AI can mirror these objects in TypeScript interfaces for front-end state managers, form payloads, and graph node mapping.

---

## 1. Retrieval & Evidence Models

### `EvidenceNode`
* **Defined in:** `app/retrieval/evidence_models.py`
* **Purpose:** Represents a single piece of retrieved semantic evidence.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `evidence_id` | `str` | Unique evidence node identifier. | - | No | `"ev_db_001"` |
| `source` | `str` | Filename or document title source. | - | No | `"database_doc.pdf"` |
| `source_type` | `str` | Extension or data source format. | - | No | `"pdf"` |
| `modality` | `str` | Content medium (`text`, `ocr`, `image`, `vqa`, `audio`). | - | No | `"text"` |
| `content` | `str` | The parsed text content snippet or caption. | - | No | `"Connection pool size is 20."` |
| `retrieval_score`| `float` | Query vector relevance score. | - | No | `0.854` |
| `confidence` | `str` | Categorical confidence (`High`, `Medium`, `Low`). | - | No | `"High"` |
| `citation_reason`| `str` | Explicit reasoning explaining why this node matches. | - | No | `"Contains database config parameters."` |
| `metadata` | `dict` | Key-value dictionary containing page/offsets. | `None` | Yes | `{"page": 3}` |
| `timestamp_start`| `float` | Audio/video starting second offset. | `None` | Yes | `12.5` |
| `timestamp_end` | `float` | Audio/video ending second offset. | `None` | Yes | `18.0` |
| `visual_category`| `str` | Image intent label (`diagram`, `chart`, `natural`). | `None` | Yes | `"diagram"` |
| `file_path` | `str` | Absolute local disk directory location. | `None` | Yes | `"/storage/uploads/doc.pdf"` |
| `provenance` | `dict` | Trace tracking retriever engine and stages. | `None` | Yes | `{"retriever": "text"}` |

---

## 2. Multi-Agent Reasoning Models

### `GoalNode`
* **Defined in:** `app/retrieval/agent_models.py`
* **Purpose:** Tracks the primary user goal/query inside the agent planning loop.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `goal_id` | `str` | Unique goal tracking ID. | - | No | `"goal_01a"` |
| `query` | `str` | Original user request query string. | - | No | `"Solve DB replication issue"` |
| `goal_type` | `str` | Categorization type of request. | - | No | `"debugging"` |
| `timestamp` | `str` | Chronological date-time string. | - | No | `"2026-06-24T10:00:00Z"` |

### `PlanNode`
* **Defined in:** `app/retrieval/agent_models.py`
* **Purpose:** Tracks step-by-step reasoning strategies.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `plan_id` | `str` | Unique plan tracker ID. | - | No | `"plan_01a"` |
| `goal_id` | `str` | Target goal reference ID. | - | No | `"goal_01a"` |
| `steps` | `List[str]` | Array of textual plan step instructions. | - | No | `["Verify port configuration", "Check DB status"]` |
| `status` | `str` | Current workflow state. | - | No | `"in_progress"` |

### `TaskNode`
* **Defined in:** `app/retrieval/agent_models.py`
* **Purpose:** Tracks sub-task executions.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `task_id` | `str` | Unique subtask ID. | - | No | `"task_01_a"` |
| `description` | `str` | Textual description of action. | - | No | `"Invoke CLIP vector search for schemas"` |
| `dependency_ids`| `List[str]` | IDs of preceding tasks that must complete first. | - | No | `[]` |
| `status` | `str` | Current execution status (`pending`, `running`, `success`, `failed`).| - | No | `"pending"` |

---

## 3. Semantic Graph & Knowledge Models

### `EntityNode`
* **Defined in:** `app/retrieval/knowledge_models.py`
* **Purpose:** Represents a unique extracted entity node in the semantic graph.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `entity_id` | `str` | Unique entity identifier in graph storage. | - | No | `"ent_sqlite"` |
| `name` | `str` | Extracted name literal. | - | No | `"SQLite"` |
| `canonical_name`| `str` | Normalized core name. | - | No | `"SQLite Database"` |
| `entity_type` | `str` | Category node classification type. | - | No | `"database"` |
| `aliases` | `List[str]` | Variant strings referencing the node. | `[]` | No | `["sqlite3", "local_db"]` |
| `mentions` | `int` | Number of times entity was observed. | `1` | No | `4` |
| `confidence` | `float` | Cumulative confidence score. | `1.0` | No | `0.95` |
| `sources` | `List[str]` | List of documents mentioning the entity. | `[]` | No | `["config.py"]` |
| `supporting_modalities`| `List[str]`| Extraction modalities (`text`, `ocr`, etc.). | `[]` | No | `["text"]` |
| `created_at` | `str` | Graph node creation date-time. | - | No | `"2026-06-24T10:00:00Z"` |
| `updated_at` | `str` | Graph node update date-time. | - | No | `"2026-06-24T10:15:00Z"` |
| `last_seen` | `str` | Last occurrence timestamp. | - | No | `"2026-06-24T10:15:00Z"` |
| `importance_score`| `float` | Central significance metric. | `0.0` | No | `0.78` |
| `community_id` | `str` | Group cluster community ID. | `None` | Yes | `"comm_storage"` |

---

## 4. Conversational & Episodic Memory Models

### `MemoryNode`
* **Defined in:** `app/retrieval/memory_models.py`
* **Purpose:** Core memory node representing conversational instances.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `memory_id` | `str` | Unique memory tracking ID. | - | No | `"mem_t1_0"` |
| `memory_type` | `str` | Classification (`turn_node`, `summary_node`, `preference_node`, `entity_node`). | - | No | `"turn_node"` |
| `content` | `str` | Textual content of memory payload. | - | No | `"User requested port offset mapping."` |
| `source` | `str` | Source session identification. | - | No | `"sess_abc"` |
| `score` | `float` | Recall score metric. | - | No | `0.88` |
| `timestamp` | `str` | Chronological date-time string. | - | No | `"2026-06-24T10:00:00Z"` |
| `importance` | `float` | Importance weighting factor. | - | No | `0.90` |

### `EpisodeNode`
* **Defined in:** `app/episodic/episodic_models.py`
* **Purpose:** Long-term memory episode node.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `episode_id` | `str` | Unique episodic identifier. | - | No | `"ep_101"` |
| `session_id` | `str` | Parent session tracker. | - | No | `"sess_abc"` |
| `summary` | `str` | Summarized text of this episode. | - | No | `"Configuration of PORT to 9090"` |
| `importance` | `float` | Importance coefficient. | - | No | `0.85` |
| `timestamp` | `str` | Event date-time string. | - | No | `"2026-06-24T10:00:00Z"` |
| `confidence` | `float` | Factual accuracy confidence level. | - | No | `0.95` |
| `metadata` | `dict` | Custom properties dictionary. | `None` | Yes | `{"reason": "manual_port_change"}` |

---

## 5. Simulation & World Model Models

### `WorldStateNode`
* **Defined in:** `app/simulation/simulation_models.py`
* **Purpose:** Represents a state projection in the world simulation model.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `state_id` | `str` | Unique projected state identifier. | - | No | `"ws_stage_1"` |
| `summary` | `str` | Textual forecast summary. | - | No | `"Cache hits drop below 50% under load."` |
| `status` | `str` | Predicted system stability status (`Success`, `Risk`, `Failure`).| - | No | `"Risk"` |
| `timestamp` | `str` | Forecast runtime timestamp. | - | No | `"2026-06-24T10:00:00Z"` |

### `HypothesisNode`
* **Defined in:** `app/simulation/simulation_models.py`
* **Purpose:** Hypotheses variables evaluated under simulated parameters.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `hypothesis_id` | `str` | Unique hypothesis tracking ID. | - | No | `"hyp_01"` |
| `description` | `str` | Speculative scenario test description. | - | No | `"ChromaDB connection drops during runtime."` |
| `confidence` | `float` | Probability rating. | - | No | `0.72` |

---

## 6. Meta-Cognition & Tool Learning Models

### `ToolLearningNode`
* **Defined in:** `app/meta/meta_models.py`
* **Purpose:** Represents performance metrics discovered for specific tools.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `tool_id` | `str` | Unique tool identifier. | - | No | `"tool_txt_ret"` |
| `tool_name` | `str` | Internal tool key. | - | No | `"TextRetrievalTool"` |
| `frequency` | `int` | Cumulative execution counts. | `0` | No | `45` |
| `success_rate` | `float` | Success percentage score. | `1.0` | No | `0.978` |
| `latency_ms` | `float` | Average execution runtime (ms). | `0.0` | No | `42.5` |
| `last_used` | `str` | Last execution date-time. | - | No | `"2026-06-24T10:00:00Z"` |

### `MetaReflectionNode`
* **Defined in:** `app/meta/meta_models.py`
* **Purpose:** Tracks self-reflections on tool execution path patterns.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `reflection_id` | `str` | Unique reflection identifier. | - | No | `"refl_01a"` |
| `query_signature`| `str` | Hashed signature key for query pattern. | - | No | `"sig_db_config"` |
| `reflection_summary`| `str` | Text description of the reasoning issue. | - | No | `"Text search fails, fallback to VQA diagrams."` |
| `issues_detected`| `List[str]`| Array of diagnosed problem issues. | `[]` | No | `["text_query_out_of_vocab"]` |
| `recommendations` | `List[str]`| Recommended actions for future routing. | `[]` | No | `["boost_image_retrieval"]` |
| `timestamp` | `str` | Reflection compilation timestamp. | - | No | `"2026-06-24T10:20:00Z"` |

---

## 7. Personalization & Layout Models

### `HumanPreferenceNode`
* **Defined in:** `app/personality/personality_models.py`
* **Purpose:** User customization preferences.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `preference_id` | `str` | Unique preference tracking ID. | - | No | `"pref_usr_1"` |
| `user_entities` | `List[str]` | Entities associated with preferences. | `[]` | No | `["default_user"]` |
| `preferred_domains`| `List[str]`| Focus areas (`engineering`, `finance`, etc.). | `[]` | No | `["engineering"]` |
| `explanation_depth`| `str` | Preferred description level (`short`, `medium`, `detailed`). | `"medium"` | No | `"detailed"` |
| `tone_preference`| `str` | Bot voice profile (`professional`, `casual`, `technical`). | `"professional"`| No | `"technical"` |
| `response_length`| `int` | Preferred length in tokens. | `200` | No | `350` |
| `confidence` | `float` | Preference confidence value. | `0.5` | No | `0.85` |
| `timestamp` | `str` | Creation date-time. | - | No | `"2026-06-24T10:00:00Z"` |

### `UserStyleNode`
* **Defined in:** `app/personality/personality_models.py`
* **Purpose:** Extracted typing and verbosity preferences.

| Field | Type | Description | Default | Nullable | Example |
|---|---|---|---|---|---|
| `style_id` | `str` | Unique style profile ID. | - | No | `"style_usr_1"` |
| `writing_style` | `str` | Profile style key (`concise`, `elaborate`).| - | No | `"concise"` |
| `verbosity` | `str` | Verbosity metric. | - | No | `"low"` |
| `formatting_style`| `str` | Code output formatting layout. | - | No | `"markdown"` |
| `emoji_usage` | `bool` | Toggle for user layout emoji output. | `False` | No | `true` |
| `confidence` | `float` | Style confidence. | `0.5` | No | `0.90` |

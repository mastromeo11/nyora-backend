# Timeline Structures Reference - Antigravity AI OS

The Antigravity AI OS organizes temporal activities into timelines. This document details the timeline structures, JSON schemas, visualization metadata (icons, colors), and datasets for all 6 system timeline types.

---

## 1. Timeline Visualization Metadata

To render timelines with cohesive visual layouts, each timeline category uses distinct metadata markers:

| Timeline Type | Primary Color (Hex) | Icon Indicator (lucide-react) | Purpose |
|---|---|---|---|
| **Episode Timeline** | `#BD00FF` (Purple) | `History` | Chronological conversation turns and episodes. |
| **Simulation Timeline** | `#EF4444` (Red) | `Sparkles` | Projected world state forks and simulations. |
| **Policy Timeline** | `#3B82F6` (Blue) | `ShieldCheck` | Planner model calibration history. |
| **Reflection Timeline** | `#10B981` (Green) | `Cpu` | Self-reflection logs and exceptions diagnostics. |
| **Personality Timeline** | `#F59E0B` (Amber) | `User` | User style drifts and custom settings changes. |
| **Interaction Timeline**| `#6366F1` (Indigo) | `MousePointer` | Layout clicks, splits, and visual swaps. |

---

## 2. Universal Timeline Event JSON Schema

All events mapped to UI timelines must conform to this schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TimelineEvent",
  "type": "object",
  "properties": {
    "event_id": { "type": "string" },
    "timeline_type": {
      "type": "string",
      "enum": ["episode", "simulation", "policy", "reflection", "personality", "interaction"]
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "importance": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "metadata": { "type": "object" }
  },
  "required": ["event_id", "timeline_type", "timestamp", "title", "description", "importance"]
}
```

---

## 3. Timeline Type Payloads

### A. Episode Timeline Event
```json
{
  "event_id": "evt_ep_101",
  "timeline_type": "episode",
  "timestamp": "2026-06-24T10:00:00Z",
  "title": "Turn 4: Local Port Setup",
  "description": "User requested default port configurations and checked FastAPI launch variables.",
  "importance": 0.75,
  "metadata": {
    "session_id": "sess_abc",
    "entities": ["FastAPI", "PORT"],
    "evidence_nodes_count": 2
  }
}
```

---

### B. Simulation Timeline Event
```json
{
  "event_id": "evt_sim_204",
  "timeline_type": "simulation",
  "timestamp": "2026-06-24T10:05:00Z",
  "title": "Simulation Branch Fork A Generated",
  "description": "World model projected system behavior if ChromaDB encounters read latency increases.",
  "importance": 0.90,
  "metadata": {
    "projected_state": "ws_chroma_latency_risk",
    "risk_level": "medium",
    "predicted_success_probability": 0.92
  }
}
```

---

### C. Policy Timeline Event
```json
{
  "event_id": "evt_pol_308",
  "timeline_type": "policy",
  "timestamp": "2026-06-24T10:10:00Z",
  "title": "Strategy Replay Recalibrated",
  "description": "ReAct strategy sequence updated to include ImageRetrievalTool as first-order execution step.",
  "importance": 0.80,
  "metadata": {
    "policy_id": "pol_react",
    "previous_success_rate": 0.92,
    "new_success_rate": 0.95
  }
}
```

---

### D. Reflection Timeline Event
```json
{
  "event_id": "evt_ref_412",
  "timeline_type": "reflection",
  "timestamp": "2026-06-24T10:15:00Z",
  "title": "System Self-Reflection Generated",
  "description": "Diagnosed failure in TextRetrievalTool routing. Fallback strategies applied successfully.",
  "importance": 0.85,
  "metadata": {
    "reflection_id": "refl_01a",
    "query_signature": "sig_db_config",
    "issues": ["text_query_out_of_vocab"]
  }
}
```

---

### E. Personality Timeline Event
```json
{
  "event_id": "evt_pers_516",
  "timeline_type": "personality",
  "timestamp": "2026-06-24T10:20:00Z",
  "title": "Tone Preference Drift Discovered",
  "description": "Detected preference drift towards highly technical formatting options.",
  "importance": 0.70,
  "metadata": {
    "user_id": "default_user",
    "new_tone_preference": "technical",
    "confidence": 0.85
  }
}
```

---

### F. Interaction Timeline Event
```json
{
  "event_id": "evt_int_620",
  "timeline_type": "interaction",
  "timestamp": "2026-06-24T10:22:00Z",
  "title": "Layout Switch: Split View Enabled",
  "description": "User switched layout configuration to split-screen to preview PDF diagrams alongside text chat.",
  "importance": 0.50,
  "metadata": {
    "layout_mode": "split_view",
    "active_panel": "canvas"
  }
}
```

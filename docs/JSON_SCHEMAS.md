# JSON Schemas Reference - Antigravity AI OS

This document details the standard JSON Schema draft-07 definitions for the key data models, request payloads, and API responses of the backend systems. This allows Lovable AI to perform validation on states, socket events, and network parameters.

---

## 1. ChatRequest

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChatRequest",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The user input message or question."
    },
    "session_id": {
      "type": "string",
      "description": "Unique UUID tracking conversational memory turns."
    }
  },
  "required": ["query", "session_id"],
  "additionalProperties": false
}
```

### JSON Example
```json
{
  "query": "Find the latest network connection issues.",
  "session_id": "sess-441-2a91"
}
```

---

## 2. ChatResponse

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChatResponse",
  "type": "object",
  "properties": {
    "answer": {
      "type": "string",
      "description": "Generated LLM response."
    },
    "confidence": {
      "type": "string",
      "enum": ["High", "Medium", "Low"]
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "source": { "type": "string" },
          "page": { "type": "integer" },
          "modality": { "type": "string" }
        },
        "required": ["source", "modality"]
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "evidence_id": { "type": "string" },
          "source": { "type": "string" },
          "source_type": { "type": "string" },
          "modality": { "type": "string" },
          "content": { "type": "string" },
          "retrieval_score": { "type": "number" },
          "confidence": { "type": "string" },
          "citation_reason": { "type": "string" }
        },
        "required": ["evidence_id", "source", "modality", "content", "retrieval_score"]
      }
    },
    "why_this_answer": {
      "type": "array",
      "items": { "type": "string" }
    },
    "supporting_modalities": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": [
    "answer",
    "confidence",
    "confidence_score",
    "sources",
    "evidence",
    "why_this_answer",
    "supporting_modalities"
  ]
}
```

---

## 3. MemoryResponse

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MemoryResponse",
  "type": "object",
  "properties": {
    "memory_used": {
      "type": "boolean"
    },
    "session_summary": {
      "type": "string"
    },
    "active_entities": {
      "type": "array",
      "items": { "type": "string" }
    },
    "memory_sources": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["memory_used", "session_summary", "active_entities", "memory_sources"]
}
```

---

## 4. EpisodeNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EpisodeNode",
  "type": "object",
  "properties": {
    "episode_id": { "type": "string" },
    "session_id": { "type": "string" },
    "summary": { "type": "string" },
    "importance": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "metadata": { "type": "object" }
  },
  "required": ["episode_id", "session_id", "summary", "importance", "timestamp", "confidence"]
}
```

---

## 5. WorldStateNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WorldStateNode",
  "type": "object",
  "properties": {
    "state_id": { "type": "string" },
    "summary": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["Success", "Risk", "Failure"]
    },
    "timestamp": { "type": "string" }
  },
  "required": ["state_id", "summary", "status"]
}
```

---

## 6. SimulationNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SimulationNode",
  "type": "object",
  "properties": {
    "sim_id": { "type": "string" },
    "score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "path": { "type": "string" }
  },
  "required": ["sim_id", "score", "path"]
}
```

---

## 7. ScenarioNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ScenarioNode",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "summary": { "type": "string" },
    "success_probability": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    }
  },
  "required": ["id", "summary", "success_probability"]
}
```

---

## 8. PolicyNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PolicyNode",
  "type": "object",
  "properties": {
    "policy_id": { "type": "string" },
    "planner_type": { "type": "string" },
    "success_rate": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    }
  },
  "required": ["policy_id", "planner_type", "success_rate"]
}
```

---

## 9. ToolLearningNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ToolLearningNode",
  "type": "object",
  "properties": {
    "tool_id": { "type": "string" },
    "tool_name": { "type": "string" },
    "frequency": { "type": "integer", "default": 0 },
    "success_rate": { "type": "number", "default": 1.0 },
    "latency_ms": { "type": "number", "default": 0.0 },
    "last_used": { "type": "string" }
  },
  "required": ["tool_id", "tool_name", "last_used"]
}
```

---

## 10. MetaReflectionNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MetaReflectionNode",
  "type": "object",
  "properties": {
    "reflection_id": { "type": "string" },
    "query_signature": { "type": "string" },
    "reflection_summary": { "type": "string" },
    "issues_detected": { "type": "array", "items": { "type": "string" } },
    "recommendations": { "type": "array", "items": { "type": "string" } },
    "timestamp": { "type": "string" }
  },
  "required": ["reflection_id", "query_signature", "reflection_summary", "timestamp"]
}
```

---

## 11. HumanPreferenceNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HumanPreferenceNode",
  "type": "object",
  "properties": {
    "preference_id": { "type": "string" },
    "user_entities": { "type": "array", "items": { "type": "string" } },
    "preferred_domains": { "type": "array", "items": { "type": "string" } },
    "explanation_depth": { "type": "string", "enum": ["short", "medium", "detailed"] },
    "tone_preference": { "type": "string", "enum": ["professional", "casual", "technical"] },
    "response_length": { "type": "integer" },
    "confidence": { "type": "number" },
    "timestamp": { "type": "string" }
  },
  "required": ["preference_id", "timestamp"]
}
```

---

## 12. ThemeNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ThemeNode",
  "type": "object",
  "properties": {
    "theme": {
      "type": "string",
      "enum": ["dark_cyber", "midnight_blue", "dracula", "matrix_green", "claude_sand", "chatgpt_green", "github_dark", "apple_vision", "glass_black", "purple_neon"]
    },
    "last_updated": { "type": "string" }
  },
  "required": ["theme", "last_updated"]
}
```

---

## 13. VoiceStateNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VoiceStateNode",
  "type": "object",
  "properties": {
    "voice_id": { "type": "string" },
    "voice_mode": {
      "type": "string",
      "enum": ["idle", "listening", "transcribing", "speaking"]
    },
    "volume": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
  },
  "required": ["voice_id", "voice_mode"]
}
```

---

## 14. NotificationNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NotificationNode",
  "type": "object",
  "properties": {
    "notification_id": { "type": "string" },
    "type": { "type": "string", "enum": ["info", "warning", "success", "error"] },
    "message": { "type": "string" }
  },
  "required": ["notification_id", "type", "message"]
}
```

---

## 15. WorkspaceNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WorkspaceNode",
  "type": "object",
  "properties": {
    "workspace_id": { "type": "string" },
    "name": { "type": "string" },
    "folders": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["workspace_id", "name", "folders"]
}
```

---

## 16. GraphNode

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GraphNode",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "type": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "label": { "type": "string" }
      },
      "required": ["label"]
    }
  },
  "required": ["id", "type", "data"]
}
```

---

## 17. GraphEdge

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GraphEdge",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string" },
    "target": { "type": "string" },
    "animated": { "type": "boolean", "default": false }
  },
  "required": ["id", "source", "target"]
}
```

---

## 18. TimelineEvent

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TimelineEvent",
  "type": "object",
  "properties": {
    "event_id": { "type": "string" },
    "title": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "description": { "type": "string" },
    "metadata": { "type": "object" }
  },
  "required": ["event_id", "title", "timestamp", "description"]
}
```

---

## 19. ErrorResponse

### Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ErrorResponse",
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Detailed error string returned by FastAPI exception handlers."
    }
  },
  "required": ["detail"],
  "additionalProperties": false
}
```

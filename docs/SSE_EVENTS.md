# Server-Sent Events (SSE) Reference - Antigravity AI OS

The Antigravity AI OS uses Server-Sent Events (SSE) to stream query answers and reasoning traces word-by-word. This document defines the stream formats, structured payload types, and event envelopes used by the frontend chat interface to render Perplexity-style reasoning cards and text generation streams.

---

## 1. Stream Endpoint & Protocol

* **Route:** `/ui/chat/stream`
* **Method:** `GET`
* **Query Parameters:** `query` (string, required)
* **Response Headers:**
  * `Content-Type: text/event-stream`
  * `Cache-Control: no-cache`
  * `Connection: keep-alive`

---

## 2. Event Payload Contracts

Every SSE stream output consists of standard text-line event envelopes:
```
event: [EVENT_TYPE]
data: [JSON_PAYLOAD]
```

---

### A. `token`
* **Purpose:** Emits individual word tokens during text generation.
* **Payload Example:**
```
event: token
data: {"token": "database "}
```

---

### B. `thinking` (Chain-of-Thought)
* **Purpose:** Streams reasoning logs before final execution.
* **Payload Example:**
```
event: thinking
data: {"step": "Searching local vector indexes for configuration parameters...", "duration_ms": 140.0}
```

---

### C. `citation`
* **Purpose:** Streams file identifiers and modalities of source nodes.
* **Payload Example:**
```
event: citation
data: {
  "citation_id": "cite_042",
  "source": "database_setup.pdf",
  "page": 4,
  "modality": "text",
  "snippet": "PORT is loaded from env, default 8000."
}
```

---

### D. `tool_call`
* **Purpose:** Notifies the client that the planner has dispatched a tool execution request.
* **Payload Example:**
```
event: tool_call
data: {
  "tool_name": "ImageRetrievalTool",
  "arguments": {
    "query": "database schema diagram",
    "limit": 3
  }
}
```

---

### E. `tool_result`
* **Purpose:** Sends outcomes returned by tool execution.
* **Payload Example:**
```
event: tool_result
data: {
  "tool_name": "ImageRetrievalTool",
  "success": true,
  "results_count": 1,
  "results": [
    {
      "source": "schema_diagram.png",
      "file_path": "/storage/uploads/schema_diagram.png",
      "visual_category": "diagram"
    }
  ]
}
```

---

### F. `memory_hit`
* **Purpose:** Notifies the UI that an active topic or user preference memory has been recalled.
* **Payload Example:**
```
event: memory_hit
data: {
  "memory_type": "preference_node",
  "key": "explanation_depth",
  "value": "detailed",
  "confidence": 0.85
}
```

---

### G. `simulation_hit`
* **Purpose:** Sent when the simulator evaluates future states or failures during planning.
* **Payload Example:**
```
event: simulation_hit
data: {
  "state_id": "ws_connection_failure",
  "summary": "Simulating sqlite connection timeout",
  "risk_score": 0.95
}
```

---

### H. `final_answer`
* **Purpose:** Dispatches the final answer string, aggregate sources, and metrics summary.
* **Payload Example:**
```
event: final_answer
data: {
  "answer": "The database port is configured using environment variables.",
  "confidence": "High",
  "confidence_score": 0.94,
  "total_sources": 1,
  "total_evidence_nodes": 1
}
```

---

### I. `done`
* **Purpose:** Standard termination event.
* **Payload Example:**
```
event: done
data: [DONE]
```

---

### J. `error`
* **Purpose:** Sent when the local engine or model pipeline encounters connection exceptions.
* **Payload Example:**
```
event: error
data: {
  "status_code": 500,
  "detail": "Failed to connect to Ollama server."
}
```

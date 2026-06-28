# Error Schemas Reference - Antigravity AI OS

This contract defines standard error envelopes, HTTP status codes, and error code values returned by the backend systems when encountering exceptions.

---

## 1. Standard Error Envelope

All error responses from the backend follow a standard JSON layout:

```json
{
  "error_code": "ERROR_CODE_IDENTIFIER",
  "detail": "Descriptive human-readable error details explaining the exception cause.",
  "timestamp": "2026-06-24T10:24:00Z",
  "diagnostics": {}
}
```

---

## 2. Error Class Reference

### A. `ValidationError`
* **HTTP Status Code:** `400 Bad Request` or `422 Unprocessable Entity`
* **Purpose:** Thrown when request body parameters violate schema rules or data types.
* **Payload Example:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "detail": "The field 'query' cannot be empty or exceed 1000 characters.",
  "timestamp": "2026-06-24T10:24:05Z",
  "diagnostics": {
    "field": "query",
    "received": ""
  }
}
```

---

### B. `ToolError`
* **HTTP Status Code:** `502 Bad Gateway`
* **Purpose:** Thrown when a planner tool fails execution.
* **Payload Example:**
```json
{
  "error_code": "TOOL_EXECUTION_FAILURE",
  "detail": "Tool 'TextRetrievalTool' failed: ChromaDB index is not ready.",
  "timestamp": "2026-06-24T10:24:10Z",
  "diagnostics": {
    "tool_name": "TextRetrievalTool",
    "raw_exception": "IndexNotFoundException"
  }
}
```

---

### C. `TimeoutError`
* **HTTP Status Code:** `504 Gateway Timeout`
* **Purpose:** Sent when LLM generation or agent plan reasoning exceeds configured limits.
* **Payload Example:**
```json
{
  "error_code": "PLANNER_TIMEOUT",
  "detail": "Agent planner failed to complete execution within 45 seconds.",
  "timestamp": "2026-06-24T10:24:15Z",
  "diagnostics": {
    "elapsed_seconds": 45.1,
    "limit_seconds": 45
  }
}
```

---

### D. `MemoryError`
* **HTTP Status Code:** `500 Internal Server Error`
* **Purpose:** Thrown when conversational or short-term memory files fail serialization.
* **Payload Example:**
```json
{
  "error_code": "MEMORY_SERIALIZATION_FAILED",
  "detail": "Failed to write conversational turn records to session cache.",
  "timestamp": "2026-06-24T10:24:20Z",
  "diagnostics": {
    "session_id": "sess-44b2"
  }
}
```

---

### E. `GraphError`
* **HTTP Status Code:** `500 Internal Server Error`
* **Purpose:** Triggered when the entity graph fails schema updates or migration queries.
* **Payload Example:**
```json
{
  "error_code": "GRAPH_MIGRATION_FAILED",
  "detail": "Failed to apply schema migrations to entity relation store.",
  "timestamp": "2026-06-24T10:24:25Z",
  "diagnostics": {
    "target_version": 2
  }
}
```

---

### F. `SimulationError`
* **HTTP Status Code:** `500 Internal Server Error`
* **Purpose:** Projection engine failure during scenario runs.
* **Payload Example:**
```json
{
  "error_code": "SIMULATION_PROJECTOR_EXCEPTION",
  "detail": "Failed to project scenario branches: depth level exceeded limits.",
  "timestamp": "2026-06-24T10:24:30Z",
  "diagnostics": {
    "sim_id": "sim_01b",
    "current_depth": 6
  }
}
```

---

### G. `VoiceError`
* **HTTP Status Code:** `502 Bad Gateway`
* **Purpose:** Thrown when audio transcription (Whisper) or speech generation fails.
* **Payload Example:**
```json
{
  "error_code": "VOICE_TRANSLATION_FAILED",
  "detail": "Audio transcription failed: invalid file encoding headers.",
  "timestamp": "2026-06-24T10:24:35Z",
  "diagnostics": {
    "file_format": "m4a"
  }
}
```

---

### H. `FileError`
* **HTTP Status Code:** `400 Bad Request` or `500 Internal Server Error`
* **Purpose:** Ingestion pipeline failure during upload parsing.
* **Payload Example:**
```json
{
  "error_code": "DOCUMENT_PARSING_FAILED",
  "detail": "Parser failed to read PDF: file is corrupted or password protected.",
  "timestamp": "2026-06-24T10:24:40Z",
  "diagnostics": {
    "filename": "tax_form.pdf"
  }
}
```

---

### I. `CacheError`
* **HTTP Status Code:** `500 Internal Server Error`
* **Purpose:** Thrown when LRU cache locks fail.
* **Payload Example:**
```json
{
  "error_code": "CACHE_MUTEX_LOCK_TIMEOUT",
  "detail": "Timed out waiting for theme cache read locks.",
  "timestamp": "2026-06-24T10:24:45Z",
  "diagnostics": {
    "cache_type": "theme"
  }
}
```

---

### J. `PolicyError`
* **HTTP Status Code:** `500 Internal Server Error`
* **Purpose:** Reinforcement model policy calibration failures.
* **Payload Example:**
```json
{
  "error_code": "POLICY_REINFORCEMENT_FAILED",
  "detail": "Failed to update strategy success rating coefficients.",
  "timestamp": "2026-06-24T10:24:50Z",
  "diagnostics": {
    "policy_id": "pol_react"
  }
}
```

---

### K. `PersonalityError`
* **HTTP Status Code:** `500 Internal Server Error`
* **Purpose:** Thrown when visual tone profiling failures occur.
* **Payload Example:**
```json
{
  "error_code": "PERSONALITY_ADAPTATION_EXCEPTION",
  "detail": "Failed to evaluate adaptive writing tone profile parameters.",
  "timestamp": "2026-06-24T10:24:55Z",
  "diagnostics": {
    "user_id": "default_user"
  }
}
```

# WebSocket Events Reference - Antigravity AI OS

The Antigravity AI OS supports real-time state synchronization via persistent WebSockets connected to `ws://localhost:8000/ui/ws`. This document defines the payload contracts for all client-to-server and server-to-client events.

---

## 1. Connection Lifecycle

### Connect
* **Endpoint:** `ws://localhost:8000/ui/ws`
* **Protocol:** WebSocket RFC 6455
* **Action:** The client establishes a TCP connection, which the backend accepts using the FastAPI `ConnectionManager`. Once connected, the client is added to the active broadcast list.

### Disconnect
* **Action:** Fired automatically when the client closes the browser tab or encounters network drops. The backend automatically catches `WebSocketDisconnect` exceptions and removes the socket from the memory broadcaster array.

---

## 2. Heartbeat Protocol (Client-Initiated)

To keep the local socket connection alive and diagnose network latency, clients submit a recurring heartbeat ping event.

### Ping (Client -> Server)
* **Payload:**
```json
{
  "type": "ping"
}
```

### Pong (Server -> Client Response)
* **Payload:**
```json
{
  "type": "pong",
  "timestamp": "2026-06-24T10:24:00.125Z"
}
```

---

## 3. Server-to-Client Broadcast Events

The backend automatically broadcasts state updates to all active UI websocket connections when underlying database nodes or configurations change.

### `dashboard_update`
* **Purpose:** Pushes latest telemetry metrics (CPU, RAM, latency, cache rates).
* **Payload Example:**
```json
{
  "type": "dashboard_update",
  "timestamp": "2026-06-24T10:24:05Z",
  "data": {
    "schema_version": 1,
    "cpu_usage_pct": 14.8,
    "ram_usage_mb": 428.2,
    "latency_ms": 105.0,
    "cache_hit_rate": 0.78,
    "episode_count": 45,
    "policies_count": 8,
    "world_states_count": 14,
    "active_threads": 4,
    "requests_total": 1258
  }
}
```

---

### `graph_update`
* **Purpose:** Notifies the client that semantic node-link relationships have been added, modified, or decayed.
* **Payload Example:**
```json
{
  "type": "graph_update",
  "timestamp": "2026-06-24T10:24:10Z",
  "data": {
    "action": "node_added",
    "node": {
      "id": "entity_fastapi",
      "type": "entity",
      "data": {
        "label": "FASTAPI"
      }
    }
  }
}
```

---

### `notification`
* **Purpose:** Pushed when the background parsing pipeline, swarms, or claim validators trigger alerts.
* **Payload Example:**
```json
{
  "type": "notification",
  "timestamp": "2026-06-24T10:24:15Z",
  "data": {
    "notification_id": "notif_8a92",
    "type": "warning",
    "message": "Factual Claim grounding accuracy fell below 80% on user query response."
  }
}
```

---

### `chat_chunk`
* **Purpose:** Stream chunk event used as websocket-based fallback for text-generation tokens.
* **Payload Example:**
```json
{
  "type": "chat_chunk",
  "session_id": "sess-99b24-77ac-4a81-9d10",
  "token": "database ",
  "index": 14,
  "is_final": false
}
```

---

### `simulation_update`
* **Purpose:** Pushed when new world state scenarios or counterfactual branches are generated.
* **Payload Example:**
```json
{
  "type": "simulation_update",
  "timestamp": "2026-06-24T10:24:20Z",
  "data": {
    "sim_id": "sim_81c2",
    "projected_state": "ws_risk_branch",
    "score": 0.94,
    "risk_level": "medium"
  }
}
```

---

### `memory_update`
* **Purpose:** Sent when conversational turns decay or long-term episodes are compressed into summaries.
* **Payload Example:**
```json
{
  "type": "memory_update",
  "timestamp": "2026-06-24T10:24:25Z",
  "data": {
    "action": "summary_generated",
    "summary_id": "sum_turn_10",
    "summary": "User updated local sqlite database connection configurations."
  }
}
```

---

### `policy_update`
* **Purpose:** Pushed when the planner ranking, tools weights, or success rates are recalibrated.
* **Payload Example:**
```json
{
  "type": "policy_update",
  "timestamp": "2026-06-24T10:24:30Z",
  "data": {
    "tool_name": "TextRetrievalTool",
    "success_rate": 0.98,
    "average_latency_ms": 41.2
  }
}
```

---

### `theme_update`
* **Purpose:** Pushed when the UI theme profile changes or is updated by user personalization scripts.
* **Payload Example:**
```json
{
  "type": "theme_update",
  "timestamp": "2026-06-24T10:24:35Z",
  "data": {
    "theme": "matrix_green"
  }
}
```

---

### `workspace_update`
* **Purpose:** Triggered when folders are added or deleted from the workspace list.
* **Payload Example:**
```json
{
  "type": "workspace_update",
  "timestamp": "2026-06-24T10:24:40Z",
  "data": {
    "workspace_id": "ws_default",
    "action": "folder_added",
    "folder": "src/controllers"
  }
}
```

---

## 4. Error Broadcast Events

### `error`
* **Purpose:** Dispatches socket failure messages to show warning dialogs on the UI client.
* **Payload Example:**
```json
{
  "type": "error",
  "timestamp": "2026-06-24T10:24:45Z",
  "data": {
    "error_code": "SWARM_BROKER_TIMEOUT",
    "message": "The multi-agent swarm broker timed out waiting for consensus answers."
  }
}
```

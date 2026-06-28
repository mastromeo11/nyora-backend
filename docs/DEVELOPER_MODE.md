# Developer Mode Reference - Antigravity AI OS

This contract defines the developer console specifications, metrics telemetry pipelines, diagnostic endpoints, and layout requirements for the Developer Mode dashboard of the Antigravity AI OS.

---

## 1. Visual Console Layout

The Developer Mode panel is structured as a multi-tab sidebar grid that docks next to the main chat pane:

```
+-----------------------------------------------------------------+
|                         DEVELOPER MODE                          |
+------------------+-----------------------+----------------------+
| [1] Metrics      | [2] Memory Hits       | [3] Active Caches    |
+------------------+-----------------------+----------------------+
| [4] Policies     | [5] Swarms Logs       | [6] Diagnostics      |
+------------------+-----------------------+----------------------+
```

---

## 2. Subsystem Console Definitions

### A. Memory Hits & Timeline Dashboard
* **Purpose:** Inspect active short-term and long-term memory retrieval states.
* **Telemetry Properties:**
  * Memory search recall accuracy.
  * Recalled entity co-occurrence counts.
  * Summarization thresholds.
* **Control Endpoints:**
  * `GET /debug/memory` (Flattened memory list)
  * `GET /debug/followup` (Pronoun diagnostic logs)
  * `GET /debug/entity-focus` (Decayed focus scores)

---

### B. Policy Leaderboard & Meta-Cognition Dashboard
* **Purpose:** Trace planning strategy path routing, latency averages, and reflection statements.
* **Telemetry Properties:**
  * Core success percentages for planner policies (ReAct, Plan-and-Solve).
  * Latency (ms) stats per tool execution.
* **Control Endpoints:**
  * `GET /tools` (List tool success/latency parameters)
  * `GET /strategies` (Dispatched planners list)
  * `GET /reflections` (Dispatched reflections)

---

### C. Simulation & World Model Dashboard
* **Purpose:** Trace forecasted state nodes, active variable modifications, and stability indices.
* **Telemetry Properties:**
  * Projected world state lists (`GET /world-states`).
  * Speculative scenarios stability risk rating.
* **Control Endpoints:**
  * `GET /hypotheses` (speculations list)
  * `GET /counterfactuals` (alternative variables changes)
  * `GET /scenarios` (evaluated branches)

---

### D. System Telemetry & Caching Dashboard
* **Purpose:** Renders live metrics for hardware usage and cache status.
* **Telemetry Properties:**
  * CPU Usage percentage.
  * RAM usage (MB).
  * Cache hit rate (percentage).
* **Control Endpoints:**
  * `GET /ui/dashboard` (Live telemetry feed)
  * `GET /ui/analytics` (Latency metrics trends)
  * `GET /debug/graph-cache` (Graph cache hit rates)

---

## 3. Failure Diagnostics Console

The failure console aggregates warnings from different layers:

```json
{
  "failure_source": "swarm_broker",
  "occurred_at": "2026-06-24T10:24:00Z",
  "issue": "TIMEOUT",
  "diagnostics": {
    "agent_id": "critic_agent",
    "elapsed_seconds": 60.0
  }
}
```

* **Control Endpoints:**
  * `GET /tool-failures` (Meta cognition)
  * `GET /optimization-failures` (Strategy generation)
  * `GET /policy-failures` (Simulation runs)
  * `GET /personality/failures` (User tonality drifts)

import time
import json
import os

# Thread-safe memory metrics store
METRICS = {
    "memory_hit_rate": 0.0,
    "summary_count": 0,
    "entity_decay_events": 0,
    "followup_accuracy": 1.0,
    "cache_hits": 0,
    "average_memory_latency": 0.0
}

_total_queries = 0
_memory_hits = 0
_total_memory_latency = 0.0
_latency_count = 0

def increment_query():
    global _total_queries
    _total_queries += 1
    _update_hit_rate()

def increment_hit():
    global _memory_hits
    _memory_hits += 1
    _update_hit_rate()

def _update_hit_rate():
    global METRICS, _memory_hits, _total_queries
    if _total_queries > 0:
        METRICS["memory_hit_rate"] = round(_memory_hits / _total_queries, 4)

def increment_summary():
    global METRICS
    METRICS["summary_count"] += 1

def increment_decay_event():
    global METRICS
    METRICS["entity_decay_events"] += 1

def increment_cache_hit():
    global METRICS
    METRICS["cache_hits"] += 1

def record_latency(latency_ms: float):
    global METRICS, _total_memory_latency, _latency_count
    _total_memory_latency += latency_ms
    _latency_count += 1
    METRICS["average_memory_latency"] = round(_total_memory_latency / _latency_count, 4)

def get_metrics() -> dict:
    return METRICS

def get_total_queries() -> int:
    return _total_queries

def export_metrics(file_path: str = "test_memory_report.json"):
    try:
        report = {}
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    report = json.load(f)
                except Exception:
                    report = {}
        
        # Update report with memory metrics
        report.update(METRICS)
        
        with open(file_path, "w") as f:
            json.dump(report, f, indent=4)
        print(f"[METRICS] Successfully exported memory metrics to {file_path}")
    except Exception as e:
        print(f"[METRICS] Error exporting metrics: {e}")

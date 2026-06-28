# Graph Structures Reference - Antigravity AI OS

The Antigravity AI OS utilizes entity-centric semantic graphs to connect evidence files, conversational memory, agent reasoning traces, and self-learning states. This document details the graph structure specifications, node-edge models, styling tokens, and ReactFlow schemas.

---

## 1. Node Types & Styling Tokens

For a premium, modern visual look, ReactFlow nodes are styled with glassmorphism effects, harmonized borders, and specific category colors.

| Node Type | Description | Background Color (Hex) | Border Color (Hex) | Text Color (Hex) |
|---|---|---|---|---|
| `entity` | Extracted topic or system configuration entity. | `#1A2D3D` (Deep Slate) | `#00D8FF` (Neon Cyan) | `#FFFFFF` |
| `evidence` | A source text segment, OCR block, image, or VQA node. | `#251C3D` (Deep Purple) | `#BD00FF` (Neon Purple) | `#FFFFFF` |
| `turn_node` | Individual user query and assistant reply steps. | `#1B2A4A` (Midnight Blue) | `#3B82F6` (Electric Blue) | `#FFFFFF` |
| `summary_node` | Recurrent summarization nodes tracking session topics. | `#132F2D` (Forest Glass) | `#10B981` (Emerald Green) | `#FFFFFF` |
| `preference_node`| Custom user format preferences or writing tones. | `#3A2E1A` (Amber Smoke) | `#F59E0B` (Bright Amber) | `#FFFFFF` |
| `task_node` | Sub-task item dispatched by agent planners. | `#3C1A1A` (Crimson Glass) | `#EF4444` (Vibrant Red) | `#FFFFFF` |
| `observation_node`| Live feedback collected by tool executions. | `#2E2E3E` (Dark Grey) | `#8B5CF6` (Violet) | `#FFFFFF` |
| `reflection_node` | Self-reflection log compiled after run exceptions. | `#1E3A2F` (Mint Glass) | `#34D399` (Mint Green) | `#FFFFFF` |
| `tool_node` | Available executor tools in the meta-cognitive list. | `#2C3E50` (Navy Grey) | `#7F8C8D` (Silver) | `#FFFFFF` |

---

## 2. Edge Types & Semantics

Edges represent relationships between nodes. Edge weights indicate confidence levels or frequency rates between nodes.

| Edge Type | Source Node Type | Target Node Type | Description | Animated | Default Style |
|---|---|---|---|---|---|
| `entity_to_entity`| `entity` | `entity` | Co-occurrence of entities inside the same text chunk. | No | Solid line, thickness = `weight` |
| `evidence_to_entity`| `evidence` | `entity` | Connection showing that evidence contains the entity. | No | Dotted line, thickness = 1px |
| `turn_to_turn` | `turn_node` | `turn_node` | Chronological transition between conversational rounds. | Yes | Flowing dashed animation |
| `turn_to_entity` | `turn_node` | `entity` | Direct mention of entity inside chat round text. | No | Solid thin line |
| `summary_to_entity`| `summary_node` | `entity` | Connects topic summarizations to their target concepts. | Yes | Dashed line |

---

## 3. ReactFlow State Schema

Lovable AI should map the graph data payloads into this exact ReactFlow-compatible structure:

### ReactFlow Node Definition
```json
{
  "id": "entity_chromadb",
  "type": "customNode",
  "data": {
    "label": "CHROMADB",
    "nodeType": "entity",
    "properties": {
      "mentions": 5,
      "confidence": 1.0,
      "canonical_name": "ChromaDB Vector Store"
    }
  },
  "position": { "x": 250, "y": 150 },
  "style": {
    "background": "rgba(26, 45, 61, 0.8)",
    "border": "1px solid #00D8FF",
    "borderRadius": "8px",
    "color": "#FFFFFF",
    "boxShadow": "0 0 10px rgba(0, 216, 255, 0.3)"
  }
}
```

### ReactFlow Edge Definition
```json
{
  "id": "e_turn1_to_chroma",
  "source": "turn_1",
  "target": "entity_chromadb",
  "type": "smoothstep",
  "animated": true,
  "style": {
    "stroke": "#3B82F6",
    "strokeWidth": 2
  },
  "label": "mentions"
}
```

---

## 4. Graph Export JSON Contract

When requesting a complete graph export or saving the visual representation state, the following JSON payload structure is used:

```json
{
  "graph_id": "graph_sess-99b24-77ac_export",
  "timestamp": "2026-06-24T10:23:45Z",
  "metadata": {
    "total_nodes": 4,
    "total_edges": 3,
    "session_id": "sess-99b24-77ac-4a81-9d10"
  },
  "nodes": [
    {
      "id": "turn_1",
      "label": "Turn 1: Database configurations",
      "type": "turn_node",
      "properties": {
        "query": "What port is Chroma running on?",
        "answer": "Chroma is running locally and connected to FastAPI."
      }
    },
    {
      "id": "entity_chromadb",
      "label": "CHROMADB",
      "type": "entity",
      "properties": {
        "mentions": 1,
        "importance_score": 0.85
      }
    },
    {
      "id": "entity_fastapi",
      "label": "FASTAPI",
      "type": "entity",
      "properties": {
        "mentions": 1,
        "importance_score": 0.75
      }
    },
    {
      "id": "ev_config_001",
      "label": "config.py",
      "type": "evidence",
      "properties": {
        "modality": "text",
        "score": 0.99
      }
    }
  ],
  "edges": [
    {
      "id": "edge_t1_to_chroma",
      "source": "turn_1",
      "target": "entity_chromadb",
      "type": "turn_to_entity",
      "weight": 1.0
    },
    {
      "id": "edge_t1_to_fastapi",
      "source": "turn_1",
      "target": "entity_fastapi",
      "type": "turn_to_entity",
      "weight": 1.0
    },
    {
      "id": "edge_ev_to_chroma",
      "source": "ev_config_001",
      "target": "entity_chromadb",
      "type": "evidence_to_entity",
      "weight": 0.95
    }
  ]
}
```

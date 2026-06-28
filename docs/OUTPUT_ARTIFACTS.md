# Output Artifacts Reference - Antigravity AI OS

The Antigravity AI OS supports streaming and rendering rich visual and textual output formats called Artifacts. This document defines the payload structures, metadata schemas, and JSON models for every supported output type.

---

## 1. Global Artifact Payload Structure

All returned Rich Artifacts must conform to this standard JSON wrapper structure:

```json
{
  "artifact_id": "art_92bc4",
  "type": "code",
  "title": "Quick Sort Implementation",
  "indexation_status": "synced",
  "metadata": {},
  "preview_available": true,
  "download_url": "/ui/download/art_92bc4"
}
```

---

## 2. Artifact Specific Specifications

### A. Code & Markdown Artifacts
* **Purpose:** Render inline syntax-highlighted code files or fully compiled markdown documents.
* **Payload Model:**
```json
{
  "artifact_id": "art_code_001",
  "type": "code",
  "title": "server.py",
  "metadata": {
    "language": "python",
    "theme": "monokai"
  },
  "content": "from fastapi import FastAPI\napp = FastAPI()\n"
}
```

---

### B. Table, CSV & Excel Artifacts
* **Purpose:** Render structured spreadsheets and tabular charts.
* **Payload Model:**
```json
{
  "artifact_id": "art_sheet_10",
  "type": "table",
  "title": "Q2 Financial Statistics",
  "metadata": {
    "columns": ["Item", "Revenue", "Margin"],
    "total_rows": 2
  },
  "content": [
    ["Database Licenses", "$45,000", "85%"],
    ["Model Fine-tuning Consulting", "$120,000", "75%"]
  ]
}
```

---

### C. PDF, DOCX & PPTX Document Artifacts
* **Purpose:** Reference physical binary documents extracted during pipeline steps.
* **Payload Model:**
```json
{
  "artifact_id": "art_doc_quarterly",
  "type": "pdf",
  "title": "Q3_Report_Final.pdf",
  "metadata": {
    "file_size_bytes": 1420455,
    "pages": 12,
    "extracted_chunks": 48
  },
  "preview_available": true,
  "download_url": "/ui/download/art_doc_quarterly"
}
```

---

### D. Image, Audio & Video Modality Artifacts
* **Purpose:** Represent media attachments referenced in multimodal queries or visual QA candidate arrays.
* **Payload Model:**
```json
{
  "artifact_id": "art_media_02",
  "type": "image",
  "title": "database_layout_v1.png",
  "metadata": {
    "file_path": "/storage/uploads/database_layout_v1.png",
    "dimensions": "1920x1080",
    "visual_category": "diagram",
    "caption": "Database tables and relationships diagram."
  },
  "preview_available": true
}
```

---

### E. Graph, Timeline & ReactFlow Artifacts
* **Purpose:** Expose visualized semantic relation charts.
* **Payload Model:**
```json
{
  "artifact_id": "art_graph_sess",
  "type": "graph",
  "title": "Conversational Memory Semantic Graph",
  "metadata": {
    "graph_engine": "ReactFlow",
    "nodes_count": 2,
    "edges_count": 1
  },
  "content": {
    "nodes": [
      { "id": "n1", "type": "turn", "data": { "label": "Turn 1" } },
      { "id": "n2", "type": "entity", "data": { "label": "ChromaDB" } }
    ],
    "edges": [
      { "id": "e1", "source": "n1", "target": "n2", "animated": true }
    ]
  }
}
```

---

### F. Voice & Speech Artifacts (TTS)
* **Purpose:** Reference output audio playback buffers generated via Text-to-Speech engines.
* **Payload Model:**
```json
{
  "artifact_id": "art_voice_audio",
  "type": "audio",
  "title": "response_reading.wav",
  "metadata": {
    "audio_encoding": "wav",
    "sample_rate": 22050,
    "duration_seconds": 12.4
  },
  "preview_available": true,
  "download_url": "/ui/download/art_voice_audio"
}
```

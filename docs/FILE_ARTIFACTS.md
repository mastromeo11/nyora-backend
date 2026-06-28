# File Artifacts Reference - Antigravity AI OS

This specification defines the backend schemas, preview configurations, metadata objects, and download routes for all 9 supported file formats.

---

## 1. Supported File Types & Preview Modes

| Extension | Format | Ingestion Subsystem | Visual UI Preview Component | Download Payload Type |
|---|---|---|---|---|
| **.png, .jpg**| Image | CLIP / Ingestion | Image canvas with bounding box overlays. | `image/png`, `image/jpeg` |
| **.wav, .mp3**| Audio | Whisper | Waveform player with speed control. | `audio/wav`, `audio/mpeg` |
| **.mp4** | Video | Ingestion | Frame canvas player. | `video/mp4` |
| **.pdf** | Document | PDF parser | PDF document reader with pagination. | `application/pdf` |
| **.docx** | Document | DOCX parser | Rich-text renderer. | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| **.csv** | Data | Table parser | Data table grid with sort filters. | `text/csv` |
| **.xlsx** | Data | Table parser | Multi-tab sheet component. | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| **.pptx** | Document | Slide parser | Slide deck carousel. | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| **.zip** | Package | Archive handler | Folder directory tree explorer. | `application/zip` |

---

## 2. Universal File Schema

All uploaded or generated files mapped inside active workspace folders must return this structure:

### File Metadata Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FileMetadata",
  "type": "object",
  "properties": {
    "file_id": { "type": "string" },
    "filename": { "type": "string" },
    "file_size_bytes": { "type": "integer" },
    "mime_type": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "indexation_status": {
      "type": "string",
      "enum": ["pending", "processing", "indexed", "failed"]
    },
    "preview_endpoint": { "type": "string" },
    "download_endpoint": { "type": "string" },
    "metadata": { "type": "object" }
  },
  "required": [
    "file_id",
    "filename",
    "file_size_bytes",
    "mime_type",
    "indexation_status",
    "preview_endpoint",
    "download_endpoint"
  ]
}
```

---

## 3. Metadata Models

### A. Document File Metadata (PDF / DOCX / PPTX)
```json
{
  "file_id": "file_pdf_88a",
  "filename": "database_setup.pdf",
  "file_size_bytes": 1048576,
  "mime_type": "application/pdf",
  "created_at": "2026-06-24T10:00:00Z",
  "indexation_status": "indexed",
  "preview_endpoint": "/ui/preview/file_pdf_88a",
  "download_endpoint": "/ui/download/file_pdf_88a",
  "metadata": {
    "pages_count": 24,
    "extracted_chunks": 96,
    "has_tables": true,
    "has_diagrams": true
  }
}
```

---

### B. Image File Metadata (PNG / JPG)
```json
{
  "file_id": "file_img_42c",
  "filename": "er_diagram.png",
  "file_size_bytes": 524288,
  "mime_type": "image/png",
  "created_at": "2026-06-24T10:05:00Z",
  "indexation_status": "indexed",
  "preview_endpoint": "/ui/preview/file_img_42c",
  "download_endpoint": "/ui/download/file_img_42c",
  "metadata": {
    "dimensions": "1920x1080",
    "detected_visual_category": "diagram",
    "model_caption": "Entity relationship diagram detailing primary key mapping."
  }
}
```

---

### C. Audio & Video File Metadata (WAV / MP3 / MP4)
```json
{
  "file_id": "file_aud_71b",
  "filename": "team_meeting.wav",
  "file_size_bytes": 4194304,
  "mime_type": "audio/wav",
  "created_at": "2026-06-24T10:10:00Z",
  "indexation_status": "indexed",
  "preview_endpoint": "/ui/preview/file_aud_71b",
  "download_endpoint": "/ui/download/file_aud_71b",
  "metadata": {
    "duration_seconds": 180.4,
    "audio_sample_rate": 44100,
    "transcription_status": "completed",
    "transcription_chunks_count": 12
  }
}
```
---

### D. Archive Package Metadata (ZIP)
```json
{
  "file_id": "file_zip_99e",
  "filename": "source_code.zip",
  "file_size_bytes": 8388608,
  "mime_type": "application/zip",
  "created_at": "2026-06-24T10:15:00Z",
  "indexation_status": "indexed",
  "preview_endpoint": "/ui/preview/file_zip_99e",
  "download_endpoint": "/ui/download/file_zip_99e",
  "metadata": {
    "total_compressed_files": 45,
    "has_directories": true,
    "supported_preview_extensions": [".py", ".json", ".txt"]
  }
}
```

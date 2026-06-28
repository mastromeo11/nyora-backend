# Artifact Renderer Specifications - Antigravity AI OS

The Antigravity AI OS is a multi-modal operating system layer. Answers are not constrained to standard chat text bubbles; instead, the frontend dynamically launches dedicated renderers and split-pane viewers based on the output payload modality and file extension. This document defines the rendering components, interactive actions, and libraries for all supported formats.

---

## 1. Modality & Renderer Registry

| Target Modality | File Extensions | Frontend Renderer Engine | Layout / Render Container | Interactive Actions |
|---|---|---|---|---|
| **TEXT** | `.txt, .md` | Custom Markdown Renderer | Centered message pane, inline cards. | Copy text, print, expand view. |
| **IMAGE** | `.png, .jpg` | Image Canvas Viewer | Split-screen canvas overlay with bounding boxes. | Zoom, pan, category labels, crop. |
| **AUDIO** | `.wav, .mp3` | Custom Waveform player | Waveform widget, floating footer. | Play, pause, seek, volume. |
| **VIDEO** | `.mp4` | Video Canvas Card | Split-screen video block. | Play, pause, frame step. |
| **PDF** | `.pdf` | PDF Document Reader | Two-column split-pane container. | Zoom, page search, download. |
| **DOCX** | `.docx` | Rich-Text Renderer | Full-width document previewer. | Edit styles, copy formatted text. |
| **PPT** | `.pptx` | Slide deck carousel | Presentation canvas container. | Previous, next slide, fullscreen. |
| **CODE** | `.py, .js, .json` | Monaco Code Editor | Split-screen workspace container. | Syntax highlight, save, run script. |
| **TABLE** | `.csv, .xlsx` | Spreadsheet Grid | Grid layout container. | Sort column, filter rows, export. |
| **GRAPH** | - | ReactFlow Canvas | Interactive node-link panel. | Node inspection, filters, layouts. |
| **TIMELINE** | - | Timeline Viewer | Chronological feed container. | Filter by topic, play event chain. |

---

## 2. Modality Render Details

### A. TEXT (Markdown Renderer)
* **Visual Component:** Uses `react-markdown` with `remark-gfm` to format tables, blockquotes, and lists inline.
* **Special Behavior:** Detects inline citations (e.g. `[1]`) and overlays them as interactive buttons. Clicking an overlay opens the source document in a split view.

---

### B. IMAGE (Image Canvas Viewer)
* **Visual Component:** Renders image attachments in a split-screen viewer.
* **Special Behavior:** Displays CLIP similarity scores and bounding boxes for visual QA candidates.

---

### C. AUDIO (Waveform Player)
* **Visual Component:** Integrates `wavesurfer.js` to render the input audio signal levels.
* **Special Behavior:** Displays transcription timestamps synchronized with audio playback.

---

### D. VIDEO (Video Canvas Card)
* **Visual Component:** HTML5 video elements wrapped in customized dark cyber control cards.
* **Special Behavior:** Displays video description metadata and frames counts.

---

### E. PDF (PDF Document Reader)
* **Visual Component:** Uses `react-pdf` to render pages side-by-side with pagination controls.
* **Special Behavior:** Highlights text segments matched during vector retrieval.

---

### F. DOCX (Rich-Text Renderer)
* **Visual Component:** Custom parser displaying raw text with paragraphs and indentation.
* **Special Behavior:** Allows users to copy formatted rich text to the clipboard.

---

### G. PPT (Slide Deck Carousel)
* **Visual Component:** Slide previewer with touch gesture handlers for carousel navigation.
* **Special Behavior:** Renders slide transcripts beside the active slide.

---

### H. CODE (Monaco Code Editor)
* **Visual Component:** Integrates the Microsoft Monaco Editor.
* **Special Behavior:** Provides auto-save triggers, syntax highlighting, and code folding.

---

### I. TABLE (Spreadsheet Grid)
* **Visual Component:** A fast spreadsheet grid component.
* **Special Behavior:** Allows users to search and sort tables, and export data in Excel/CSV formats.

---

### J. GRAPH (ReactFlow Canvas)
* **Visual Component:** Renders dynamic node-link graph layouts.
* **Special Behavior:** Highlights connected nodes and displays node metrics.

---

### K. TIMELINE (Timeline Viewer)
* **Visual Component:** Renders vertical chronological cards.
* **Special Behavior:** Animates transaction logs and transition sequences.

# Iconography & Color Tokens - Antigravity AI OS

This specification details the design tokens for icons, colors, statuses, policy categories, memory components, and simulation indicators. It ensures a consistent and visual UI implementation.

---

## 1. Icon Library Mapping (Lucide Icons)

| Component Area | Lucide Icon | Core Purpose |
|---|---|---|
| **Chat Feed** | `MessageSquare` | User conversational turns. |
| **System Answer** | `Cpu` | Generated LLM answers. |
| **Deep Research** | `Search` | Document index scanning. |
| **Workspace Folder**| `FolderOpen` | Directory navigation. |
| **Monaco Editor** | `Code` | Source editing tabs. |
| **Evidence PDF** | `FileText` | Uploaded document references. |
| **CLIP Image** | `Image` | Image search matches. |
| **Voice Microphone**| `Mic` | Audio recording status. |
| **Swarms Broker** | `Network` | Agent communication grids. |
| **Simulation Project**| `Sliders` | Projected alternative states. |
| **Telemetry console**| `Terminal` | Developer logging tables. |
| **Analytics Trend** | `TrendingUp` | Metric graph visuals. |
| **Settings Theme** | `Palette` | Theme selections. |
| **Alerts Toast** | `Bell` | System warning flags. |

---

## 2. Color System Mappings

### A. Subsystem Specific Color Indicators
Subsystems are color-coded in visual widgets:

* **Conversational Memory:**
  * Primary: `#10B981` (Emerald Green)
  * Visual Accent: `rgba(16, 185, 129, 0.2)`
* **Swarms & Agents:**
  * Primary: `#F59E0B` (Bright Amber)
  * Visual Accent: `rgba(245, 158, 11, 0.2)`
* **Simulation Engine:**
  * Primary: `#EF4444` (Vibrant Red)
  * Visual Accent: `rgba(239, 68, 68, 0.2)`
* **Meta Cognition:**
  * Primary: `#3B82F6` (Electric Blue)
  * Visual Accent: `rgba(59, 130, 246, 0.2)`
* **Knowledge Graph:**
  * Primary: `#00D8FF` (Neon Cyan)
  * Visual Accent: `rgba(0, 216, 255, 0.2)`

---

### B. Status Indicator Colors

| Status | Color Representation | Hex Code | Visual Style |
|---|---|---|---|
| **Success / Connected**| Green | `#10B981` | Solid green badge, active pulse. |
| **Warning / Risk** | Amber | `#F59E0B` | Solid amber badge. |
| **Failure / Error** | Red | `#EF4444` | Solid red badge, slow flash. |
| **Pending / Inactive** | Slate | `#64748B` | Dotted grey outline. |
| **Processing / Running**| Blue | `#3B82F6` | Solid blue badge with spinning ring. |

---

## 3. Theme Mappings

Icons are dynamically colored based on the active CSS theme:

* **Apple Vision / Midnight Blue:** Use white or soft silver borders with glowing drop-shadows.
* **Matrix Green:** Monochrome scale: everything colored in shades of lime green (`#00FF41`).
* **Dark Cyber / Purple Neon:** Semi-transparent gradient backdrops using high-contrast neon borders.

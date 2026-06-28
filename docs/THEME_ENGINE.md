# Theme Engine Reference - Antigravity AI OS

This specification details the design tokens, color configurations, borders, blurs, shadows, and spacing variables of the RAG PRO visual styling layer. It outlines 10 custom UI themes.

---

## 1. CSS Custom Property Visual Tokens

Every theme implements these visual properties to control components:

* **Font Family:** System sans-serif fallback with Inter, Roboto Mono, and JetBrains Mono.
  * *UI Sans:* `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
  * *Mono:* `"JetBrains Mono", "Fira Code", Monaco, Menlo, Consolas, monospace`
* **Spacing Scale:** Standard 4px-base layout system (`--spacing-1` = 4px, `--spacing-2` = 8px, `--spacing-4` = 16px, `--spacing-8` = 32px).
* **Corner Radius:** `--radius-sm` = 4px, `--radius-md` = 8px, `--radius-lg` = 12px, `--radius-full` = 9999px.
* **Animation Speeds:** `--speed-fast` = 150ms, `--speed-normal` = 300ms, `--speed-slow` = 500ms.

---

## 2. Visual Theme Configurations

### A. Dark Cyber
* **Vibe:** Sleek cyberpunk coding terminal.
* **Colors & Gradients:**
  * Background: `#0B0E14` (Deep Coal)
  * Card Background: `rgba(20, 26, 38, 0.7)`
  * Core Accent: `#00F0FF` (Cyber Neon Cyan)
  * Secondary Accent: `#FF007A` (Neon Pink)
  * Gradient: `linear-gradient(135deg, #00F0FF 0%, #FF007A 100%)`
* **Glassmorphism:** Blur: `12px`, Border: `1px solid rgba(0, 240, 255, 0.15)`
* **Shadow:** `0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 240, 255, 0.1)`

---

### B. Midnight Blue
* **Vibe:** Deep ocean night dashboard.
* **Colors & Gradients:**
  * Background: `#070F2B`
  * Card Background: `rgba(27, 26, 85, 0.7)`
  * Core Accent: `#535C91`
  * Secondary Accent: `#9290C3`
  * Gradient: `linear-gradient(135deg, #070F2B 0%, #1B1A55 100%)`
* **Glassmorphism:** Blur: `16px`, Border: `1px solid rgba(146, 144, 195, 0.1)`
* **Shadow:** `0 8px 32px 0 rgba(7, 15, 43, 0.5)`

---

### C. Dracula
* **Vibe:** Classic dark programming colors.
* **Colors & Gradients:**
  * Background: `#282a36`
  * Card Background: `rgba(68, 71, 90, 0.7)`
  * Core Accent: `#bd93f9` (Purple)
  * Secondary Accent: `#ff79c6` (Pink)
  * Gradient: `linear-gradient(135deg, #bd93f9 0%, #ff79c6 100%)`
* **Glassmorphism:** Blur: `8px`, Border: `1px solid rgba(189, 147, 249, 0.2)`
* **Shadow:** `0 10px 25px rgba(0, 0, 0, 0.4)`

---

### D. Matrix Green
* **Vibe:** Retro digital code space.
* **Colors & Gradients:**
  * Background: `#000000`
  * Card Background: `rgba(10, 25, 10, 0.8)`
  * Core Accent: `#00FF41` (Matrix Lime Green)
  * Secondary Accent: `#008F11` (Forest Green)
  * Gradient: `linear-gradient(180deg, #001100 0%, #000000 100%)`
* **Glassmorphism:** Blur: `4px`, Border: `1px solid rgba(0, 255, 65, 0.3)`
* **Shadow:** `0 0 10px rgba(0, 255, 65, 0.2)`

---

### E. Claude Sand
* **Vibe:** Minimalist, warm reading paper.
* **Colors & Gradients:**
  * Background: `#FBF9F6` (Alabaster Sand)
  * Card Background: `rgba(244, 240, 233, 0.8)`
  * Core Accent: `#D97706` (Terracotta)
  * Secondary Accent: `#78350F` (Amber Brown)
  * Gradient: `linear-gradient(135deg, #FBF9F6 0%, #F5F1EB 100%)`
* **Glassmorphism:** Blur: `2px`, Border: `1px solid rgba(120, 53, 15, 0.08)`
* **Shadow:** `0 4px 12px rgba(120, 53, 15, 0.04)`

---

### F. ChatGPT Green
* **Vibe:** Clean, modern conversational workspace.
* **Colors & Gradients:**
  * Background: `#202123`
  * Card Background: `rgba(52, 53, 65, 0.7)`
  * Core Accent: `#10a37f` (OpenAI Teal)
  * Secondary Accent: `#2a2b32`
  * Gradient: `linear-gradient(135deg, #202123 0%, #343541 100%)`
* **Glassmorphism:** Blur: `10px`, Border: `1px solid rgba(16, 163, 127, 0.15)`
* **Shadow:** `0 8px 30px rgba(0, 0, 0, 0.3)`

---

### G. GitHub Dark
* **Vibe:** Developer-centric code repository dashboard.
* **Colors & Gradients:**
  * Background: `#0D1117`
  * Card Background: `rgba(22, 27, 34, 0.8)`
  * Core Accent: `#58A6FF` (Blue Link)
  * Secondary Accent: `#30363D` (Border Grey)
  * Gradient: `linear-gradient(135deg, #0D1117 0%, #161B22 100%)`
* **Glassmorphism:** Blur: `6px`, Border: `1px solid #30363D`
* **Shadow:** `0 4px 16px rgba(0, 0, 0, 0.5)`

---

### H. Apple Vision
* **Vibe:** Semi-transparent spatial computing layers.
* **Colors & Gradients:**
  * Background: `radial-gradient(circle at center, #2e2a38 0%, #0d0b12 100%)`
  * Card Background: `rgba(255, 255, 255, 0.06)`
  * Core Accent: `#FFFFFF`
  * Secondary Accent: `rgba(255, 255, 255, 0.3)`
  * Gradient: `linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%)`
* **Glassmorphism:** Blur: `30px` (Ultra Blur), Border: `1px solid rgba(255, 255, 255, 0.12)`
* **Shadow:** `0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1)`

---

### I. Glass Black
* **Vibe:** Sleek glass layers.
* **Colors & Gradients:**
  * Background: `#050505`
  * Card Background: `rgba(15, 15, 15, 0.65)`
  * Core Accent: `#EAEAEA`
  * Secondary Accent: `#333333`
  * Gradient: `linear-gradient(135deg, #111111 0%, #050505 100%)`
* **Glassmorphism:** Blur: `20px`, Border: `1px solid rgba(255, 255, 255, 0.06)`
* **Shadow:** `0 12px 40px rgba(0, 0, 0, 0.7)`

---

### J. Purple Neon
* **Vibe:** High-energy visual gradients.
* **Colors & Gradients:**
  * Background: `#0A0915`
  * Card Background: `rgba(25, 20, 50, 0.7)`
  * Core Accent: `#8A2BE2` (Purple Neon)
  * Secondary Accent: `#FF00FF` (Magenta Glow)
  * Gradient: `linear-gradient(135deg, #8A2BE2 0%, #FF00FF 100%)`
* **Glassmorphism:** Blur: `14px`, Border: `1px solid rgba(255, 0, 255, 0.15)`
* **Shadow:** `0 8px 32px rgba(138, 43, 226, 0.25)`

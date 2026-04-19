# The Tinkerer's Grid

## 1. Identity Statement & Motto

**"DON'T BLACKOUT - a tinkerer's guide to energy"**

**Core Philosophy:**
*   **Bare Metal:** We favor directness, technical accuracy, and transparency over decorative flair.
*   **No Design Fuzz:** No gradients, no shadows, no rounded corners. Every visual element must serve a functional purpose.
*   **Down to the Point:** Information density, data visibility, and readability are paramount.
*   **Aesthetic:** A soft dark mode blending terminal utility with textbook clarity.

## 2. Typography

*   **Font Family:** A single, clean, technical sans-serif font is used globally across the entire application.
*   **Tabular Figures:** Crucially, we enforce **`font-variant-numeric: tabular-nums;`** globally. This guarantees perfect vertical alignment for all simulation charts, power grid data arrays, and financial figures without requiring a jarring switch to a separate monospace font.

## 3. Structure & Layout

*   **Absolute Minimalism:**
    *   `box-shadow: none;` (Zero drop shadows)
    *   `border-radius: 0px;` (Zero rounded corners)
*   **Hierarchy:** Visual structure and hierarchy are defined entirely through deliberate whitespace (padding/margins) and crisp **1px solid borders**.

## 4. Token Palette

Implement the following CSS variables globally to ensure consistency:

```css
:root {
  /* Backgrounds */
  --bg-base: #181A1B;       /* Deep charcoal background */
  --bg-surface: #222426;    /* Panels/Cards */
  --bg-hover: #2C2E30;      /* Hover states */

  /* Borders */
  --border-metal: #3A3D40;  /* Muted grid lines */

  /* Typography */
  --text-primary: #EAEAEA;
  --text-secondary: #9BA1A6;

  /* Accents & Status */
  --copper-raw: #D97736;       /* Primary actions, links, load curves */
  --copper-hover: #E88B4F;
  --copper-oxidized: #5E9C88;  /* Success states, generation curves */
  --danger-red: #D25C5C;       /* Errors, blackouts */
}
```

## 5. Component Behavior

*   **Cards/Panels:** Flat surface (`--bg-surface`) with a 1px `--border-metal` outline. No internal shadows.
*   **Buttons:**
    *   **Primary:** Solid `--copper-raw` background. Hover state uses `--copper-hover`.
    *   **Secondary:** Transparent background with a `--copper-raw` 1px outline and `--copper-raw` text.
*   **Forms/Inputs:** Flat `--bg-base` background with a `--border-metal` 1px border. On focus, the border must snap immediately to `--copper-raw` (no slow transition effects).
*   **Charts (Ferntree):**
    *   Gridlines utilize `--border-metal`.
    *   Data plots use `--copper-raw` (e.g., load/demand) and `--copper-oxidized` (e.g., generation/supply/battery charge).
    *   Grid stress or deficit areas use `--danger-red`.

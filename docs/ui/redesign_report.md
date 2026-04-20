# UI Redesign Report

## Scope

This report documents the completed implementation work for:

- **Phase 1: Foundation Tokens and Global Reset**
- **Phase 2: Shell and Navigation Refactor**

as defined in `docs/ui/redesign_plan.md`.

## Decisions Applied

- Focus color for global keyboard accessibility states: `--copper-raw`.
- Accent role for secondary positive/semantic accents: `--copper-oxidized`.

## Files Changed

- `frontend/src/styles/global.css`

## Implemented Changes

### 1) Token Foundation Replacement

Updated `:root` to include the Tinkerer's Grid semantic token set:

- `--bg-base`, `--bg-surface`, `--bg-hover`
- `--border-metal`
- `--text-primary`, `--text-secondary`
- `--copper-raw`, `--copper-hover`, `--copper-oxidized`
- `--danger-red`

Also set geometry/elevation baseline tokens:

- `--radius: 0`
- `--shadow: none`
- `--shadow-md: none`

To reduce regression risk in Phase 1, legacy token names were kept as compatibility aliases and mapped to the new semantic palette.

### 2) Global Typography Baseline

Applied global typography defaults in `html, body`:

- Single sans-serif family (`'IBM Plex Sans', 'Segoe UI', Helvetica, Arial, sans-serif`)
- `font-variant-numeric: tabular-nums`
- Base text/background mapped to `--text-primary` / `--bg-base`

### 3) Global Geometry and Elevation Reset

Applied base visual reset on universal selector:

- `border-radius: 0`
- `box-shadow: none`

This enforces the bare-metal requirement and removes rounded/shadowed styling globally.

### 4) Base Surface and Shell Updates

Updated core app shell surfaces:

- `#app` now uses `--bg-base` / `--text-primary`
- `#topnav` and `#sidenav` background switched from `white` to `--bg-surface`
- Shared white panel surfaces moved to dark surfaces in key primitives:
  - `.card`
  - `.loading-card`
  - `dialog`
  - `.blog-card`
  - `.blog-post-article`
  - `.landing-cta-strip`
  - `.landing-cta-primary`

### 5) Interactive Defaults and Focus Accessibility

Updated global interactive defaults:

- `a` now defaults to copper with hover using `--copper-hover`
- `button` defaults to dark surface + metal border
- `input/select/textarea` defaults to dark surface + metal border
- Global `:focus-visible` added with `2px solid var(--copper-raw)` and `outline-offset: 2px`

Updated existing control-specific focus states to copper:

- `.sidebar-select:focus`
- `.date-label input[type="date"]:focus`

Removed `outline: none` from `.form-input` to avoid suppressing keyboard focus visuals.

### 6) Literal Color Cleanup (Phase 1 baseline)

Converted selected hardcoded light-mode literals in shared/foundation areas:

- `.fin-warning` background/border to tokenized dark + danger treatment
- `.landing-hero` gradient replaced with flat `--bg-surface`

### 7) Shell and Navigation Refactor (Phase 2)

Refactored top navigation and workspace sidenav styling to use structural hierarchy and direct semantic tokens, while keeping route behavior unchanged.

Applied in `frontend/src/styles/global.css`:

- Topnav and sidenav borders now use `--border-metal` directly.
- Brand/logo accents in nav surfaces now use `--copper-raw` directly (no legacy alias reliance).
- Topnav link defaults updated to `--text-secondary`, with hover states using `--bg-hover` + `--text-primary`.
- Topnav active state changed from blue filled-pill treatment to structural copper emphasis:
  - transparent background
  - `color: var(--copper-raw)`
  - `border-bottom: 2px solid var(--copper-raw)`
- Sidenav link defaults updated to `--text-secondary`, with hover states using `--bg-hover` + `--text-primary`.
- Sidenav active state changed from blue filled-pill treatment to structural copper emphasis:
  - transparent background
  - `color: var(--copper-raw)`
  - `border-left: 2px solid var(--copper-raw)`
  - active padding compensation to prevent layout shift
- Nav interaction transitions were removed in these selectors to match direct, no-fuzz interaction behavior.
- Reserved `.topnav-link--app` variant remapped from blue aliases to copper tokens for consistency.

Mobile behavior alignment (also in `frontend/src/styles/global.css`):

- Corrected mobile label-hiding selector to match actual markup (`.topnav-logo span`).
- Normalized active sidenav link padding in collapsed icon-only mode so active indicators remain clean and usable.

No router logic changes were required. Existing `updateActiveNav()` and `has-sidenav` shell behavior continue to function as before.

## Verification

Build verification completed:

- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 1)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 2)

## Notes and Deferred Work

The following are intentionally deferred to later phases per plan:

- Full component variant redesign (buttons/forms/cards behavior details)
- Page-level visual harmonization across all sections
- Chart palette centralization and tokenized chart theme module

Phase 1 established the high-risk global foundation. Phase 2 completed shell/navigation visual refactoring without changing routing behavior or page templates.

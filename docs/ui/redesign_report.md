# UI Redesign Report

## Scope

This report documents the completed implementation work for:

- **Phase 1: Foundation Tokens and Global Reset**
- **Phase 2: Shell and Navigation Refactor**
- **Phase 3: Primitive Components Consolidation**
- **Phase 4: Workspace Views Migration**
- **Phase 5: Landing and Blog Integration**
- **Phase 6: Chart Theme Unification**
- **Phase 7: Cleanup and Consistency Enforcement**

as defined in `docs/ui/redesign_plan.md`.

## Decisions Applied

- Focus color for global keyboard accessibility states: `--copper-raw`.
- Accent role for secondary positive/semantic accents: `--copper-oxidized`.

## Files Changed

- `frontend/src/styles/global.css`
- `frontend/src/pages/models.ts`
- `frontend/src/pages/simulations.ts`
- `frontend/src/pages/finances.ts`
- `frontend/src/pages/landing-ferntree.ts`
- `frontend/src/chart-theme.ts`
- `frontend/src/router.ts`
- `frontend/src/pages/fin-results.ts` (removed)

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

### 8) Primitive Components Consolidation (Phase 3)

Consolidated shared UI primitives in `frontend/src/styles/global.css` so cards, buttons, forms, dialog/overlay, and warning/status surfaces align with the Tinkerer's Grid token semantics.

Loading overlay updates:

- `.loading-message` text moved to `--text-secondary`.
- Spinner ring updated to semantic tokens:
  - ring border uses `--border-metal`
  - spinner accent uses `--copper-raw`

Card primitive updates:

- `.card` now has a structural `1px solid var(--border-metal)` outline.
- `.card-header` decorative top accent was removed and replaced with a structural bottom divider:
  - removed `border-top: 4px` accent treatment
  - added `border-bottom: 1px solid var(--border-metal)`

Button primitive consolidation:

- `.btn` base transition removed (`opacity`-based hover behavior removed).
- `.btn-blue` remapped to canonical primary copper action style (`--copper-raw` / `--copper-hover`).
- `.btn-green` remapped to semantic success accent (`--copper-oxidized`) with explicit hover treatment.
- `.btn-orange` converted from filled variant to outlined copper action style:
  - transparent background
  - copper border and text
  - tokenized hover background/text/border
- `.btn-red` remapped to semantic danger token (`--danger-red`) with explicit hover treatment.
- `.btn-outline` normalized to structural secondary style:
  - `--border-metal` border
  - `--text-secondary` default text
  - `--bg-hover` + `--text-primary` hover state

Form primitive normalization:

- `.form-label` text color standardized to `--text-secondary`.
- `.form-input` border standardized to `--border-metal`.
- Focus behavior snapped to `--copper-raw` with no slow border transition.
- Error states standardized to `--danger-red` (`.form-input.error`, `.form-error`).

Workspace primitive consistency:

- `.workflow-card` moved from blue-tinted fill to structural surface:
  - background `--bg-surface`
  - `1px solid var(--border-metal)` border
  - hover state `--bg-hover`
- `.workflow-badge` remapped to copper (`--copper-raw`) with dark text.
- `.workflow-desc` and `.workflow-arrow` moved to `--text-secondary`.

Dialog primitive normalization:

- `dialog` now explicitly sets `background: var(--bg-surface)` and `color: var(--text-primary)`.
- `.dialog-header` and `.dialog-footer` borders now use `--border-metal`.

Status/warning utility cleanup:

- `.fin-warning` text standardized to `--text-secondary`.
- `.fin-warning-link` remapped from legacy blue to `--copper-raw`.
- `.empty-arrow` remapped from legacy blue to `--text-secondary`.

### 9) Workspace Views Migration (Phase 4)

Implemented workspace-page migration tasks in:

- `frontend/src/pages/models.ts`
- `frontend/src/pages/simulations.ts`
- `frontend/src/pages/finances.ts`
- `frontend/src/styles/global.css`

Inline style removal and class consolidation:

- Replaced inline loading/error state styles in Models with shared status utilities:
  - `.status-text`
  - `.status-text--error`
- Replaced inline card top-spacing in Simulations with `.card--mt`.
- Replaced inline no-simulation content layout styles in Finances with:
  - `.centered-card-text--mb`
  - `.centered-card-actions`
- Refactored donut legend swatches from inline `style="background:..."` to class-driven swatches:
  - `.legend-swatch--copper`
  - `.legend-swatch--border`

Workspace tokenization pass in `global.css`:

- Replaced workspace-section legacy aliases (`--gray-*`, `--blue-500`) with semantic tokens in Models, Simulations, and Finances selectors.
- Updated sidebar, form labels, card titles, KPI labels/values, date controls, and legend text styles to use:
  - `--text-primary`
  - `--text-secondary`
  - `--border-metal`
  - `--bg-base`
  - `--copper-raw`

Simulation chart theming updates (`frontend/src/pages/simulations.ts`):

- Removed legacy `COLORS` hex palette and introduced runtime token resolver:
  - `cssVar('--token-name')`
- Remapped chart series to semantic tokens:
  - load/deficit -> `--danger-red`
  - PV/primary -> `--copper-raw`
  - battery/generation -> `--copper-oxidized`
  - secondary/neutral -> `--border-metal` and `--text-secondary`
- Updated donut center label from hardcoded `#1f2937` to `--text-primary`.
- Removed bar chart corner rounding (`borderRadius: 3`) to preserve zero-radius geometry.
- Added tokenized chart UI styling for axes, grids, legend labels, and tooltips.

Finance chart theming updates (`frontend/src/pages/finances.ts`):

- Removed legacy `COLORS` hex palette and introduced runtime token resolver (`cssVar`).
- Remapped lifetime and performance chart datasets to semantic tokens:
  - investment/risk -> `--danger-red`
  - revenue/savings -> `--copper-oxidized`
  - cash flow and loan accents -> `--copper-raw` / `--copper-hover`
- Added tokenized chart UI styling for axes, grids, legend labels, and tooltips.

Behavioral integrity:

- No routing or API behavior changed.
- Existing interactions (model selection, run-sim navigation, finance calculation flow) remain intact; changes are presentation-layer only.

### 10) Landing and Blog Integration (Phase 5)

Implemented marketing/editorial migration tasks in:

- `frontend/src/styles/global.css`
- `frontend/src/pages/landing-ferntree.ts`

Tokenization and legacy-style removal in `global.css`:

- Migrated landing, blog-listing, blog-post, and DontBlackout selectors from legacy aliases and literals to semantic tokens:
  - `--text-primary`
  - `--text-secondary`
  - `--bg-base`
  - `--bg-surface`
  - `--bg-hover`
  - `--border-metal`
  - `--copper-raw`
  - `--copper-hover`
  - `--copper-oxidized`
- Removed hardcoded hero literals in landing styles (`white`, `rgb(255 255 255 / ...)`).
- Replaced decorative top-accent borders and lift effects in landing/blog cards:
  - removed `border-top: 4px ...` treatments
  - removed hover translate/shadow patterns
  - replaced with structural `1px` borders and `--bg-hover` state changes
- Updated blog post editorial styles for dark-surface readability:
  - headings on `--text-primary`
  - body copy on `--text-secondary`
  - links mapped to copper states
  - code and pre blocks mapped to `--bg-hover` + `--border-metal`
- Updated DontBlackout project section to the same product-surface system:
  - section background and separators mapped to base/metal tokens
  - icon and link accents remapped to copper

Template cleanup in `landing-ferntree.ts`:

- Removed inline SVG styling (`style="flex-shrink:0"`) and centralized behavior in CSS (`.btn svg { flex-shrink: 0; }`).
- Removed obsolete `landing-cta-secondary` class usage and relied on consolidated `btn btn-outline` primitive behavior.

Phase 5 QA checks completed:

- Verified no remaining `var(--gray-*)`, `var(--blue-*)`, or `var(--brand-blue)` references in landing/blog/DontBlackout selectors.
- Verified no remaining hardcoded white/rgba landing hero color literals.
- Verified no remaining `.landing-cta-secondary` selector or template usage.
- Verified DontBlackout and blog cards use structural border/surface + hover background behavior (no lift/shadow animation).
- Confirmed blog long-form content selectors cover links, headings, lists, and code blocks with tokenized styling.

### 11) Chart Theme Unification (Phase 6)

Implemented chart-theme centralization tasks in:

- `frontend/src/chart-theme.ts`
- `frontend/src/pages/simulations.ts`
- `frontend/src/pages/finances.ts`

Shared chart theme module:

- Added new `frontend/src/chart-theme.ts` module with reusable token-driven helpers:
  - `cssVar(name)` runtime token resolver
  - `tooltipTheme()` for shared tooltip surface, text, and border styles
  - `scaleTheme()` for shared axis tick/grid styling
  - `legendLabelTheme()` for shared legend label typography color
  - `chartTokens` accessors for canonical chart token mappings

Simulations and finances consolidation:

- Removed duplicate local `cssVar` helper definitions from both pages and imported shared helpers from `chart-theme.ts`.
- Replaced repeated inline Chart.js tooltip config with `...tooltipTheme()` in all chart renderers on both pages.
- Replaced repeated axis tick/grid styling with `...scaleTheme()` across bar and line charts on both pages.
- Replaced inline legend label color config with `...legendLabelTheme()` where legends are displayed.

Chart visual grammar and token mapping parity:

- Preserved dataset token roles across both pages:
  - primary/accent: `--copper-raw`
  - success/generation: `--copper-oxidized`
  - danger/deficit: `--danger-red`
  - neutral/grid: `--border-metal`
  - axis/secondary text: `--text-secondary`
  - legend/primary text: `--text-primary`
  - tooltip surface: `--bg-surface`
- Donut legend swatches remain class-driven (`legend-swatch--copper`, `legend-swatch--border`) with no inline color styles.

Phase 6 QA checks completed:

- Verified `cssVar` is centralized in `frontend/src/chart-theme.ts` (no local `function cssVar(...)` remains in page files).
- Verified both simulations and finances import shared chart theme helpers.
- Verified tooltip, scale, and legend label styles are token-driven via shared helpers in both pages.
- Verified no hardcoded chart color literals were introduced.
- Confirmed chart rendering behavior remains presentation-only with no routing/API logic changes.

### 12) Cleanup and Consistency Enforcement (Phase 7)

Implemented cleanup and consistency-enforcement tasks in:

- `frontend/src/styles/global.css`
- `frontend/src/router.ts`
- `frontend/src/pages/fin-results.ts` (removed)

Legacy token and obsolete style cleanup in `global.css`:

- Removed the full Phase 1 compatibility alias block from `:root`:
  - `--brand-blue`
  - `--blue-100`, `--blue-300`, `--blue-500`
  - `--rose-500`, `--amber-500`, `--teal-500`, `--indigo-500`
  - `--green-600`, `--red-500`, `--orange-500`
  - `--gray-50` through `--gray-900`
- Added shared overlay token and replaced duplicated hardcoded backdrop literals:
  - new token: `--overlay-backdrop: rgb(0 0 0 / 0.4)`
  - applied to both `#loading-overlay` and `dialog::backdrop`
- Removed unused reserved topnav variant selectors:
  - `.topnav-link--app`
  - `.topnav-link--app:hover`
  - `.topnav-link--app.active`
- Removed unused `.page-title` selector.
- Removed the lone transition outlier (`transition: background 0.15s`) from `.blog-back-link` to preserve direct interaction behavior.

Structural consistency in `global.css`:

- Added explicit wrapper rules for classes already present in templates so structure is self-documenting and complete:
  - `.sim-grid`
  - `.fin-grid`

Template/runtime inline-style cleanup:

- Removed inline-style fallback markup in `router.ts` and replaced it with class-driven markup:
  - error fallback now uses `.route-message.route-message--error`
  - 404 fallback now uses `.route-message`
- Added corresponding utility selectors in `global.css`:
  - `.route-message`
  - `.route-message--error`

Optional placeholder page validation / de-scope:

- Removed `frontend/src/pages/fin-results.ts` entirely.
- The page was previously an unregistered placeholder with inline style and no route/import usage, so removal reduced dead code without affecting routing behavior.

Phase 7 QA checks completed:

- Verified no remaining legacy token aliases are defined or referenced (`--gray-*`, `--blue-*`, `--brand-blue`, and related alias families).
- Verified no remaining unused Phase 7 target selectors (`.topnav-link--app*`, `.page-title`).
- Verified duplicated overlay/backdrop literal color was centralized under `--overlay-backdrop`.
- Verified `.sim-grid` and `.fin-grid` now have explicit CSS definitions.
- Verified router fallback messages no longer use inline styles.
- Verified optional `fin-results` placeholder is fully de-scoped (file removed, no route impact).
- Performed responsive regression review against existing mobile media-query breakpoints for workspace, landing, and blog route groups.

## Verification

Build verification completed:

- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 1)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 2)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 3)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 4)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 5)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 6)
- Command: `npm run build` (in `frontend/`)
- Result: success (Phase 7)

## Notes

Phase 1 established the high-risk global foundation. Phase 2 completed shell/navigation visual refactoring without changing routing behavior or page templates. Phase 3 consolidated primitive component behavior across shared styles. Phase 4 migrated workspace views to class-based, tokenized presentation. Phase 5 migrated landing and blog surfaces into the same identity system while preserving the DON'T BLACKOUT hero concept and improving long-form readability on dark surfaces. Phase 6 centralized chart theming into a shared module so simulations and finances now use one reusable token-driven chart grammar. Phase 7 removed legacy aliases, dead selectors, and unused placeholder code while enforcing class-driven styling and consistency across shell-level fallback states.

# Frontend Redesign Implementation Plan

This document defines an engineer-ready execution plan for implementing the new frontend identity, **The Tinkerer's Grid**, across the entire `frontend/` application.

## Objectives

- Unify visual identity across landing, blog, and Ferntree workspace pages.
- Apply the bare-metal design system from `docs/ui/design_concept.md`.
- Keep implementation maintainable in a vanilla TypeScript + Vite architecture.
- Minimize risk by using phased migration and clear acceptance criteria.

## Design-System Translation Rules

The redesign is a subtraction-first refactor. Decorative UI patterns are replaced with structural patterns.

| Component | Legacy Pattern to Remove | New Pattern |
| --- | --- | --- |
| Global typography | Mixed defaults and proportional numerals | Single sans-serif font family + global `font-variant-numeric: tabular-nums;` |
| Cards/panels | White backgrounds, rounded corners, shadows | `--bg-surface`, 1px `--border-metal`, `border-radius: 0`, `box-shadow: none` |
| Primary buttons | Filled blue/green variants, soft hover | Copper-led action style using `--copper-raw` and `--copper-hover` |
| Secondary buttons | Generic gray outline/filled | Transparent surface + structural border with tokenized text states |
| Inputs/forms | Light backgrounds and soft focus | Flat dark inputs using `--bg-base`, `--border-metal`, copper focus state |
| Navigation | Blue active pills and soft backgrounds | Structural shell with border-based hierarchy and copper active indicators |
| Alerts/warnings | Mixed yellows and ad-hoc styles | Tokenized status surfaces using shared patterns (`--copper-oxidized`, `--danger-red`) |
| Charts | Page-local color constants and mixed styles | Shared chart theme using semantic token mappings |
| Overlays/dialogs | Floating card look | Flat metal surface, strong border, no blur/shadow treatment |

## File Inventory and Scope

### Core styling and shell

- `frontend/src/styles/global.css` - primary redesign target (tokens, primitives, page styles).
- `frontend/src/main.ts` - top navigation and workspace shell markup.
- `frontend/src/router.ts` - shell behavior (`has-sidenav`) and route active states.
- `frontend/src/overlay.ts` - loading overlay behavior class/state handling.
- `frontend/index.html` - overlay mount and base app shell entry point.

### Workspace pages

- `frontend/src/pages/workspace.ts`
- `frontend/src/pages/models.ts`
- `frontend/src/pages/simulations.ts`
- `frontend/src/pages/finances.ts`

### Marketing and editorial pages

- `frontend/src/pages/landing.ts`
- `frontend/src/pages/landing-ferntree.ts`
- `frontend/src/pages/blog.ts`
- `frontend/src/pages/blog-post.ts`

### Data and optional follow-up

- `frontend/src/data/blog-posts.ts` (content style coverage check for prose, lists, code blocks).
- `frontend/src/pages/fin-results.ts` (currently placeholder; align if retained).

## Phased Implementation Plan

## Phase 1: Foundation Tokens and Global Reset (Highest Risk)

### Files

- `frontend/src/styles/global.css`

### Steps

1. Replace existing color/token block with Tinkerer's Grid tokens from `docs/ui/design_concept.md`.
2. Standardize global type defaults:
   - one sans-serif font family;
   - global `font-variant-numeric: tabular-nums;`.
3. Remove all shadows and rounding from base primitives:
   - set `box-shadow: none`;
   - set `border-radius: 0`.
4. Apply base surfaces:
   - `html`, `body`, `#app` use `--bg-base` and `--text-primary`.
5. Update base interactive defaults (`a`, `button`, `input`, `select`, `textarea`) to tokenized dark-mode behavior.

### Acceptance Criteria

- Entire app renders in dark mode.
- No rounded corners and no shadows remain.
- Typography is unified and numeric tabular alignment is active globally.

## Phase 2: Shell and Navigation Refactor

### Files

- `frontend/src/main.ts`
- `frontend/src/router.ts`
- `frontend/src/styles/global.css`

### Steps

1. Refactor topnav and sidenav visuals to structural hierarchy:
   - 1px `--border-metal` separation;
   - remove blue active-fill patterns.
2. Define active nav states using copper text/border emphasis.
3. Resolve mobile nav behavior mismatches (current CSS assumptions around hidden labels/icons).
4. Ensure `has-sidenav` route behavior remains functionally intact.

### Acceptance Criteria

- Topnav/sidenav are visually consistent with the new design system.
- Active route indication uses copper accents only.
- Mobile navigation remains usable and legible.

## Phase 3: Primitive Components Consolidation

### Files

- `frontend/src/styles/global.css`
- `frontend/src/overlay.ts`
- `frontend/index.html`

### Steps

1. Normalize card/panel primitives for all pages.
2. Consolidate button variants into tokenized primary/secondary behavior.
3. Normalize form controls and focus treatment across all control types (including date/select).
4. Refactor dialog and overlay to flat panel semantics (no floating visual noise).
5. Replace ad-hoc warning/status styles with tokenized utility classes.

### Acceptance Criteria

- Buttons, forms, dialogs, overlays share one consistent interaction language.
- No page-specific primitive drift remains.

## Phase 4: Workspace Views Migration

### Files

- `frontend/src/pages/workspace.ts`
- `frontend/src/pages/models.ts`
- `frontend/src/pages/simulations.ts`
- `frontend/src/pages/finances.ts`

### Steps

1. Migrate layout containers and card structures to shared primitives.
2. Remove residual inline style fragments in templates and move to class-based styling.
3. Align sidebar patterns between simulations and finances.
4. Standardize status/loading/empty/error blocks under a shared visual pattern.

### Acceptance Criteria

- Workspace flow remains intact with redesigned visual hierarchy.
- Models, simulations, and finances feel like one coherent product surface.

## Phase 5: Landing and Blog Integration

### Files

- `frontend/src/pages/landing.ts`
- `frontend/src/pages/landing-ferntree.ts`
- `frontend/src/pages/blog.ts`
- `frontend/src/pages/blog-post.ts`
- `frontend/src/data/blog-posts.ts` (validation pass)

### Steps

1. Preserve the "DON'T BLACKOUT" hero concept while removing decorative legacy treatments.
2. Update project/blog cards to the same border/surface system used by app pages.
3. Apply editorial typography rhythm for long-form reading on dark backgrounds.
4. Ensure links, code blocks, lists, and headings match tokenized styles.

### Acceptance Criteria

- Marketing/editorial pages match the exact identity of product pages.
- Blog readability remains high across desktop and mobile.

## Phase 6: Chart Theme Unification

### Files

- `frontend/src/pages/simulations.ts`
- `frontend/src/pages/finances.ts`
- `frontend/src/types.ts` (if needed for shared config typing)
- (recommended new file) `frontend/src/chart-theme.ts`

### Steps

1. Extract per-page chart color constants to a shared theme module.
2. Map chart primitives to design tokens:
   - grid lines: `--border-metal`;
   - primary series: `--copper-raw`;
   - generation/success series: `--copper-oxidized`;
   - text/ticks: `--text-secondary`.
3. Standardize legend, tooltip, axis, and center-label typography.
4. Replace inline legend swatch styles with class/token-driven styling.

### Acceptance Criteria

- Simulations and finances charts share one visual grammar.
- Chart contrast and readability are consistent with the global theme.

## Phase 7: Cleanup and Consistency Enforcement

### Files

- `frontend/src/styles/global.css`
- All modified page templates

### Steps

1. Remove unused/legacy classes and duplicate selectors.
2. Remove hardcoded legacy colors from templates and styles where tokens exist.
3. Validate optional placeholder pages (`fin-results`) for parity or de-scope.
4. Final responsive pass for all major route groups.

### Acceptance Criteria

- CSS is lean and maintainable.
- No obsolete visual patterns remain.

## Ordered Execution Sequence (Dependency-Aware)

1. `frontend/src/styles/global.css`
2. `frontend/src/main.ts`
3. `frontend/src/router.ts`
4. `frontend/src/overlay.ts`
5. `frontend/index.html`
6. `frontend/src/pages/workspace.ts`
7. `frontend/src/pages/models.ts`
8. `frontend/src/pages/simulations.ts`
9. `frontend/src/pages/finances.ts`
10. `frontend/src/pages/landing.ts`
11. `frontend/src/pages/landing-ferntree.ts`
12. `frontend/src/pages/blog.ts`
13. `frontend/src/pages/blog-post.ts`
14. `frontend/src/data/blog-posts.ts`
15. `frontend/src/pages/fin-results.ts` (optional)

## QA Checklist

- Geometry:
  - zero rounded corners across all elements;
  - zero box shadows in all interaction states.
- Typography:
  - one global font family;
  - tabular numbers active for financial and simulation data.
- Contrast and readability:
  - primary/secondary text legibility on `--bg-base` and `--bg-surface`.
- Interaction states:
  - hover, focus, active, disabled styles are visible and consistent.
- Navigation:
  - active route indication is clear in desktop and mobile layouts.
- Charts:
  - tokenized palette and readable axes/legends/tooltips.
- Responsive behavior:
  - landing, blog, and workspace pages are usable on mobile breakpoints.

## Migration Pitfalls and Safeguards

- Specificity collisions in a monolithic `global.css`:
  - safeguard: flatten selector depth and consolidate shared primitives early.
- Border noise from over-framing every container:
  - safeguard: use whitespace as hierarchy; reserve borders for structural boundaries.
- Legacy utility/class drift:
  - safeguard: remove or migrate stale classes as each phase completes.
- Inline style residue in TS templates:
  - safeguard: move visual concerns into CSS classes before final QA.
- Divergent chart styles between pages:
  - safeguard: centralize chart theming in one module.

## Future Consistency Guidelines

- All new visual colors must come from design tokens, not ad-hoc hex values.
- Reuse existing primitives before introducing new component classes.
- Keep chart configuration centralized for all current and future webapps.
- Require redesign QA checklist completion for each future UI feature.

## Definition of Done

The redesign is complete when all of the following are true:

1. A single coherent Tinkerer's Grid identity is visible across landing, blog, and workspace.
2. Global typography is unified and tabular numeric alignment is active.
3. No rounded corners or drop shadows remain.
4. Legacy blue-first visual patterns are fully removed or remapped.
5. Charts are tokenized and consistent across simulations and finances.
6. Responsive behavior is stable on core routes.
7. Frontend build passes (`npm run build` in `frontend/`).

# NextJS MVP — Auth Strip Changes

This document records all changes made to produce a minimal, auth-free version of the NextJS frontend. The goal was to remove all authentication, login, contact-form, and user-identity infrastructure while keeping every workspace feature (Models, Simulations, Finances) fully intact.

## Key Design Decision: Anonymous User ID

All 9 backend API endpoints accept `user_id` as a query parameter. Rather than touching the backend, a fixed placeholder `'mvp-user'` is returned by the new `getAnonymousUserId()` function in `helpers.ts`. Every server action that previously called `await getUserID()` (which resolved the real user via NextAuth) now calls the synchronous `getAnonymousUserId()` instead.

---

## Deleted Files

| File | Reason |
|---|---|
| `frontend/auth.ts` | NextAuth main config (MongoDB adapter, Nodemailer provider, Google/GitHub OAuth) |
| `frontend/auth.config.ts` | Edge-safe NextAuth config used by middleware |
| `frontend/middleware.ts` | Route protection via NextAuth session check |
| `frontend/app/api/auth/[...nextauth]/route.ts` | NextAuth catch-all API route handler |
| `frontend/app/login/page.tsx` | Login page |
| `frontend/app/login/sign-in.tsx` | Sign-in form component |
| `frontend/app/login/provider-button.tsx` | OAuth provider button component |
| `frontend/app/login/actions.ts` | Login server actions |
| `frontend/app/components/contact-form.tsx` | Contact/feedback form (used `sendEmail` and `EmailDataSchema`) |
| `frontend/app/components/sidenav/signout-button.tsx` | Sign-out button component |
| `frontend/app/utils/db.ts` | MongoDB client singleton (only used by NextAuth adapter) |

---

## Modified Files

### `frontend/app/page.tsx`
- **Before:** Landing page with marketing content and login CTA.
- **After:** Simple `redirect('/workspace')` — the root now drops straight into the app.

### `frontend/app/workspace/page.tsx`
- **Before:** Imported `getUser` from `next-auth` and `User` type; rendered a user avatar/welcome card alongside the three workflow step cards.
- **After:** Removed all auth imports and the welcome card. Only the three workflow step cards remain.

### `frontend/app/components/sidenav/sidenav.tsx`
- **Before:** Imported `signOut` from `@/auth`; rendered a sign-out `<form>` with an inline `'use server'` action and `<SignoutButton>`.
- **After:** Sign-out form and import removed. Sidenav now just renders the logo, nav links, and ferntree icon.

### `frontend/app/utils/helpers.ts`
- **Removed:** `auth` import from `@/auth`; `Session` and `User` type imports from `next-auth`; `nodemailer` import; `EmailDataSchema` import; `getUser()`, `getUserID()`, `sendEmail()` functions.
- **Added:** `getAnonymousUserId(): string` — returns the fixed string `'mvp-user'`.
- **Kept:** `loadBackendBaseUri()`, `fetchModels()`.

### `frontend/app/utils/definitions.ts`
- **Removed:** `EmailFormData` type and `EmailDataSchema` Zod schema (were only used by the contact form).

### `frontend/app/components/button-actions.ts`
- Replaced `getUserID` import and `await getUserID()` call with `getAnonymousUserId` (synchronous).

### `frontend/app/workspace/models/actions.ts`
- Replaced `getUserID` import and `await getUserID()` call with `getAnonymousUserId`.

### `frontend/app/workspace/finances/actions.ts`
- Replaced `getUserID` import and both `await getUserID()` calls (`submitFinFormData`, `fetchFinFormData`) with `getAnonymousUserId`.

### `frontend/app/workspace/simulations/[model_id]/actions.ts`
- Replaced `getUserID` import and both `await getUserID()` calls (`fetchSimResults`, `fetchPowerData`) with `getAnonymousUserId`.

### `frontend/app/workspace/finances/[model_id]/actions.ts`
- Replaced `getUserID` import and `await getUserID()` call with `getAnonymousUserId`.

### `frontend/next.config.mjs`
- **Removed:** `images.remotePatterns` block (GitHub and Google avatar hostnames — no longer needed without user avatars).

---

## Unchanged Files (workspace functionality)

All workspace pages, components, charts, and forms were left entirely untouched:

- `app/workspace/models/` — all pages and components
- `app/workspace/simulations/` — all pages and components
- `app/workspace/finances/` — all pages and components
- `app/components/base-comps.tsx`
- `app/components/buttons.tsx`
- `app/components/components.tsx`
- `app/components/loading-screen.tsx`
- `app/components/skeletons.tsx`
- `app/components/sidenav/nav-links.tsx`
- `app/components/sidenav/ferntree-logo.tsx`
- `app/utils/definitions.ts` (except `EmailFormData`/`EmailDataSchema` removal)

---

## Verification

`npm run lint` in `frontend/` reports no ESLint warnings or errors after all changes.

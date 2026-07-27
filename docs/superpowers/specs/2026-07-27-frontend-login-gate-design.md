# Frontend Login Gate — Design

## Goal

Add a login page to the React frontend that keeps casual/random visitors out
of the publicly deployed demo. Not a real security boundary — the backend
API stays open regardless of login state (explicit scope decision, see
"Out of scope" below).

## Context

Before this change, the app has zero authentication anywhere:

- No backend auth/session code exists in `src/api` (verified — the only
  `auth`-adjacent grep hit in the codebase was the word "session" in an
  unrelated SQLite comment in `admin.py`).
- No client-side routing exists at all. `App.tsx` is a single page that
  swaps tabs via local `useState`, not React Router or any URL-based
  navigation. A login gate therefore wraps the whole app at the render
  root, not a route.
- No frontend test framework exists (`src/frontend/package.json` has no
  vitest/jest/testing-library) — verification for this feature is manual,
  matching how the recent light-mode-theme work was verified.

## Decisions

- **Threat model:** keep random visitors from landing on the live demo URL
  and poking around, not defend against a motivated attacker. A single
  shared password, not per-user accounts.
- **Enforcement:** frontend-only. The FastAPI backend (Railway) is
  unmodified and continues to accept requests regardless of login state.
  Explicitly chosen over backend-enforced auth to keep scope small, given
  the stated threat model doesn't require real protection.
- **Known limitation, explicitly accepted:** because there's no backend
  check, the correct password ends up as a plain string in the built
  JavaScript bundle (`import.meta.env.VITE_LOGIN_PASSWORD` gets inlined by
  Vite at build time). Anyone who opens browser devtools and reads the
  bundle can find it. This is inherent to any frontend-only gate, not a
  gap in this specific implementation — acceptable given the stated goal.
- **Persistence:** login persists across page reloads and browser
  restarts via `localStorage`, until explicitly cleared. No logout button
  in this version (not requested; clearing `localStorage` manually is
  sufficient if ever needed).
- **Rejected alternative — Vercel Edge Middleware / HTTP Basic Auth:**
  would check the password server-side at Vercel's edge, so it's never
  shipped to the browser, closing the bundle-visibility gap above.
  Rejected because it uses the browser's native unstyled auth popup
  instead of a designed page matching the app, which is what was
  explicitly asked for.

## Architecture

```
main.tsx
  └─ <LoginGate>       (new — src/frontend/src/app/LoginGate.tsx)
       ├─ not authed →  <LoginScreen>   (new — src/frontend/src/app/components/LoginScreen.tsx)
       └─ authed     →  <App />         (existing, unmodified)
```

No React Router involved — `LoginGate` is a plain conditional wrapper
component, consistent with how the rest of this app avoids routing.

### `LoginGate.tsx`

- Holds `authed: boolean` state, initialized from
  `localStorage.getItem("sc_authed") === "true"`.
- If `authed`, renders `children` directly.
- If not, renders `<LoginScreen onSuccess={...} />`.
- `onSuccess` handler: sets `localStorage.setItem("sc_authed", "true")` and
  flips `authed` to `true`.

### `LoginScreen.tsx`

- Reuses the existing wordmark treatment from `App.tsx`'s status bar (the
  `bg-gradient-to-br from-primary to-accent` icon badge + "Supply Chain
  Command Center" text) so the login screen visually matches the rest of
  the app rather than looking like a bolted-on afterthought.
- A password `<input type="password">`, a submit button, and an inline
  error message slot (rendered only after a failed attempt).
- On submit: compares input against `import.meta.env.VITE_LOGIN_PASSWORD`.
  - Match → calls `onSuccess()`.
  - No match → sets local error state ("Incorrect password"), clears the
    input, form stays up. No lockout/rate-limiting — not warranted for
    this threat model.
- **Misconfiguration guard:** if `VITE_LOGIN_PASSWORD` is unset or an
  empty string, the comparison must not let an empty/undefined input
  accidentally match. The check is structured as: only succeed if
  `VITE_LOGIN_PASSWORD` is a non-empty string AND it equals the input —
  never treat "both sides falsy" as a match. This prevents a misconfigured
  Vercel deploy (env var forgotten) from silently shipping with the gate
  wide open.

### `main.tsx`

Wraps the existing `<App />` render with `<LoginGate>`:

```tsx
createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <LoginGate>
      <App />
    </LoginGate>
  </QueryClientProvider>
);
```

## Environment variable

- `VITE_LOGIN_PASSWORD` — new Vite env var.
  - **Vercel:** set under Project Settings → Environment Variables for
    whichever deployment(s) should be gated.
  - **Local dev:** add to a `.env` file under `src/frontend/` (not
    committed to git — matches existing convention for `VITE_API_BASE_URL`
    in `src/frontend/src/app/api/config.ts`).

## Out of scope

- Backend/API-level enforcement (rejected in favor of frontend-only, see
  Decisions above).
- Multiple named user accounts / roles.
- Logout button.
- Password reset / rotation flow.
- Rate-limiting or lockout after failed attempts.

## Testing (manual — no frontend test framework exists)

- `npm run build` passes clean (TypeScript + Vite build).
- Fresh browser / cleared `localStorage` → root shows the login screen,
  not the dashboard.
- Wrong password → inline error shown, app stays gated.
- Correct password → dashboard renders; a subsequent page refresh skips
  the login screen (persistence confirmed).
- Manually clearing `localStorage` in devtools → next load shows the
  login screen again (confirms the flag is actually what gates access,
  not some other bypass).
- Build with `VITE_LOGIN_PASSWORD` unset → confirm login never succeeds
  (misconfiguration guard actually holds, not just assumed).

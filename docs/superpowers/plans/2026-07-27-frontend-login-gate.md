# Frontend Login Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a password-gated login screen in front of the React dashboard, matching the app's visual style, to keep casual visitors off the public deployment.

**Architecture:** A `LoginGate` component wraps the existing `<App />` at the render root in `main.tsx`. It checks `localStorage` for an authed flag; if absent, it renders `LoginScreen` instead of `children`. `LoginScreen` compares the typed password against `import.meta.env.VITE_LOGIN_PASSWORD` client-side — no backend involvement, no React Router (this app has none).

**Tech Stack:** React 18, TypeScript, Vite, Tailwind v4 (via `theme.css` CSS variables — `bg-card`, `text-foreground`, `bg-primary`, etc.), `lucide-react` icons.

## Global Constraints

- Frontend-only enforcement — do not modify anything under `src/api` or `src/agents` (backend stays open, per design spec decision).
- No new npm dependencies — everything needed (`useState`, `lucide-react`'s `Activity` icon) is already installed.
- No test framework exists in `src/frontend` (no vitest/jest) — verification is manual, described as concrete steps below, not automated test code.
- `VITE_LOGIN_PASSWORD` must never match when unset/empty — see Task 2's misconfiguration guard.
- Design reference: `docs/superpowers/specs/2026-07-27-frontend-login-gate-design.md`

---

### Task 1: LoginScreen component

**Files:**
- Create: `src/frontend/src/app/components/LoginScreen.tsx`

**Interfaces:**
- Consumes: nothing from other tasks (self-contained).
- Produces: `LoginScreen({ onSuccess: () => void })` — a React component. `onSuccess` is called exactly once, when the typed password matches `VITE_LOGIN_PASSWORD`. Task 2 depends on this exact prop name and signature.

- [ ] **Step 1: Create the component**

```tsx
// src/frontend/src/app/components/LoginScreen.tsx
import { useState } from "react";
import { Activity } from "lucide-react";

export function LoginScreen({ onSuccess }: { onSuccess: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const expected = import.meta.env.VITE_LOGIN_PASSWORD;
    // Guard: if VITE_LOGIN_PASSWORD is unset/empty, `expected` is falsy,
    // so this never succeeds regardless of what `password` is — prevents
    // a misconfigured deploy (env var forgotten) from silently letting
    // an empty input through.
    if (expected && password === expected) {
      onSuccess();
    } else {
      setError(true);
      setPassword("");
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background">
      <div className="w-[360px] rounded-xl border border-border bg-card p-8 shadow-lg">
        <div className="flex items-center gap-2.5 mb-7">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-gradient-to-br from-primary to-accent shrink-0">
            <Activity size={18} className="text-white" />
          </div>
          <div>
            <div className="text-[13px] font-bold text-foreground leading-tight">Supply Chain</div>
            <div className="text-[10px] text-muted-foreground leading-tight tracking-wide">COMMAND CENTER</div>
          </div>
        </div>

        <h1 className="text-[17px] font-semibold text-foreground mb-1">Sign in</h1>
        <p className="text-xs text-muted-foreground mb-5">Enter the password to access the dashboard.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="login-password" className="block text-xs font-medium text-card-foreground mb-1.5">
            Password
          </label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => { setPassword(e.target.value); setError(false); }}
            placeholder="••••••••"
            className={`w-full px-3 py-2 rounded-lg border bg-input-background text-sm text-foreground mb-1 ${
              error ? "border-destructive" : "border-border"
            }`}
            autoFocus
          />
          <div className="text-[11px] text-destructive min-h-[14px] font-medium mb-3.5">
            {error ? "Incorrect password" : ""}
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
          >
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it type-checks in isolation**

Run: `cd src/frontend && npx tsc --noEmit -p tsconfig.json`
Expected: no errors referencing `LoginScreen.tsx` (errors in unrelated files, if any, are pre-existing — not this task's concern).

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/app/components/LoginScreen.tsx
git commit -m "Add LoginScreen component for the frontend login gate"
```

---

### Task 2: LoginGate wrapper + wire into main.tsx

**Files:**
- Create: `src/frontend/src/app/LoginGate.tsx`
- Modify: `src/frontend/src/main.tsx`

**Interfaces:**
- Consumes: `LoginScreen` from Task 1 — `LoginScreen({ onSuccess: () => void })`.
- Produces: `LoginGate({ children: React.ReactNode })` — a React component. Nothing later depends on internals beyond this signature.

- [ ] **Step 1: Create LoginGate**

```tsx
// src/frontend/src/app/LoginGate.tsx
import { useState, type ReactNode } from "react";
import { LoginScreen } from "./components/LoginScreen";

const STORAGE_KEY = "sc_authed";

export function LoginGate({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState<boolean>(
    () => localStorage.getItem(STORAGE_KEY) === "true"
  );

  if (!authed) {
    return (
      <LoginScreen
        onSuccess={() => {
          localStorage.setItem(STORAGE_KEY, "true");
          setAuthed(true);
        }}
      />
    );
  }

  return <>{children}</>;
}
```

- [ ] **Step 2: Wire it into main.tsx**

Current content of `src/frontend/src/main.tsx`:

```tsx
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./app/App";
import "./styles/index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 10_000 } },
});

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
```

Replace with:

```tsx
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./app/App";
import { LoginGate } from "./app/LoginGate";
import "./styles/index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 10_000 } },
});

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <LoginGate>
      <App />
    </LoginGate>
  </QueryClientProvider>
);
```

- [ ] **Step 3: Add VITE_LOGIN_PASSWORD to the local env example**

Append to `src/frontend/.env.local.example`:

```
# Password for the login gate (src/app/LoginGate.tsx). Required — if
# unset, the login screen never succeeds (fail-safe by design).
# VITE_LOGIN_PASSWORD=changeme
```

- [ ] **Step 4: Create your own local .env.local with a real value**

```bash
cd src/frontend
echo "VITE_LOGIN_PASSWORD=changeme" > .env.local
```

(`.env.local` is already gitignored — confirmed in `.gitignore:52` — so this never gets committed.)

- [ ] **Step 5: Run the production build**

Run: `cd src/frontend && npm run build`
Expected: `✓ built in <N>s` with no TypeScript errors.

- [ ] **Step 6: Commit**

```bash
git add src/frontend/src/app/LoginGate.tsx src/frontend/src/main.tsx src/frontend/.env.local.example
git commit -m "Wire LoginGate in front of the app in main.tsx"
```

(`.env.local` itself is gitignored and intentionally not committed.)

---

### Task 3: Manual verification

**Files:** none (no code changes — this task is entirely verification steps).

**Interfaces:** none.

- [ ] **Step 1: Start the dev server**

Run: `cd src/frontend && npm run dev`
Expected: Vite prints a `Local: http://localhost:5173/` URL.

- [ ] **Step 2: Verify the gate blocks a fresh browser**

Open `http://localhost:5173/` in an incognito/private window (guarantees empty `localStorage`).
Expected: the login screen renders — wordmark, "Sign in" heading, password field, submit button. The dashboard must NOT be visible.

- [ ] **Step 3: Verify wrong password is rejected**

Type any incorrect string into the password field and submit.
Expected: "Incorrect password" appears below the field, the input clears, the dashboard still does not render.

- [ ] **Step 4: Verify correct password succeeds and persists**

Type the value you set in `.env.local` (`changeme`, unless you changed it) and submit.
Expected: the dashboard renders immediately. Refresh the page (`Cmd+R`).
Expected: the dashboard renders again immediately, without showing the login screen — confirms `localStorage` persistence is working.

- [ ] **Step 5: Verify clearing localStorage re-locks the app**

Open browser devtools → Application/Storage tab → clear `localStorage` for `localhost:5173` (or run `localStorage.clear()` in the console). Refresh.
Expected: the login screen appears again — confirms the `localStorage` flag is what's actually gating access, not some other bypass.

- [ ] **Step 6: Verify the misconfiguration guard**

Stop the dev server. Temporarily rename `.env.local` (e.g. `mv .env.local .env.local.bak`). Restart: `npm run dev`. In an incognito window, try submitting the login form with any password, including an empty one.
Expected: login never succeeds — "Incorrect password" every time, dashboard never renders. This confirms `VITE_LOGIN_PASSWORD` being unset fails safe rather than silently letting anything through.

Restore your env file afterward: `mv .env.local.bak .env.local`.

- [ ] **Step 7: Report results**

No commit for this task (verification only). If any step doesn't match its expected result, report which step and what actually happened — that's a bug in Task 1 or 2 to fix before this plan is considered done.

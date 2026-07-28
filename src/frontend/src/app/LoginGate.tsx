import { useState, type ReactNode } from "react";
import { LoginScreen } from "./components/LoginScreen";

const STORAGE_KEY = "sc_authed";

// Reload rather than lifting state up: LoginGate only checks localStorage
// on initial mount, so a full reload is the simplest way to force the
// already-mounted <App /> tree back through the gate without wiring
// context/props through every layer just for this one action.
export function logout() {
  localStorage.removeItem(STORAGE_KEY);
  window.location.reload();
}

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

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

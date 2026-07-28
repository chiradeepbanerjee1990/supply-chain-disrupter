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

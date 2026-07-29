/**
 * Shared bordered-card wrapper — the `<Panel title rightContent?>` contract
 * documented in design.md §1.6 but never implemented; every screen was
 * inlining its own `rounded-lg p-4 bg-card border border-border` div
 * (some `rounded-lg`, some `rounded-panel` — drifted). Centralizes radius,
 * border, background, and the light-mode elevation shadow (design.md §1.4)
 * in one place so future styling changes don't require touching all 8 tabs.
 */
import type { ReactNode } from "react";

export function Panel({
  title,
  rightContent,
  className = "",
  children,
}: {
  title?: ReactNode;
  rightContent?: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={`rounded-panel bg-card border border-border shadow-panel p-4 ${className}`}
    >
      {(title || rightContent) && (
        <div className="flex items-center gap-2 mb-3">
          {title && (
            <div className="text-xs font-semibold text-muted-foreground">{title}</div>
          )}
          {rightContent && <div className="ml-auto">{rightContent}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

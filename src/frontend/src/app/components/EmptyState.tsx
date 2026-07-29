/**
 * Shared no-data placeholder — replaces the plain gray "No data yet" /
 * "Not yet built this session" strings previously scattered across panels
 * with no visual design (Mitigation India Sourcing, Admin DB status cards,
 * Forecast Monte Carlo, Live Feed pre-data states).
 */
import type { LucideIcon } from "lucide-react";

export function EmptyState({
  icon: Icon,
  title,
  subtitle,
}: {
  icon: LucideIcon;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-8 px-4">
      <Icon size={22} className="text-muted-foreground/50 mb-2" />
      <div className="text-xs font-medium text-muted-foreground">{title}</div>
      {subtitle && <div className="text-[10px] text-muted-foreground/70 mt-1 max-w-xs">{subtitle}</div>}
    </div>
  );
}

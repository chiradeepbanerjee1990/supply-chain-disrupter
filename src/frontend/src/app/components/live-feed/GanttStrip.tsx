/**
 * Screen 1 (Live Feed) — Pipeline Timeline Gantt strip, below the 3-column grid.
 * Real data source: GET /api/live-feed/gantt?run_id=. L2-L7 bars are real
 * once a run_id is active (fetch_run_gantt() reads agent_execution_log's
 * duration_ms per agent); without an active run_id the endpoint falls back
 * to Day-1 fixture stub bars (source="stub"), rendered dimmed so the
 * fallback stays visible.
 */
import { RefreshCw } from "lucide-react";
import { useLiveFeedGantt } from "../../hooks/useLiveFeed";
import { Panel } from "../Panel";

// Evenly spaced tick marks across [0, totalDuration] — 5 ticks reads clean
// at the strip's typical width without crowding short (<10s) runs.
const TICK_COUNT = 5;

export function GanttStrip({ runId }: { runId?: string }) {
  const { data, isLoading, isError } = useLiveFeedGantt(runId);
  const bars = data?.bars ?? [];
  const totalDuration = bars.length > 0 ? Math.max(...bars.map((b) => b.start + b.dur)) : 0;
  const waitingForRun = Boolean(runId) && bars.length > 0 && bars.every((b) => b.source === "stub");
  const ticks = totalDuration > 0
    ? Array.from({ length: TICK_COUNT + 1 }, (_, i) => (totalDuration / TICK_COUNT) * i)
    : [];

  return (
    <div className="px-3 pb-3 shrink-0">
      <Panel className="!p-3">
        <div className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          Pipeline Timeline — end-to-end: {totalDuration.toFixed(1)}s
        </div>
        {isLoading && (
          <div className="text-xs text-muted-foreground">Loading timeline…</div>
        )}
        {isError && (
          <div className="text-xs text-risk-critical">Could not load Gantt data.</div>
        )}
        {waitingForRun && (
          <div className="flex items-center gap-1.5 text-[10px] text-status-running mb-1.5">
            <RefreshCw size={9} className="animate-spin shrink-0" />
            Pipeline running — timeline will populate as agents complete.
          </div>
        )}
        <div className="space-y-1">
          {bars.map((row) => (
            <div
              key={row.id}
              className={`flex items-center gap-2 transition-opacity duration-300 motion-reduce:transition-none ${row.source === "stub" ? "opacity-60" : ""}`}
            >
              <span className="text-[9px] font-mono text-muted-foreground w-4 shrink-0">
                {row.id}
              </span>
              <div className="flex-1 relative h-3.5 rounded overflow-hidden bg-background">
                {ticks.map((t) => (
                  <div
                    key={t}
                    className="absolute top-0 h-full w-px bg-border/60"
                    style={{ left: `${(t / totalDuration) * 100}%` }}
                  />
                ))}
                <div
                  className="absolute top-0 h-full rounded flex items-center px-1 text-[9px] font-mono transition-all duration-300 ease-out motion-reduce:transition-none"
                  style={{
                    left: totalDuration > 0 ? `${(row.start / totalDuration) * 100}%` : "0%",
                    width: totalDuration > 0 ? `${(row.dur / totalDuration) * 100}%` : "0%",
                    background: row.color + "28",
                    border: `1px solid ${row.color}44`,
                    color: row.color,
                    minWidth: 28,
                  }}
                >
                  {row.dur.toFixed(1)}s
                </div>
              </div>
              {row.source === "stub" && (
                <span className="text-[9px] text-muted-foreground italic shrink-0">stub</span>
              )}
            </div>
          ))}
          {ticks.length > 0 && (
            <div className="flex items-center gap-2 pt-1">
              <span className="w-4 shrink-0" />
              <div className="flex-1 relative h-3">
                {ticks.map((t) => (
                  <span
                    key={t}
                    className="absolute top-0 text-[8px] font-mono text-muted-foreground/70 -translate-x-1/2"
                    style={{ left: `${(t / totalDuration) * 100}%` }}
                  >
                    {t.toFixed(0)}s
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </Panel>
    </div>
  );
}

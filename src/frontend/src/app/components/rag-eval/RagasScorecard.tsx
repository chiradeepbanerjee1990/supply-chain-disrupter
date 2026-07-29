/**
 * Screen 6 4-tile RAGAS scorecard (Faithfulness / Answer Relevance /
 * Context Precision / Context Recall). Owns its own query via
 * useRagScorecard — GET /api/rag/scorecard, still fixture JSON in this
 * cut. Layout ported from _reference/App.mockup.tsx:948-967, pass/fail
 * coloring switched from inline hex to the riskColors tokens (risk-low /
 * risk-critical) per design.md.
 */
import { useEffect, useState } from "react";
import { useRagScorecard } from "../../hooks/useRagEval";
import { useAnimateOnChange } from "../../utils/animation";
import { HeroStat } from "../HeroStat";

const STAGGER_MS = 100;

export function RagasScorecard() {
  const { data, isLoading, isError } = useRagScorecard();
  const shouldAnimate = useAnimateOnChange(data ? "loaded" : null);
  // Two-phase mount: render bars at 0 width first, then flip to their real
  // width so the CSS transition actually has something to animate from.
  const [grown, setGrown] = useState(!shouldAnimate);
  useEffect(() => {
    if (!data || !shouldAnimate) return;
    const raf = requestAnimationFrame(() => setGrown(true));
    return () => cancelAnimationFrame(raf);
  }, [data, shouldAnimate]);

  if (isLoading) {
    return <div className="text-xs text-muted-foreground p-2">Loading RAGAS scorecard…</div>;
  }

  if (isError || !data) {
    return <div className="text-xs text-risk-critical p-2">Could not load RAGAS scorecard.</div>;
  }

  return (
    <div className="grid grid-cols-4 gap-3">
      {data.map((tile, i) => {
        const borderClass = tile.passed ? "border-risk-low/30" : "border-risk-critical/30";
        const barClass = tile.passed ? "bg-risk-low" : "bg-risk-critical";
        return (
          <div key={tile.metric} className={`rounded-panel shadow-panel p-4 bg-card border ${borderClass}`}>
            <HeroStat
              value={tile.score.toFixed(2)}
              label={tile.metric}
              threshold={`threshold: ${tile.threshold}`}
              status={tile.passed ? "pass" : "fail"}
            />
            <div className="h-1.5 rounded-full overflow-hidden mt-2 bg-border">
              <div
                className={`h-full rounded-full ${barClass} transition-[width] duration-[600ms] ease-out motion-reduce:transition-none`}
                style={{
                  width: grown ? `${tile.score * 100}%` : "0%",
                  transitionDelay: `${i * STAGGER_MS}ms`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

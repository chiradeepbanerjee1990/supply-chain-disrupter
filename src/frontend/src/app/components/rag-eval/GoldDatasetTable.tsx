/**
 * Screen 6 chunk-grounded gold-dataset table. Owns its own query via
 * useGoldDataset — GET /api/rag/gold-dataset. Ground-truth strings are
 * short enough for a truncate+title-attr pattern rather than Screen 5's
 * inspector-style row expansion. query_style badge distinguishes the
 * agent's internal RAG query pattern from natural-language evaluator
 * questions; match/no-match icon colored via riskColors. Layout ported
 * from _reference/App.mockup.tsx:1032-1050.
 */
import { useState } from "react";
import { AlertCircle, CheckCircle } from "lucide-react";
import { useGoldDataset } from "../../hooks/useRagEval";
import { useAnimateOnChange } from "../../utils/animation";
import { Panel } from "../Panel";

const STAGGER_MS = 60;
const STAGGER_CAP = 8;
// Answers longer than this render truncated with a show-more toggle rather
// than always inline — long ground-truth strings were making every row a
// dense, hard-to-scan paragraph.
const ANSWER_TRUNCATE_LENGTH = 120;

export function GoldDatasetTable() {
  const { data, isLoading, isError } = useGoldDataset();
  const shouldAnimate = useAnimateOnChange(data ? "loaded" : null);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const toggleExpanded = (i: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  if (isLoading) {
    return <div className="text-xs text-muted-foreground p-2">Loading gold dataset…</div>;
  }

  if (isError || !data) {
    return <div className="text-xs text-risk-critical p-2">Could not load gold dataset.</div>;
  }

  return (
    <Panel title="Gold Dataset — Chunk-Grounded QA Test Set">
      <div className="space-y-1.5">
        {data.map((row, i) => {
          const isLong = row.ground_truth.length > ANSWER_TRUNCATE_LENGTH;
          const isExpanded = expanded.has(i);
          const answerText = isLong && !isExpanded
            ? `${row.ground_truth.slice(0, ANSWER_TRUNCATE_LENGTH)}…`
            : row.ground_truth;
          return (
            <div
              key={i}
              className={`flex gap-3 p-2.5 rounded text-[10px] bg-background border border-border${
                shouldAnimate && i < STAGGER_CAP ? " animate-fade-stagger motion-reduce:animate-none" : ""
              }`}
              style={shouldAnimate && i < STAGGER_CAP ? { animationDelay: `${i * STAGGER_MS}ms` } : undefined}
            >
              <div className={`mt-0.5 shrink-0 font-mono font-bold ${row.match ? "text-risk-low" : "text-risk-critical"}`}>
                {row.match ? "✓" : "✗"}
              </div>
              <div className="min-w-0">
                <div className="mb-1 truncate" title={row.question}>
                  <span className="text-muted-foreground font-medium">Q:</span>{" "}
                  <span className="text-foreground font-medium">{row.question}</span>
                </div>
                <div className="font-mono text-muted-foreground leading-relaxed">
                  <span className="font-sans font-normal">A:</span> {answerText}
                  {isLong && (
                    <button
                      onClick={() => toggleExpanded(i)}
                      className="ml-1.5 font-sans font-medium text-accent hover:underline"
                    >
                      {isExpanded ? "show less" : "show more"}
                    </button>
                  )}
                </div>
              </div>
              <span
                className={`ml-auto shrink-0 text-[9px] font-mono px-1.5 py-0.5 rounded h-fit ${
                  row.query_style === "agent_pattern"
                    ? "text-accent bg-accent/10"
                    : "text-muted-strong bg-secondary"
                }`}
              >
                {row.query_style}
              </span>
              <div className="shrink-0 flex items-center">
                {row.match ? (
                  <CheckCircle size={12} className="text-risk-low" />
                ) : (
                  <AlertCircle size={12} className="text-risk-critical" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

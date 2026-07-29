/**
 * Shared headline-metric tile — extracted from Screen 6's RAGAS scorecard
 * (RagasScorecard.tsx), the best-executed "one big number" pattern already
 * in the app: large mono numeral, muted uppercase label, optional
 * threshold caption + pass/fail color. Reused wherever a screen renders a
 * single headline metric as plain text instead of this treatment (Mitigation
 * Cost Delta, Forecast MAPE/Stockout, Risk Classification composite score,
 * Admin stat grid at `size="sm"`).
 */
const SIZE_CLASS: Record<"sm" | "md" | "lg", string> = {
  sm: "text-lg",
  md: "text-2xl",
  lg: "text-3xl",
};

const STATUS_COLOR: Record<"pass" | "fail" | "neutral", string> = {
  pass: "text-risk-low",
  fail: "text-risk-critical",
  neutral: "text-foreground",
};

export function HeroStat({
  value,
  label,
  threshold,
  status = "neutral",
  size = "lg",
}: {
  value: string;
  label: string;
  threshold?: string;
  status?: "pass" | "fail" | "neutral";
  size?: "sm" | "md" | "lg";
}) {
  return (
    <div>
      <div className="text-[9px] text-muted-foreground uppercase tracking-wider mb-1">{label}</div>
      <div className={`font-mono font-bold ${SIZE_CLASS[size]} ${STATUS_COLOR[status]}`}>{value}</div>
      {threshold && (
        <div className="flex items-center justify-between text-[9px] mt-1">
          <span className="text-muted-foreground font-mono">{threshold}</span>
          {status !== "neutral" && (
            <span className={`font-mono ${STATUS_COLOR[status]}`}>
              {status === "pass" ? "✓ Pass" : "✗ Fail"}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

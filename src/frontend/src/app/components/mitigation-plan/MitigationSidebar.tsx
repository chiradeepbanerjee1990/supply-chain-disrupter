/**
 * Screen 4 mitigation sidebar sections for India sourcing, Slack preview,
 * and cost delta. It renders only real values from the API and shows an
 * explicit empty state when the backend has no persisted content yet.
 */
import { PackageSearch } from "lucide-react";
import type { MitigationResponse } from "../../types/mitigation";
import { EmptyState } from "../EmptyState";
import { HeroStat } from "../HeroStat";

export function MitigationSidebar({ data }: { data: MitigationResponse }) {
  // No numeric cost-delta severity threshold exists in the API response —
  // reuse the urgency this same run already assigned (IMMEDIATE/HIGH read
  // as elevated cost impact) rather than inventing an unbacked $ cutoff.
  const costStatus = data.urgency === "IMMEDIATE" || data.urgency === "HIGH" ? "fail" : "neutral";

  return (
    <aside className="space-y-3">
      <section className="rounded-panel shadow-panel p-4 bg-card border border-border">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">India Sourcing Recommendations</div>
        <div className="mt-3 space-y-2">
          {data.india_sourcing_recommendations.length > 0 ? (
            data.india_sourcing_recommendations.map((item) => (
              <div key={item} className="rounded-btn border border-border bg-background px-3 py-2 text-xs text-foreground">
                {item}
              </div>
            ))
          ) : (
            <EmptyState
              icon={PackageSearch}
              title="No India sourcing recommendation"
              subtitle="No persisted india sourcing recommendation for this run."
            />
          )}
        </div>
      </section>

      <section className="rounded-panel shadow-panel p-4 bg-card border border-border">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Slack Message Preview</div>
        <div className="mt-3 rounded-btn border border-border bg-background px-3 py-2 text-xs leading-5 text-foreground whitespace-pre-wrap font-mono">
          {data.slack_alert_fired && data.slack_preview ? (
            data.slack_preview
          ) : (
            <span className="font-sans text-muted-foreground">No alert fired for this run.</span>
          )}
        </div>
      </section>

      <section className="rounded-panel shadow-panel p-4 bg-card border border-border">
        <div className="mt-3 flex items-end justify-between gap-3 rounded-btn border border-border bg-background px-3 py-2">
          <HeroStat
            size="md"
            label="Cost Delta"
            status={costStatus}
            value={data.cost_delta_usd != null ? `$${data.cost_delta_usd.toLocaleString()}` : "—"}
          />
          <div className="text-[10px] text-muted-foreground">{data.cost_delta ?? "No persisted cost delta for this run."}</div>
        </div>
      </section>
    </aside>
  );
}

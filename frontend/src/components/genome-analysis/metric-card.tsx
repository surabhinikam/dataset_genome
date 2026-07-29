"use client";

/**
 * components/genome-analysis/metric-card.tsx — Metric Card Component.
 *
 * Renders individual profiler scores, icons, and status summaries in Google Stitch style.
 */

interface MetricCardProps {
  title: string;
  score: number;
  subtitle: string;
  icon: React.ReactNode;
  accentColor: string;
  details: string[];
}

export default function MetricCard({
  title,
  score,
  subtitle,
  icon,
  accentColor,
  details,
}: MetricCardProps) {
  const getStatusPill = (val: number) => {
    if (val >= 85) return { label: "Pass", color: "bg-emerald-500/10 text-emerald-300 border-emerald-500/20" };
    if (val >= 70) return { label: "Fair", color: "bg-indigo-500/10 text-indigo-300 border-indigo-500/20" };
    if (val >= 50) return { label: "Warning", color: "bg-amber-500/10 text-amber-300 border-amber-500/20" };
    return { label: "Critical", color: "bg-red-500/10 text-red-300 border-red-500/20" };
  };

  const status = getStatusPill(score);

  return (
    <div className="group relative flex flex-col justify-between rounded-2xl border border-white/8 bg-white/[0.03] p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:border-white/20 hover:bg-white/[0.05] hover:shadow-xl">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 ${accentColor}`}>
            {icon}
          </div>
          <span className={`rounded-full border px-2.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase ${status.color}`}>
            {status.label}
          </span>
        </div>

        {/* Title & Score */}
        <div className="mb-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-white/50">{title}</h4>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold tracking-tight text-white">{score.toFixed(1)}%</span>
            <span className="text-xs text-white/40">{subtitle}</span>
          </div>
        </div>

        {/* Details list */}
        <div className="mt-3 space-y-1.5 border-t border-white/5 pt-3">
          {details.map((detail, idx) => (
            <div key={idx} className="flex items-center gap-2 text-xs text-white/60">
              <span className="h-1 w-1 rounded-full bg-violet-400/60" />
              <span className="truncate">{detail}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

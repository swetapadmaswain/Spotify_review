import { InsightSummary } from '../api/client';

interface Props {
  data: InsightSummary | null;
}

const cards = [
  { key: 'pattern_count', label: 'Patterns', color: 'text-spotify' },
  { key: 'segment_count', label: 'Segments', color: 'text-blue-400' },
  { key: 'root_cause_count', label: 'Root Causes', color: 'text-orange-400' },
  { key: 'unmet_need_count', label: 'Unmet Needs', color: 'text-pink-400' },
] as const;

export default function SummaryCards({ data }: Props) {
  if (!data) return <div className="text-muted">Loading summary...</div>;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map(({ key, label, color }) => (
        <div key={key} className="bg-card rounded-xl p-5 border border-white/10">
          <p className="text-muted text-sm">{label}</p>
          <p className={`text-3xl font-bold mt-1 ${color}`}>{data[key]}</p>
        </div>
      ))}
    </div>
  );
}

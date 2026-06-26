import { InsightSummary } from '../api/client';
import Card from './ui/Card';

interface Props {
  data: InsightSummary | null;
  onCardClick?: (key: string) => void;
  activeKey?: string | null;
}

const cards = [
  { key: 'pattern_count', label: 'Patterns Detected', desc: 'Temporal, thematic & cross-platform', color: 'text-spotify', tab: 'patterns' },
  { key: 'segment_count', label: 'User Segments', desc: 'Behavior & platform clusters', color: 'text-blue-400', tab: 'segments' },
  { key: 'root_cause_count', label: 'Root Causes', desc: 'Causal chain analyses', color: 'text-orange-400', tab: 'insights' },
  { key: 'unmet_need_count', label: 'Unmet Needs', desc: 'Feature gaps & requests', color: 'text-pink-400', tab: 'insights' },
] as const;

export default function SummaryCards({ data, onCardClick, activeKey }: Props) {
  if (!data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse h-28 bg-white/5">
            <div />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map(({ key, label, desc, color, tab }) => (
        <Card
          key={key}
          onClick={() => onCardClick?.(tab)}
          className={activeKey === tab ? 'border-spotify/50 ring-1 ring-spotify/30' : ''}
        >
          <p className="text-muted text-xs uppercase tracking-wide">{label}</p>
          <p className={`text-4xl font-extrabold mt-1 ${color}`}>{data[key]}</p>
          <p className="text-xs text-muted mt-2">{desc}</p>
          <p className="text-xs text-spotify mt-2 opacity-0 group-hover:opacity-100">Click to explore →</p>
        </Card>
      ))}
    </div>
  );
}

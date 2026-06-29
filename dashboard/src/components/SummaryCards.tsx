import { InsightSummary } from '../api/client';
import Card from './ui/Card';

interface Props {
  data: InsightSummary | null;
  onCardClick?: (key: string) => void;
  activeKey?: string | null;
}

const cards = [
  { key: 'total_reviews', label: 'Total Reviews', desc: 'Collected from all sources', detail: 'Reviews from App Store, Play Store, Reddit, and forums', color: 'text-green-400', tab: 'executive' },
  { key: 'pattern_count', label: 'Patterns Detected', desc: 'Temporal, thematic & cross-platform', detail: 'Recurring behaviors and themes in user feedback', color: 'text-spotify', tab: 'patterns' },
  { key: 'segment_count', label: 'User Segments', desc: 'Behavior & platform clusters', detail: 'Groups of users with similar characteristics', color: 'text-blue-400', tab: 'segments' },
  { key: 'root_cause_count', label: 'Root Causes', desc: 'Causal chain analyses', detail: 'Underlying reasons for user issues', color: 'text-orange-400', tab: 'insights' },
  { key: 'unmet_need_count', label: 'Unmet Needs', desc: 'Feature gaps & requests', detail: 'Features users want but don\'t have', color: 'text-pink-400', tab: 'insights' },
] as const;

export default function SummaryCards({ data, onCardClick, activeKey }: Props) {
  if (!data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Card key={i} className="animate-pulse h-28 bg-white/5">
            <div />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {cards.map(({ key, label, desc, detail, color, tab }) => (
        <Card
          key={key}
          onClick={() => onCardClick?.(tab)}
          className={`cursor-pointer transition-all hover:border-spotify/40 ${activeKey === tab ? 'border-spotify/50 ring-1 ring-spotify/30' : ''}`}
        >
          <p className="text-muted text-xs uppercase tracking-wide">{label}</p>
          <p className={`text-4xl font-extrabold mt-1 ${color}`}>{data[key]}</p>
          <p className="text-xs text-muted mt-2">{desc}</p>
          <p className="text-xs text-spotify mt-1 opacity-0 group-hover:opacity-100 transition-opacity">Click to explore →</p>
        </Card>
      ))}
    </div>
  );
}

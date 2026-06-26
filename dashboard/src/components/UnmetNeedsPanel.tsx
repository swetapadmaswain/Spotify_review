import { UnmetNeed } from '../api/client';
import Card from './ui/Card';
import Badge from './ui/Badge';

interface Props {
  data: UnmetNeed[];
}

export default function UnmetNeedsPanel({ data }: Props) {
  const sorted = [...data].sort((a, b) => b.priority_score - a.priority_score);

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-4">Prioritized Unmet Needs</h3>
      {sorted.length === 0 ? (
        <p className="text-muted text-sm">No unmet needs detected.</p>
      ) : (
        <div className="space-y-3">
          {sorted.map((need, i) => (
            <div
              key={need.id}
              className="flex gap-4 p-4 rounded-xl bg-black/20 border border-white/5 hover:border-spotify/20 transition-colors"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-spotify/10 flex items-center justify-center text-spotify font-bold">
                {i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">{need.need_description}</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge label={need.need_category} variant="info" />
                  <Badge
                    label={`${Math.round(need.priority_score * 100)}% priority`}
                    variant={need.priority_score >= 0.8 ? 'danger' : need.priority_score >= 0.6 ? 'warning' : 'default'}
                  />
                  <Badge label={`${need.strategic_impact} impact`} variant={
                    need.strategic_impact === 'high' ? 'danger' : 'warning'
                  } />
                  {need.request_count > 0 && (
                    <Badge label={`${need.request_count} requests`} variant="default" />
                  )}
                </div>
                <div className="mt-2 h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-spotify rounded-full transition-all"
                    style={{ width: `${need.priority_score * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

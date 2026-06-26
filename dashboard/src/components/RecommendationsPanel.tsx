import { useState } from 'react';
import { Recommendation, RoadmapItem } from '../api/client';
import Card from './ui/Card';
import Badge from './ui/Badge';
import Button from './ui/Button';

interface Props {
  recommendations: Recommendation[];
  roadmap: RoadmapItem[];
}

const priorityVariant: Record<string, 'danger' | 'warning' | 'success'> = {
  high: 'danger',
  medium: 'warning',
  low: 'success',
};

export default function RecommendationsPanel({ recommendations, roadmap }: Props) {
  const [expanded, setExpanded] = useState<number | null>(0);
  const [view, setView] = useState<'recs' | 'roadmap'>('recs');

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex gap-2">
        <Button variant={view === 'recs' ? 'primary' : 'ghost'} onClick={() => setView('recs')}>
          Recommendations ({recommendations.length})
        </Button>
        <Button variant={view === 'roadmap' ? 'primary' : 'ghost'} onClick={() => setView('roadmap')}>
          Product Roadmap ({roadmap.length})
        </Button>
      </div>

      {view === 'recs' && (
        <div className="space-y-3">
          {recommendations.length === 0 ? (
            <Card><p className="text-muted text-sm">No recommendations yet.</p></Card>
          ) : (
            recommendations.map((rec, i) => (
              <Card key={i} className={expanded === i ? 'border-spotify/30' : ''}>
                <button
                  className="w-full text-left"
                  onClick={() => setExpanded(expanded === i ? null : i)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h4 className="font-semibold">{rec.title}</h4>
                      <div className="flex flex-wrap gap-2 mt-2">
                        <Badge label={rec.priority} variant={priorityVariant[rec.priority] || 'default'} />
                        <Badge label={rec.category} variant="info" />
                        <Badge label={`${rec.expected_impact} impact`} variant="warning" />
                      </div>
                    </div>
                    <span className="text-muted">{expanded === i ? '▲' : '▼'}</span>
                  </div>
                </button>
                {expanded === i && (
                  <div className="mt-4 pt-4 border-t border-white/10 space-y-3 animate-fade-in">
                    <p className="text-sm text-white/80">{rec.description}</p>
                    <div className="grid sm:grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-white/5">
                        <p className="text-xs text-muted">Implementation Effort</p>
                        <p className="font-semibold capitalize">{rec.complexity}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5">
                        <p className="text-xs text-muted">Discovery Impact</p>
                        <p className="font-semibold capitalize">{rec.expected_impact}</p>
                      </div>
                    </div>
                    {rec.success_metrics && rec.success_metrics.length > 0 && (
                      <div>
                        <p className="text-xs text-muted mb-2">Success Metrics</p>
                        <div className="flex flex-wrap gap-2">
                          {rec.success_metrics.map((m, j) => (
                            <Badge key={j} label={m} variant="success" />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            ))
          )}
        </div>
      )}

      {view === 'roadmap' && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => {
            const items = roadmap.filter((r) => r.quarter === q);
            return (
              <Card key={q}>
                <h4 className="font-bold text-spotify mb-3">{q}</h4>
                {items.length === 0 ? (
                  <p className="text-xs text-muted">No items</p>
                ) : (
                  <ul className="space-y-2">
                    {items.map((item) => (
                      <li key={item.id} className="p-2 rounded-lg bg-white/5 text-sm">
                        <p className="font-medium">{item.title}</p>
                        <Badge label={item.priority} variant={priorityVariant[item.priority] || 'default'} />
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

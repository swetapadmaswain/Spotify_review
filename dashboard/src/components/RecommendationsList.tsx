import { Recommendation } from '../api/client';

interface Props {
  data: Recommendation[];
}

const priorityColor: Record<string, string> = {
  high: 'bg-red-500/20 text-red-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  low: 'bg-green-500/20 text-green-400',
};

export default function RecommendationsList({ data }: Props) {
  return (
    <div className="bg-card rounded-xl p-5 border border-white/10">
      <h3 className="text-lg font-semibold mb-4">Strategic Recommendations</h3>
      {data.length === 0 ? (
        <p className="text-muted">No recommendations yet.</p>
      ) : (
        <div className="space-y-4">
          {data.map((rec, i) => (
            <div key={i} className="border border-white/10 rounded-lg p-4">
              <div className="flex items-center justify-between gap-2 mb-2">
                <h4 className="font-medium">{rec.title}</h4>
                <span className={`text-xs px-2 py-1 rounded-full ${priorityColor[rec.priority] || ''}`}>
                  {rec.priority}
                </span>
              </div>
              <p className="text-sm text-muted mb-2">{rec.description}</p>
              <div className="flex gap-3 text-xs text-muted">
                <span>{rec.category}</span>
                <span>Impact: {rec.expected_impact}</span>
                <span>Effort: {rec.complexity}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

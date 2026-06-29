import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import Card from './ui/Card';

interface Props {
  data: { sentiment: string; count: number }[];
}

const COLORS: Record<string, string> = {
  positive: '#1DB954',
  negative: '#e91429',
  neutral: '#b3b3b3',
};

const SENTIMENT_EXPLANATIONS: Record<string, string> = {
  positive: 'Users are happy with the experience',
  negative: 'Users are experiencing issues or frustration',
  neutral: 'Users have mixed feelings or no strong opinion',
};

export default function SentimentDistribution({ data }: Props) {
  const total = data.reduce((s, d) => s + d.count, 0);
  const maxReviews = 10000;

  return (
    <Card>
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-1">📊 Sentiment Breakdown</h3>
        <p className="text-xs text-muted">
          Analysis of {maxReviews.toLocaleString()} reviews from the last 30 days
        </p>
        <p className="text-xs text-muted mt-1">
          ({total.toLocaleString()} reviews analyzed with sentiment data)
        </p>
      </div>
      {data.length === 0 ? (
        <p className="text-muted text-sm">No sentiment data available</p>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={data}
                dataKey="count"
                nameKey="sentiment"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={75}
                paddingAngle={3}
              >
                {data.map((entry) => (
                  <Cell key={entry.sentiment} fill={COLORS[entry.sentiment] || '#888'} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-4">
            {data.map((d) => (
              <div key={d.sentiment} className="text-center">
                <p className="text-lg font-bold" style={{ color: COLORS[d.sentiment] }}>
                  {total ? Math.round((d.count / total) * 100) : 0}%
                </p>
                <p className="text-xs text-muted capitalize">{d.sentiment}</p>
                <p className="text-xs text-muted mt-1">{d.count.toLocaleString()} reviews</p>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-white/10">
            <p className="text-xs text-muted mb-2">What this means:</p>
            <div className="space-y-1">
              {data.map((d) => (
                <div key={d.sentiment} className="flex items-center gap-2 text-xs">
                  <div 
                    className="w-2 h-2 rounded-full" 
                    style={{ backgroundColor: COLORS[d.sentiment] }}
                  />
                  <span className="text-muted capitalize">
                    <strong>{d.sentiment}:</strong> {SENTIMENT_EXPLANATIONS[d.sentiment]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </Card>
  );
}

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

export default function SentimentDistribution({ data }: Props) {
  const total = data.reduce((s, d) => s + d.count, 0);

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-1">Sentiment Breakdown</h3>
      <p className="text-xs text-muted mb-4">{total} total reviews analyzed</p>
      {data.length === 0 ? (
        <p className="text-muted text-sm">No data</p>
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
          <div className="flex justify-center gap-4 mt-2">
            {data.map((d) => (
              <div key={d.sentiment} className="text-center">
                <p className="text-lg font-bold" style={{ color: COLORS[d.sentiment] }}>
                  {total ? Math.round((d.count / total) * 100) : 0}%
                </p>
                <p className="text-xs text-muted capitalize">{d.sentiment}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </Card>
  );
}

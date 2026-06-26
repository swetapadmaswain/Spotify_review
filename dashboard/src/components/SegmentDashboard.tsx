import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Segment } from '../api/client';

interface Props {
  data: Segment[];
}

const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#1DB954',
  negative: '#e91429',
  neutral: '#b3b3b3',
  mixed: '#f59b23',
};

export default function SegmentDashboard({ data }: Props) {
  const pieData = data
    .filter((s) => s.user_count > 0)
    .slice(0, 8)
    .map((s) => ({
      name: (s.segment_name || 'Unknown').slice(0, 20),
      value: s.user_count,
    }));

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl p-5 border border-white/10">
          <h3 className="text-lg font-semibold mb-4">Segment Distribution</h3>
          {pieData.length === 0 ? (
            <p className="text-muted">No segment data.</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={['#1DB954', '#509bf5', '#f59b23', '#e91429', '#b3b3b3'][i % 5]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#282828', border: 'none' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-card rounded-xl p-5 border border-white/10 overflow-auto">
          <h3 className="text-lg font-semibold mb-4">Segment Comparison</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted border-b border-white/10">
                <th className="text-left py-2">Segment</th>
                <th className="text-right py-2">Users</th>
                <th className="text-right py-2">Sentiment</th>
              </tr>
            </thead>
            <tbody>
              {data.map((s) => (
                <tr key={s.id} className="border-b border-white/5">
                  <td className="py-2">{s.segment_name}</td>
                  <td className="text-right">{s.user_count}</td>
                  <td className="text-right">
                    <span style={{ color: SENTIMENT_COLORS[s.avg_sentiment] || '#fff' }}>
                      {s.avg_sentiment}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

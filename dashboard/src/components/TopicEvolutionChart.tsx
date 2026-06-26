import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TopicEvolution } from '../api/client';
import Card from './ui/Card';

interface Props {
  data: TopicEvolution[];
}

const TOPIC_COLORS = ['#1DB954', '#509bf5', '#f59b23', '#e91429', '#b794f6', '#38b2ac'];

export default function TopicEvolutionChart({ data }: Props) {
  const byTopic: Record<string, number> = {};
  data.forEach((row) => {
    const topic = row.primary_topic || 'other';
    byTopic[topic] = (byTopic[topic] || 0) + row.count;
  });

  const chartData = Object.entries(byTopic)
    .map(([topic, count]) => ({ topic, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-1">Topic Evolution</h3>
      <p className="text-xs text-muted mb-4">Most discussed themes in user feedback</p>
      {chartData.length === 0 ? (
        <p className="text-muted text-sm py-6 text-center">No topic data available</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis dataKey="topic" stroke="#666" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={60} />
            <YAxis stroke="#666" />
            <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }} />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={TOPIC_COLORS[i % TOPIC_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}

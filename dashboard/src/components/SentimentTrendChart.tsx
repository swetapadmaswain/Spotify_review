import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { SentimentTrend } from '../api/client';

interface Props {
  data: SentimentTrend[];
}

export default function SentimentTrendChart({ data }: Props) {
  const byDate: Record<string, Record<string, number | string>> = {};

  data.forEach((row) => {
    const date = String(row.date).slice(0, 10);
    if (!byDate[date]) byDate[date] = { date };
    byDate[date][row.sentiment] = Number(row.count);
  });

  const chartData = Object.values(byDate).sort((a, b) =>
    String(a.date).localeCompare(String(b.date))
  );

  return (
    <div className="bg-card rounded-xl p-5 border border-white/10">
      <h3 className="text-lg font-semibold mb-4">Sentiment Trends</h3>
      {chartData.length === 0 ? (
        <p className="text-muted">No trend data available. Run insight generation first.</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#b3b3b3" tick={{ fontSize: 11 }} />
            <YAxis stroke="#b3b3b3" />
            <Tooltip contentStyle={{ background: '#282828', border: 'none' }} />
            <Legend />
            <Line type="monotone" dataKey="positive" stroke="#1DB954" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="negative" stroke="#e91429" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="neutral" stroke="#b3b3b3" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

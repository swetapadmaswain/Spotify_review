import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart,
} from 'recharts';
import { SentimentTrend } from '../api/client';
import Card from './ui/Card';
import Button from './ui/Button';

interface Props {
  data: SentimentTrend[];
  days: number;
  onDaysChange: (d: number) => void;
}

export default function SentimentTrendChart({ data, days, onDaysChange }: Props) {
  const byDate: Record<string, Record<string, number | string>> = {};

  data.forEach((row) => {
    const date = String(row.date).slice(0, 10);
    if (!byDate[date]) byDate[date] = { date };
    byDate[date][row.sentiment] = Number(row.count);
  });

  const chartData = Object.values(byDate).sort((a, b) =>
    String(a.date).localeCompare(String(b.date))
  );

  const totalNegative = data.filter((d) => d.sentiment === 'negative').reduce((s, d) => s + d.count, 0);
  const totalPositive = data.filter((d) => d.sentiment === 'positive').reduce((s, d) => s + d.count, 0);

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-lg font-semibold">Sentiment Trends</h3>
          <p className="text-xs text-muted mt-1">
            {totalPositive} positive · {totalNegative} negative over {days} days
          </p>
        </div>
        <div className="flex gap-1">
          {[7, 14, 30].map((d) => (
            <Button
              key={d}
              variant={days === d ? 'primary' : 'ghost'}
              onClick={() => onDaysChange(d)}
            >
              {d}d
            </Button>
          ))}
        </div>
      </div>
      {chartData.length === 0 ? (
        <p className="text-muted text-sm py-8 text-center">No trend data. Click &quot;Run AI Analysis&quot; to generate insights.</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="posGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1DB954" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#1DB954" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="negGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#e91429" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#e91429" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis dataKey="date" stroke="#666" tick={{ fontSize: 10 }} />
            <YAxis stroke="#666" />
            <Tooltip
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }}
              labelStyle={{ color: '#fff' }}
            />
            <Legend />
            <Area type="monotone" dataKey="positive" stroke="#1DB954" fill="url(#posGrad)" strokeWidth={2} />
            <Area type="monotone" dataKey="negative" stroke="#e91429" fill="url(#negGrad)" strokeWidth={2} />
            <Line type="monotone" dataKey="neutral" stroke="#b3b3b3" strokeWidth={1.5} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}

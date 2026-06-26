import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { Pattern } from '../api/client';

interface Props {
  data: Pattern[];
}

const COLORS: Record<string, string> = {
  temporal: '#1DB954',
  thematic: '#509bf5',
  cross_platform: '#f59b23',
};

export default function PatternDashboard({ data }: Props) {
  const chartData = data.slice(0, 12).map((p) => ({
    name: (p.pattern_description || p.pattern_type || '').slice(0, 28),
    frequency: p.frequency,
    type: p.pattern_type,
  }));

  return (
    <div className="space-y-6">
      <div className="bg-card rounded-xl p-5 border border-white/10">
        <h3 className="text-lg font-semibold mb-4">Pattern Frequency</h3>
        {chartData.length === 0 ? (
          <p className="text-muted">No patterns detected.</p>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#b3b3b3" />
              <YAxis dataKey="name" type="category" width={140} stroke="#b3b3b3" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#282828', border: 'none' }} />
              <Bar dataKey="frequency" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={COLORS[entry.type] || '#888'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {['temporal', 'thematic', 'cross_platform'].map((type) => (
          <div key={type} className="bg-card rounded-xl p-4 border border-white/10">
            <h4 className="text-spotify capitalize mb-2">{type.replace('_', ' ')}</h4>
            <p className="text-2xl font-bold">
              {data.filter((p) => p.pattern_type === type).length}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

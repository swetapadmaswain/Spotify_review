import { useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { Segment } from '../api/client';
import Card from './ui/Card';
import Badge from './ui/Badge';

interface Props {
  data: Segment[];
}

const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#1DB954',
  negative: '#e91429',
  neutral: '#b3b3b3',
  mixed: '#f59b23',
};

const PIE_COLORS = ['#1DB954', '#509bf5', '#f59b23', '#e91429', '#b794f6', '#38b2ac', '#ed64a6', '#ecc94b'];

export default function SegmentDashboard({ data }: Props) {
  const [selected, setSelected] = useState<Segment | null>(null);

  const pieData = data
    .filter((s) => s.user_count > 0)
    .slice(0, 8)
    .map((s) => ({
      name: (s.segment_name || 'Unknown').slice(0, 18),
      value: s.user_count,
      segment: s,
    }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-4">Segment Distribution</h3>
          <p className="text-xs text-muted mb-2">Click a segment to view details</p>
          {pieData.length === 0 ? (
            <p className="text-muted text-sm">No segment data.</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  onClick={(d: any) => setSelected(d?.segment)}
                  className="cursor-pointer"
                >
                  {pieData.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={PIE_COLORS[i % PIE_COLORS.length]}
                      opacity={selected?.id === entry.segment.id ? 1 : 0.7}
                      stroke={selected?.id === entry.segment.id ? '#fff' : 'none'}
                      strokeWidth={2}
                    />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-4">
            {selected ? selected.segment_name : 'Select a Segment'}
          </h3>
          {selected ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-xs text-muted">Users</p>
                  <p className="text-2xl font-bold">{selected.user_count}</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-xs text-muted">Sentiment</p>
                  <p className="text-2xl font-bold capitalize" style={{ color: SENTIMENT_COLORS[selected.avg_sentiment] }}>
                    {selected.avg_sentiment}
                  </p>
                </div>
              </div>
              {selected.primary_challenges?.length > 0 && (
                <div>
                  <p className="text-xs text-muted mb-2">Primary Challenges</p>
                  <div className="flex flex-wrap gap-2">
                    {selected.primary_challenges.map((c, i) => (
                      <Badge key={i} label={String(c)} variant="warning" />
                    ))}
                  </div>
                </div>
              )}
              {selected.segment_criteria && (
                <div className="p-3 rounded-lg bg-black/30 text-xs text-muted font-mono">
                  {JSON.stringify(selected.segment_criteria, null, 2)}
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted text-sm py-16 text-center">Click a pie slice or table row to explore</p>
          )}
        </Card>
      </div>

      <Card className="overflow-auto">
        <h3 className="text-lg font-semibold mb-4">All Segments</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-muted border-b border-white/10">
              <th className="text-left py-3 px-2">Segment</th>
              <th className="text-right py-3 px-2">Users</th>
              <th className="text-right py-3 px-2">Sentiment</th>
              <th className="text-right py-3 px-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {data.map((s) => (
              <tr
                key={s.id}
                className={`border-b border-white/5 transition-colors ${
                  selected?.id === s.id ? 'bg-spotify/5' : 'hover:bg-white/5'
                }`}
              >
                <td className="py-3 px-2 font-medium">{s.segment_name}</td>
                <td className="text-right py-3 px-2">{s.user_count}</td>
                <td className="text-right py-3 px-2">
                  <span style={{ color: SENTIMENT_COLORS[s.avg_sentiment] || '#fff' }} className="capitalize">
                    {s.avg_sentiment}
                  </span>
                </td>
                <td className="text-right py-3 px-2">
                  <button
                    onClick={() => setSelected(s)}
                    className="text-xs text-spotify hover:underline"
                  >
                    Inspect
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

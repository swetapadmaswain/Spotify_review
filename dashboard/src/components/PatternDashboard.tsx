import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Pattern } from '../api/client';
import { filterPatterns } from '../utils/insights';
import Card from './ui/Card';
import Button from './ui/Button';
import Badge from './ui/Badge';

interface Props {
  data: Pattern[];
}

const COLORS: Record<string, string> = {
  temporal: '#1DB954',
  thematic: '#509bf5',
  cross_platform: '#f59b23',
};

const FILTERS = [
  { id: null, label: 'All' },
  { id: 'temporal', label: 'Temporal' },
  { id: 'thematic', label: 'Thematic' },
  { id: 'cross_platform', label: 'Cross-Platform' },
];

export default function PatternDashboard({ data }: Props) {
  const [filter, setFilter] = useState<string | null>(null);
  const [selected, setSelected] = useState<Pattern | null>(null);

  const filtered = filterPatterns(data, filter);
  const chartData = filtered.slice(0, 10).map((p) => ({
    name: (p.pattern_description || p.pattern_type || '').slice(0, 32),
    frequency: p.frequency,
    type: p.pattern_type,
    full: p,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <Button
            key={String(f.id)}
            variant={filter === f.id ? 'primary' : 'ghost'}
            onClick={() => { setFilter(f.id); setSelected(null); }}
          >
            {f.label}
            {f.id && (
              <span className="ml-1 opacity-70">
                ({data.filter((p) => p.pattern_type === f.id).length})
              </span>
            )}
          </Button>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {['temporal', 'thematic', 'cross_platform'].map((type) => {
          const count = data.filter((p) => p.pattern_type === type).length;
          const top = data.filter((p) => p.pattern_type === type).sort((a, b) => b.frequency - a.frequency)[0];
          return (
            <Card
              key={type}
              onClick={() => setFilter(type)}
              className={filter === type ? 'border-spotify/40' : ''}
            >
              <p className="text-xs text-muted uppercase tracking-wide">{type.replace('_', ' ')}</p>
              <p className="text-3xl font-bold mt-1" style={{ color: COLORS[type] }}>{count}</p>
              {top && <p className="text-xs text-muted mt-2 truncate">{top.pattern_description}</p>}
            </Card>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-4">Pattern Frequency</h3>
          {chartData.length === 0 ? (
            <p className="text-muted text-sm">No patterns for this filter.</p>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis type="number" stroke="#666" />
                <YAxis dataKey="name" type="category" width={130} stroke="#666" tick={{ fontSize: 9 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }}
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                />
                <Bar dataKey="frequency" radius={[0, 6, 6, 0]}>
                  {chartData.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={COLORS[entry.type] || '#888'}
                      opacity={selected?.id === entry.full.id ? 1 : 0.75}
                      style={{ cursor: 'pointer' }}
                      onClick={() => setSelected(entry.full)}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-4">Pattern Detail</h3>
          {selected ? (
            <div className="space-y-4">
              <Badge label={selected.pattern_type} variant="info" />
              <p className="text-white/90">{selected.pattern_description}</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-xs text-muted">Frequency</p>
                  <p className="text-xl font-bold text-spotify">{selected.frequency}</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-xs text-muted">Confidence</p>
                  <p className="text-xl font-bold">{Math.round((selected.confidence || 0) * 100)}%</p>
                </div>
              </div>
              {selected.time_period && (
                <p className="text-xs text-muted">Period: {selected.time_period}</p>
              )}
            </div>
          ) : (
            <p className="text-muted text-sm py-12 text-center">
              Click a bar in the chart to inspect pattern details
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}

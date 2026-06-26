import { useState } from 'react';
import { RootCause } from '../api/client';
import { summarizeRootCause } from '../utils/insights';
import Card from './ui/Card';
import Badge from './ui/Badge';

interface Props {
  data: RootCause[];
}

export default function RootCausePanel({ data }: Props) {
  const [selected, setSelected] = useState<number | null>(data[0]?.id ?? null);
  const active = data.find((r) => r.id === selected) || data[0];

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-4">Root Cause Analysis</h3>
      {data.length === 0 ? (
        <p className="text-muted text-sm">No root cause analyses yet.</p>
      ) : (
        <div className="grid md:grid-cols-3 gap-4">
          <div className="space-y-2">
            {data.map((rc) => (
              <button
                key={rc.id}
                onClick={() => setSelected(rc.id)}
                className={`w-full text-left p-3 rounded-lg text-sm transition-all border ${
                  selected === rc.id
                    ? 'bg-spotify/10 border-spotify/40 text-white'
                    : 'border-white/10 text-muted hover:border-white/20 hover:text-white'
                }`}
              >
                <p className="font-medium capitalize">{rc.issue_topic?.replace(/_/g, ' ')}</p>
                <Badge label={`${Math.round((rc.confidence || 0) * 100)}% confidence`} variant="info" />
              </button>
            ))}
          </div>
          <div className="md:col-span-2 p-4 rounded-xl bg-black/30 border border-white/5">
            {active && (
              <>
                <h4 className="font-semibold text-spotify mb-2 capitalize">
                  {active.issue_topic?.replace(/_/g, ' ')}
                </h4>
                <p className="text-sm text-white/80 leading-relaxed whitespace-pre-line">
                  {summarizeRootCause(active)}
                </p>
              </>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}

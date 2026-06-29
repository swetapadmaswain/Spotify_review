import { useState } from 'react';
import { RootCause } from '../api/client';
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
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">🧠 Root Cause Analysis</h3>
        <p className="text-sm text-muted">
          Deep dive into the underlying causes of user issues. Understanding root causes helps fix problems at their source.
        </p>
      </div>
      {data.length === 0 ? (
        <p className="text-muted text-sm">No root cause analyses yet. Run AI analysis to generate insights.</p>
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
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-spotify mb-2 capitalize">
                    {active.issue_topic?.replace(/_/g, ' ')}
                  </h4>
                  <Badge label={`${Math.round((active.confidence || 0) * 100)}% confidence`} variant="info" />
                </div>
                
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-xs text-muted mb-1">Root Causes</p>
                  <p className="text-sm text-white/90 leading-relaxed whitespace-pre-line">
                    {String(active.root_causes?.analysis || 'No analysis available')}
                  </p>
                </div>

                {active.root_causes?.intermediate_factors && typeof active.root_causes.intermediate_factors === 'string' && (
                  <div className="p-3 rounded-lg bg-white/5">
                    <p className="text-xs text-muted mb-1">Contributing Factors</p>
                    <p className="text-sm text-white/90 leading-relaxed whitespace-pre-line">
                      {active.root_causes.intermediate_factors}
                    </p>
                  </div>
                )}

                {active.root_causes?.suggested_fixes && typeof active.root_causes.suggested_fixes === 'string' && (
                  <div className="p-3 rounded-lg bg-spotify/10 border border-spotify/20">
                    <p className="text-xs text-spotify mb-1">💡 Suggested Fixes</p>
                    <p className="text-sm text-white/90 leading-relaxed whitespace-pre-line">
                      {active.root_causes.suggested_fixes}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}

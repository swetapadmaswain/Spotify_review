import { useState } from 'react';
import Card from './ui/Card';
import Badge from './ui/Badge';

interface Props {
  title: string;
  findings: string[];
  variant?: 'findings' | 'needs';
}

export default function KeyFindingsList({ title, findings, variant = 'findings' }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  // Remove duplicates while preserving order
  const uniqueFindings = Array.from(new Set(findings.map(f => f.trim()))).filter(f => f.length > 0);

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <Badge label={`${uniqueFindings.length} items`} variant={variant === 'needs' ? 'warning' : 'info'} />
      </div>
      {uniqueFindings.length === 0 ? (
        <p className="text-muted text-sm">No findings yet.</p>
      ) : (
        <ul className="space-y-2">
          {uniqueFindings.map((f, i) => (
            <li key={i}>
              <button
                onClick={() => setExpanded(expanded === i ? null : i)}
                className="w-full text-left flex gap-3 text-sm p-3 rounded-lg hover:bg-white/5 transition-colors border border-transparent hover:border-white/10"
              >
                <span className="text-spotify font-bold flex-shrink-0">{i + 1}</span>
                <span className="flex-1">{expanded === i ? f : `${f.slice(0, 90)}${f.length > 90 ? '…' : ''}`}</span>
                <span className="text-muted text-xs">{expanded === i ? '▲' : '▼'}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

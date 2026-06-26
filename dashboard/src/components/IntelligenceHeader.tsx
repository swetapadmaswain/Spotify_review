import Card from './ui/Card';
import Badge from './ui/Badge';
import { InsightSummary } from '../api/client';
import { getScoreLabel } from '../utils/insights';

interface Props {
  score: number;
  summary: InsightSummary | null;
  narrative: string;
  lastUpdated: Date | null;
  dominantSentiment: string;
}

export default function IntelligenceHeader({
  score, summary, narrative, lastUpdated, dominantSentiment,
}: Props) {
  const { label, color } = getScoreLabel(score);

  return (
    <Card glow className="relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-spotify/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
      <div className="relative flex flex-col lg:flex-row lg:items-center gap-6">
        <div className="flex-shrink-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-spotify insight-pulse" />
            <span className="text-xs text-spotify font-semibold uppercase tracking-wider">AI Engine Active</span>
          </div>
          <div className="flex items-end gap-3">
            <span className={`text-6xl font-extrabold ${color}`}>{score}</span>
            <div className="mb-2">
              <p className="text-white font-semibold">Discovery Health Score</p>
              <p className={`text-sm ${color}`}>{label}</p>
            </div>
          </div>
        </div>

        <div className="flex-1 border-l border-white/10 pl-0 lg:pl-6">
          <p className="text-sm text-muted mb-2 font-medium">AI Insight Summary</p>
          <p className="text-white/90 leading-relaxed text-sm">{narrative}</p>
          <div className="flex flex-wrap gap-2 mt-4">
            <Badge label={`Dominant: ${dominantSentiment}`} variant={
              dominantSentiment === 'positive' ? 'success' : dominantSentiment === 'negative' ? 'danger' : 'default'
            } />
            {summary && (
              <>
                <Badge label={`${summary.pattern_count} patterns`} variant="info" />
                <Badge label={`${summary.root_cause_count} root causes`} variant="warning" />
              </>
            )}
            {lastUpdated && (
              <Badge label={`Updated ${lastUpdated.toLocaleTimeString()}`} variant="default" />
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

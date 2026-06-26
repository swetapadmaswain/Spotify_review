import {
  InsightSummary, Pattern, Segment, Recommendation, UnmetNeed,
  SentimentTrend, RootCause,
} from '../api/client';

export function computeDiscoveryScore(
  summary: InsightSummary | null,
  sentimentDist: { sentiment: string; count: number }[],
): number {
  if (!summary) return 0;
  const total = sentimentDist.reduce((s, r) => s + r.count, 0) || 1;
  const positive = sentimentDist.find((r) => r.sentiment === 'positive')?.count || 0;
  const negative = sentimentDist.find((r) => r.sentiment === 'negative')?.count || 0;
  const sentimentScore = Math.round(((positive - negative * 0.5) / total) * 50 + 50);
  const insightDepth = Math.min(30, summary.pattern_count + summary.segment_count);
  const needsPenalty = Math.min(20, summary.unmet_need_count * 2);
  return Math.max(0, Math.min(100, sentimentScore + insightDepth - needsPenalty));
}

export function getScoreLabel(score: number): { label: string; color: string } {
  if (score >= 75) return { label: 'Healthy Discovery', color: 'text-spotify' };
  if (score >= 50) return { label: 'Needs Attention', color: 'text-yellow-400' };
  return { label: 'Critical Gaps', color: 'text-red-400' };
}

export function buildAINarrative(
  summary: InsightSummary | null,
  patterns: Pattern[],
  segments: Segment[],
  unmetNeeds: UnmetNeed[],
): string {
  if (!summary) return 'Analyzing user feedback data...';

  const topPattern = patterns.sort((a, b) => b.frequency - a.frequency)[0];
  const topNeed = unmetNeeds.sort((a, b) => b.priority_score - a.priority_score)[0];
  const frustrated = segments.filter((s) => s.avg_sentiment === 'negative').length;

  const parts = [
    `Detected ${summary.pattern_count} behavioral patterns across ${summary.segment_count} user segments.`,
  ];
  if (topPattern) {
    parts.push(`Strongest signal: "${topPattern.pattern_description?.slice(0, 80)}" (${topPattern.frequency} mentions).`);
  }
  if (frustrated > 0) {
    parts.push(`${frustrated} segment(s) show negative sentiment — discovery friction likely.`);
  }
  if (topNeed) {
    parts.push(`Top unmet need: ${topNeed.need_description} (priority ${Math.round(topNeed.priority_score * 100)}%).`);
  }
  return parts.join(' ');
}

export function summarizeRootCause(rc: RootCause): string {
  const analysis = rc.root_causes?.analysis;
  if (typeof analysis === 'string') return analysis.slice(0, 300);
  return `Root cause analysis for ${rc.issue_topic} (confidence: ${Math.round((rc.confidence || 0) * 100)}%)`;
}

export function dominantSentiment(trends: SentimentTrend[]): string {
  const totals: Record<string, number> = {};
  trends.forEach((t) => {
    totals[t.sentiment] = (totals[t.sentiment] || 0) + t.count;
  });
  return Object.entries(totals).sort((a, b) => b[1] - a[1])[0]?.[0] || 'unknown';
}

export function filterPatterns(patterns: Pattern[], type: string | null): Pattern[] {
  if (!type) return patterns;
  return patterns.filter((p) => p.pattern_type === type);
}

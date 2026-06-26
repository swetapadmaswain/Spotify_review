const API_BASE = '';

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  return json.data ?? json;
}

export interface InsightSummary {
  pattern_count: number;
  segment_count: number;
  root_cause_count: number;
  unmet_need_count: number;
  key_findings: string[];
  top_unmet_needs: string[];
}

export interface SentimentTrend {
  date: string;
  sentiment: string;
  count: number;
}

export interface Pattern {
  id: number;
  pattern_type: string;
  pattern_description: string;
  frequency: number;
  confidence: number;
}

export interface Segment {
  id: number;
  segment_name: string;
  user_count: number;
  avg_sentiment: string;
  primary_challenges: string[];
}

export interface Recommendation {
  title: string;
  description: string;
  category: string;
  priority: string;
  complexity: string;
  expected_impact: string;
}

export const api = {
  getSummary: () => fetchJson<InsightSummary>('/api/insights/summary'),
  getSentimentTrends: (days = 30) =>
    fetchJson<SentimentTrend[]>(`/api/analytics/sentiment-trends?days=${days}`),
  getPatterns: () => fetchJson<Pattern[]>('/api/insights/patterns'),
  getSegments: () => fetchJson<Segment[]>('/api/insights/segments'),
  getUnmetNeeds: () => fetchJson<Record<string, unknown>[]>('/api/insights/unmet-needs'),
  getRecommendations: () => fetchJson<Recommendation[]>('/api/recommendations'),
  getSentimentDistribution: () =>
    fetchJson<{ sentiment: string; count: number }[]>('/api/analytics/sentiment-distribution'),
};

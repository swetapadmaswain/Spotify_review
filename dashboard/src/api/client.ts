const API_BASE = '';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
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

export interface TopicEvolution {
  date: string;
  primary_topic: string;
  count: number;
}

export interface Pattern {
  id: number;
  pattern_type: string;
  pattern_description: string;
  frequency: number;
  confidence: number;
  time_period?: string;
}

export interface Segment {
  id: number;
  segment_name: string;
  user_count: number;
  avg_sentiment: string;
  primary_challenges: string[];
  segment_criteria?: Record<string, unknown>;
}

export interface Recommendation {
  id?: number;
  title: string;
  description: string;
  category: string;
  priority: string;
  complexity: string;
  expected_impact: string;
  success_metrics?: string[];
  dependencies?: string[];
}

export interface UnmetNeed {
  id: number;
  need_description: string;
  need_category: string;
  request_count: number;
  priority_score: number;
  strategic_impact: string;
}

export interface RootCause {
  id: number;
  issue_topic: string;
  root_causes: Record<string, unknown>;
  confidence: number;
}

export interface RoadmapItem {
  id: number;
  title: string;
  description: string;
  priority: string;
  quarter: string;
  estimated_effort: string;
}

export const api = {
  getSummary: () => fetchJson<InsightSummary>('/api/insights/summary'),
  getSentimentTrends: (days = 30) =>
    fetchJson<SentimentTrend[]>(`/api/analytics/sentiment-trends?days=${days}`),
  getTopicEvolution: (days = 30) =>
    fetchJson<TopicEvolution[]>(`/api/analytics/topic-evolution?days=${days}`),
  getPatterns: () => fetchJson<Pattern[]>('/api/insights/patterns'),
  getSegments: () => fetchJson<Segment[]>('/api/insights/segments'),
  getUnmetNeeds: () => fetchJson<UnmetNeed[]>('/api/insights/unmet-needs'),
  getRootCauses: () => fetchJson<RootCause[]>('/api/insights/root-causes'),
  getRecommendations: () => fetchJson<Recommendation[]>('/api/recommendations'),
  getRoadmap: () => fetchJson<RoadmapItem[]>('/api/roadmap'),
  getSentimentDistribution: () =>
    fetchJson<{ sentiment: string; count: number }[]>('/api/analytics/sentiment-distribution'),
  getTopTopics: (limit = 8) =>
    fetchJson<{ primary_topic: string; count: number }[]>(`/api/analytics/top-topics?limit=${limit}`),
  generateInsights: (seed = false) =>
    fetch(`${API_BASE}/api/insights/generate?seed=${seed}`, { method: 'POST' }).then((r) => r.json()),
  generateReport: () =>
    fetch(`${API_BASE}/api/reports/generate?template_type=executive`, { method: 'POST' }).then((r) => r.json()),
};

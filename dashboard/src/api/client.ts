import { supabase } from '../lib/supabase';

const API_BASE = (import.meta.env.VITE_API_URL || 'https://spotify-insights-backend-3zs1qksbt-swetapadmaswains-projects.vercel.app').replace(/\/+$/, '');

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    cache: 'no-cache',
    headers: {
      ...options?.headers,
      'Cache-Control': 'no-cache',
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  console.log(`API Response for ${path}:`, json);
  return json.data ?? json;
}

export interface InsightSummary {
  total_reviews: number;
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
  root_causes: {
    analysis?: string;
    intermediate_factors?: string;
    suggested_fixes?: string;
    [key: string]: string | undefined;
  };
  confidence: number;
}

export interface RoadmapItem {
  id: number;
  title: string;
  description: string;
  priority: string;
  quarter: string;
  estimated_effort: string;
  dependencies?: string[];
}

export interface SentimentDistribution {
  sentiment: string;
  count: number;
}

export interface ReportResult {
  file_path: string;
  status: string;
}

export const api = {
  getSummary: async (): Promise<InsightSummary> => {
    return fetchJson<InsightSummary>('/api/insights/summary');
  },
  
  getSentimentTrends: async (days = 30): Promise<SentimentTrend[]> => {
    return fetchJson<SentimentTrend[]>(`/api/analytics/sentiment-trends?days=${days}`);
  },
  
  getTopicEvolution: async (days = 30): Promise<TopicEvolution[]> => {
    return fetchJson<TopicEvolution[]>(`/api/analytics/topic-evolution?days=${days}`);
  },
  
  getPatterns: async (): Promise<Pattern[]> => {
    return fetchJson<Pattern[]>('/api/insights/patterns');
  },
  
  getSegments: async (): Promise<Segment[]> => {
    return fetchJson<Segment[]>('/api/insights/segments');
  },
  
  getUnmetNeeds: async (): Promise<UnmetNeed[]> => {
    return fetchJson<UnmetNeed[]>('/api/insights/unmet-needs');
  },
  
  getRootCauses: async (): Promise<RootCause[]> => {
    return fetchJson<RootCause[]>('/api/insights/root-causes');
  },
  
  getRecommendations: async (): Promise<Recommendation[]> => {
    return fetchJson<Recommendation[]>('/api/recommendations');
  },
  
  getRoadmap: async (): Promise<RoadmapItem[]> => {
    return fetchJson<RoadmapItem[]>('/api/roadmap');
  },
  
  getSentimentDistribution: async (): Promise<SentimentDistribution[]> => {
    return fetchJson<SentimentDistribution[]>('/api/analytics/sentiment-distribution');
  },
  
  getTopTopics: async (limit = 8) => {
    return fetchJson(`/api/analytics/top-topics?limit=${limit}`);
  },
  
  generateInsights: async (seed = false) => {
    return fetchJson('/api/insights/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed })
    });
  },

  generateReport: async (): Promise<ReportResult> => {
    return fetchJson<ReportResult>('/api/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
  },
};

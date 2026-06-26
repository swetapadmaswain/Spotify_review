import { supabase } from '../lib/supabase';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${path}`, options);
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
  getSummary: async (): Promise<InsightSummary> => {
    const { data } = await supabase
      .from('insights')
      .select('insight_type, data')
      .in('insight_type', ['pattern', 'segment', 'root_cause', 'unmet_need']);
    
    const patterns = data?.filter(i => i.insight_type === 'pattern').length || 0;
    const segments = data?.filter(i => i.insight_type === 'segment').length || 0;
    const rootCauses = data?.filter(i => i.insight_type === 'root_cause').length || 0;
    const unmetNeeds = data?.filter(i => i.insight_type === 'unmet_need').length || 0;
    
    return {
      pattern_count: patterns,
      segment_count: segments,
      root_cause_count: rootCauses,
      unmet_need_count: unmetNeeds,
      key_findings: [],
      top_unmet_needs: []
    };
  },
  
  getSentimentTrends: async (days = 30): Promise<SentimentTrend[]> => {
    const { data } = await supabase
      .from('sentiment_analysis')
      .select('sentiment, analyzed_at')
      .gte('analyzed_at', new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString());
    
    const trends: Record<string, Record<string, number>> = {};
    
    data?.forEach(item => {
      const date = new Date(item.analyzed_at).toISOString().split('T')[0];
      if (!trends[date]) trends[date] = {};
      if (!trends[date][item.sentiment]) trends[date][item.sentiment] = 0;
      trends[date][item.sentiment]++;
    });
    
    return Object.entries(trends).flatMap(([date, sentiments]) =>
      Object.entries(sentiments).map(([sentiment, count]) => ({ date, sentiment, count }))
    );
  },
  
  getTopicEvolution: async (days = 30): Promise<TopicEvolution[]> => {
    const { data } = await supabase
      .from('topic_analysis')
      .select('primary_topic, analyzed_at')
      .gte('analyzed_at', new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString());
    
    const topics: Record<string, Record<string, number>> = {};
    
    data?.forEach(item => {
      const date = new Date(item.analyzed_at).toISOString().split('T')[0];
      if (!topics[date]) topics[date] = {};
      if (!topics[date][item.primary_topic]) topics[date][item.primary_topic] = 0;
      topics[date][item.primary_topic]++;
    });
    
    return Object.entries(topics).flatMap(([date, topics]) =>
      Object.entries(topics).map(([primary_topic, count]) => ({ date, primary_topic, count }))
    );
  },
  
  getPatterns: async (): Promise<Pattern[]> => {
    const { data } = await supabase
      .from('insights')
      .select('*')
      .eq('insight_type', 'pattern');
    
    return (data || []).map(item => ({
      id: parseInt(item.id.toString().slice(0, 8), 16),
      pattern_type: item.insight_type,
      pattern_description: item.title,
      frequency: 1,
      confidence: item.confidence || 0.8
    }));
  },
  
  getSegments: async (): Promise<Segment[]> => {
    const { data } = await supabase
      .from('insights')
      .select('*')
      .eq('insight_type', 'segment');
    
    return (data || []).map(item => ({
      id: parseInt(item.id.toString().slice(0, 8), 16),
      segment_name: item.title,
      user_count: 100,
      avg_sentiment: 'neutral',
      primary_challenges: [item.description || '']
    }));
  },
  
  getUnmetNeeds: async (): Promise<UnmetNeed[]> => {
    const { data } = await supabase
      .from('insights')
      .select('*')
      .eq('insight_type', 'unmet_need');
    
    return (data || []).map(item => ({
      id: parseInt(item.id.toString().slice(0, 8), 16),
      need_description: item.title,
      need_category: 'general',
      request_count: 10,
      priority_score: item.confidence ? Math.floor(item.confidence * 10) : 5,
      strategic_impact: item.description || 'medium'
    }));
  },
  
  getRootCauses: async (): Promise<RootCause[]> => {
    const { data } = await supabase
      .from('insights')
      .select('*')
      .eq('insight_type', 'root_cause');
    
    return (data || []).map(item => ({
      id: parseInt(item.id.toString().slice(0, 8), 16),
      issue_topic: item.title,
      root_causes: item.data || {},
      confidence: item.confidence || 0.8
    }));
  },
  
  getRecommendations: async (): Promise<Recommendation[]> => {
    const { data } = await supabase
      .from('insights')
      .select('*')
      .eq('insight_type', 'recommendation');
    
    return (data || []).map(item => ({
      id: parseInt(item.id.toString().slice(0, 8), 16),
      title: item.title,
      description: item.description || '',
      category: 'product',
      priority: 'medium',
      complexity: 'medium',
      expected_impact: 'high'
    }));
  },
  
  getRoadmap: async (): Promise<RoadmapItem[]> => {
    return [];
  },
  
  getSentimentDistribution: async () => {
    const { data } = await supabase
      .from('sentiment_analysis')
      .select('sentiment');
    
    const distribution: Record<string, number> = {};
    data?.forEach(item => {
      if (!distribution[item.sentiment]) distribution[item.sentiment] = 0;
      distribution[item.sentiment]++;
    });
    
    return Object.entries(distribution).map(([sentiment, count]) => ({ sentiment, count }));
  },
  
  getTopTopics: async (limit = 8) => {
    const { data } = await supabase
      .from('topic_analysis')
      .select('primary_topic')
      .limit(100);
    
    const topicCounts: Record<string, number> = {};
    data?.forEach(item => {
      if (!topicCounts[item.primary_topic]) topicCounts[item.primary_topic] = 0;
      topicCounts[item.primary_topic]++;
    });
    
    return Object.entries(topicCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([primary_topic, count]) => ({ primary_topic, count }));
  },
  
  generateInsights: async (seed = false) => {
    return { message: 'Insights generation triggered' };
  },

  generateReport: async () => {
    return { message: 'Report generation triggered' };
  },
};

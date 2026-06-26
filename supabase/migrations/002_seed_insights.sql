-- Seed insights table with sample data
-- Run this in Supabase SQL Editor to populate insights

-- Disable RLS temporarily for this operation
ALTER TABLE insights DISABLE ROW LEVEL SECURITY;

-- Clear existing insights
DELETE FROM insights;

-- Insert pattern insight
INSERT INTO insights (insight_type, title, description, data, confidence, created_at)
VALUES (
  'pattern',
  'Most common topic: recommendation',
  'Users frequently mention recommendation in their feedback (2 mentions)',
  '{"topic": "recommendation", "count": 2}'::jsonb,
  0.8,
  NOW()
);

-- Insert sentiment insight
INSERT INTO insights (insight_type, title, description, data, confidence, created_at)
VALUES (
  'root_cause',
  'Sentiment distribution',
  'Sentiment breakdown: 1 positive, 1 negative, 2 neutral',
  '{"negative_count": 1, "positive_count": 1, "neutral_count": 2, "total": 4}'::jsonb,
  0.75,
  NOW()
);

-- Insert segment insight
INSERT INTO insights (insight_type, title, description, data, confidence, created_at)
VALUES (
  'segment',
  'User segment analysis',
  'Based on review patterns, users can be segmented by their primary concerns',
  '{"segments": ["recommendation-focused", "ui-focused", "performance-focused"]}'::jsonb,
  0.7,
  NOW()
);

-- Insert unmet need insight
INSERT INTO insights (insight_type, title, description, data, confidence, created_at)
VALUES (
  'unmet_need',
  'Feature requests',
  'Users are requesting better playlist customization and discovery features',
  '{"needs": ["better recommendations", "more variety", "ui improvements"]}'::jsonb,
  0.8,
  NOW()
);

-- Insert recommendation insight
INSERT INTO insights (insight_type, title, description, data, confidence, created_at)
VALUES (
  'recommendation',
  'Improve recommendation algorithm',
  'Focus on reducing repetition in radio and playlist suggestions',
  '{"priority": "high", "category": "product"}'::jsonb,
  0.85,
  NOW()
);

-- Re-enable RLS
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;

-- Allow service role to bypass RLS (already default, but ensuring)
ALTER TABLE insights FORCE ROW LEVEL SECURITY;

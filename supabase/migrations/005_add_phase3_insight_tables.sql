-- Add Phase 3 Insight Store tables
-- These tables support the insight generation pipeline

-- Pattern insights table
CREATE TABLE IF NOT EXISTS pattern_insights (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50),
    pattern_description TEXT,
    frequency INTEGER,
    confidence FLOAT,
    time_period VARCHAR(20),
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User segments table
CREATE TABLE IF NOT EXISTS user_segments (
    id SERIAL PRIMARY KEY,
    segment_name VARCHAR(100),
    segment_criteria JSONB,
    user_count INTEGER,
    primary_challenges JSONB,
    avg_sentiment VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Root cause analysis table
CREATE TABLE IF NOT EXISTS root_cause_analysis (
    id SERIAL PRIMARY KEY,
    issue_topic VARCHAR(100),
    root_causes JSONB,
    intermediate_factors JSONB,
    surface_symptoms JSONB,
    confidence FLOAT,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unmet needs table
CREATE TABLE IF NOT EXISTS unmet_needs (
    id SERIAL PRIMARY KEY,
    need_description TEXT,
    need_category VARCHAR(50),
    request_count INTEGER,
    priority_score FLOAT,
    strategic_impact VARCHAR(20),
    identified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RAG cache table
CREATE TABLE IF NOT EXISTS rag_cache (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    context JSONB,
    response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendations table (Phase 4)
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    priority VARCHAR(20),
    complexity VARCHAR(20),
    expected_impact VARCHAR(20),
    success_metrics JSONB,
    dependencies JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roadmap items table (Phase 4)
CREATE TABLE IF NOT EXISTS roadmap_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20),
    estimated_effort VARCHAR(20),
    quarter VARCHAR(10),
    success_metrics JSONB,
    dependencies JSONB,
    recommendation_id INTEGER REFERENCES recommendations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated reports table (Phase 4)
CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) DEFAULT 'comprehensive',
    template_type VARCHAR(50),
    content JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_pattern_insights_type ON pattern_insights(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_insights_discovered ON pattern_insights(discovered_at);
CREATE INDEX IF NOT EXISTS idx_user_segments_created ON user_segments(created_at);
CREATE INDEX IF NOT EXISTS idx_root_cause_topic ON root_cause_analysis(issue_topic);
CREATE INDEX IF NOT EXISTS idx_unmet_needs_priority ON unmet_needs(priority_score);
CREATE INDEX IF NOT EXISTS idx_rag_cache_query ON rag_cache(query);
CREATE INDEX IF NOT EXISTS idx_recommendations_category ON recommendations(category);
CREATE INDEX IF NOT EXISTS idx_roadmap_items_quarter ON roadmap_items(quarter);
CREATE INDEX IF NOT EXISTS idx_generated_reports_type ON generated_reports(report_type);

-- Enable RLS on all new tables
ALTER TABLE pattern_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE root_cause_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE unmet_needs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE roadmap_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;

-- Allow service role full access on all tables
-- Drop existing policies first for idempotency
DROP POLICY IF EXISTS "Service role full access on pattern_insights" ON pattern_insights;
DROP POLICY IF EXISTS "Service role full access on user_segments" ON user_segments;
DROP POLICY IF EXISTS "Service role full access on root_cause_analysis" ON root_cause_analysis;
DROP POLICY IF EXISTS "Service role full access on unmet_needs" ON unmet_needs;
DROP POLICY IF EXISTS "Service role full access on rag_cache" ON rag_cache;
DROP POLICY IF EXISTS "Service role full access on recommendations" ON recommendations;
DROP POLICY IF EXISTS "Service role full access on roadmap_items" ON roadmap_items;
DROP POLICY IF EXISTS "Service role full access on generated_reports" ON generated_reports;

-- Create service role policies
CREATE POLICY "Service role full access on pattern_insights"
ON pattern_insights FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on user_segments"
ON user_segments FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on root_cause_analysis"
ON root_cause_analysis FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on unmet_needs"
ON unmet_needs FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on rag_cache"
ON rag_cache FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on recommendations"
ON recommendations FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on roadmap_items"
ON roadmap_items FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role full access on generated_reports"
ON generated_reports FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- Allow public read access on all tables
-- Drop existing policies first for idempotency
DROP POLICY IF EXISTS "Public read access on pattern_insights" ON pattern_insights;
DROP POLICY IF EXISTS "Public read access on user_segments" ON user_segments;
DROP POLICY IF EXISTS "Public read access on root_cause_analysis" ON root_cause_analysis;
DROP POLICY IF EXISTS "Public read access on unmet_needs" ON unmet_needs;
DROP POLICY IF EXISTS "Public read access on recommendations" ON recommendations;
DROP POLICY IF EXISTS "Public read access on roadmap_items" ON roadmap_items;
DROP POLICY IF EXISTS "Public read access on generated_reports" ON generated_reports;

-- Create public read policies
CREATE POLICY "Public read access on pattern_insights"
ON pattern_insights FOR SELECT
USING (true);

CREATE POLICY "Public read access on user_segments"
ON user_segments FOR SELECT
USING (true);

CREATE POLICY "Public read access on root_cause_analysis"
ON root_cause_analysis FOR SELECT
USING (true);

CREATE POLICY "Public read access on unmet_needs"
ON unmet_needs FOR SELECT
USING (true);

CREATE POLICY "Public read access on recommendations"
ON recommendations FOR SELECT
USING (true);

CREATE POLICY "Public read access on roadmap_items"
ON roadmap_items FOR SELECT
USING (true);

CREATE POLICY "Public read access on generated_reports"
ON generated_reports FOR SELECT
USING (true);

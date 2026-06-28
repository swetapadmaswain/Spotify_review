-- Add entity_analysis table for Phase 3 insights
CREATE TABLE entity_analysis (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    review_id UUID REFERENCES raw_reviews(id) ON DELETE CASCADE,
    entities JSONB,
    entity_types JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_entity_review_id ON entity_analysis(review_id);

-- Enable RLS
ALTER TABLE entity_analysis ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public read access for entity_analysis"
  ON entity_analysis FOR SELECT
  TO anon
  USING (true);

-- Allow service role full access
CREATE POLICY "Service role full access on entity_analysis"
ON entity_analysis FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

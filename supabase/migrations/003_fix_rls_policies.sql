-- Fix RLS policies to allow service_role to write to all tables
-- This enables automated data collection and insights generation

-- Drop existing policies
DROP POLICY IF EXISTS "Enable read access for all users" ON data_collection_runs;
DROP POLICY IF EXISTS "Enable read access for all users" ON raw_reviews;
DROP POLICY IF EXISTS "Enable read access for all users" ON sentiment_analysis;
DROP POLICY IF EXISTS "Enable read access for all users" ON topic_analysis;
DROP POLICY IF EXISTS "Enable read access for all users" ON insights;

-- Drop our new policies if they already exist (for idempotency)
DROP POLICY IF EXISTS "Service role full access on data_collection_runs" ON data_collection_runs;
DROP POLICY IF EXISTS "Public read access on data_collection_runs" ON data_collection_runs;
DROP POLICY IF EXISTS "Service role full access on raw_reviews" ON raw_reviews;
DROP POLICY IF EXISTS "Public read access on raw_reviews" ON raw_reviews;
DROP POLICY IF EXISTS "Service role full access on sentiment_analysis" ON sentiment_analysis;
DROP POLICY IF EXISTS "Public read access on sentiment_analysis" ON sentiment_analysis;
DROP POLICY IF EXISTS "Service role full access on topic_analysis" ON topic_analysis;
DROP POLICY IF EXISTS "Public read access on topic_analysis" ON topic_analysis;
DROP POLICY IF EXISTS "Service role full access on insights" ON insights;
DROP POLICY IF EXISTS "Public read access on insights" ON insights;

-- Create new policies that allow service_role full access and public read access

-- data_collection_runs
CREATE POLICY "Service role full access on data_collection_runs"
ON data_collection_runs FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read access on data_collection_runs"
ON data_collection_runs FOR SELECT
USING (true);

-- raw_reviews
CREATE POLICY "Service role full access on raw_reviews"
ON raw_reviews FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read access on raw_reviews"
ON raw_reviews FOR SELECT
USING (true);

-- sentiment_analysis
CREATE POLICY "Service role full access on sentiment_analysis" 
ON sentiment_analysis FOR ALL 
USING (auth.role() = 'service_role') 
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read access on sentiment_analysis" 
ON sentiment_analysis FOR SELECT 
USING (true);

-- topic_analysis
CREATE POLICY "Service role full access on topic_analysis" 
ON topic_analysis FOR ALL 
USING (auth.role() = 'service_role') 
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read access on topic_analysis" 
ON topic_analysis FOR SELECT 
USING (true);

-- insights
CREATE POLICY "Service role full access on insights" 
ON insights FOR ALL 
USING (auth.role() = 'service_role') 
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Public read access on insights" 
ON insights FOR SELECT 
USING (true);

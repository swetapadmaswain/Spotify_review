-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Data collection runs table
CREATE TABLE data_collection_runs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    records_collected INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Raw reviews table
CREATE TABLE raw_reviews (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    review_text TEXT NOT NULL,
    rating INTEGER,
    author VARCHAR(255),
    date TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    collection_run_id UUID REFERENCES data_collection_runs(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sentiment analysis table
CREATE TABLE sentiment_analysis (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    review_id UUID REFERENCES raw_reviews(id) ON DELETE CASCADE,
    sentiment VARCHAR(20) NOT NULL,
    confidence FLOAT,
    emotion VARCHAR(50),
    intensity VARCHAR(20),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Topic analysis table
CREATE TABLE topic_analysis (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    review_id UUID REFERENCES raw_reviews(id) ON DELETE CASCADE,
    primary_topic VARCHAR(100),
    secondary_topics JSONB,
    relevance_scores JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insights table
CREATE TABLE insights (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    data JSONB,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_raw_reviews_source ON raw_reviews(source);
CREATE INDEX idx_raw_reviews_date ON raw_reviews(date);
CREATE INDEX idx_sentiment_sentiment ON sentiment_analysis(sentiment);
CREATE INDEX idx_topic_primary ON topic_analysis(primary_topic);
CREATE INDEX idx_insights_type ON insights(insight_type);
CREATE INDEX idx_insights_created ON insights(created_at);

-- Row Level Security (RLS)
ALTER TABLE raw_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;

-- Allow public read access for dashboard
CREATE POLICY "Public read access for raw_reviews"
  ON raw_reviews FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public read access for sentiment_analysis"
  ON sentiment_analysis FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public read access for topic_analysis"
  ON topic_analysis FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public read access for insights"
  ON insights FOR SELECT
  TO anon
  USING (true);

-- Storage policies (run in Supabase dashboard)
-- CREATE POLICY "Public read access for storage"
--   ON storage.objects FOR SELECT
--   TO anon
--   USING (bucket_id = 'raw-data');

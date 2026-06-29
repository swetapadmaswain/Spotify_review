-- Add generated_reports table for storing AI-generated reports
CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) DEFAULT 'comprehensive',
    template_type VARCHAR(50) DEFAULT 'executive',
    content JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;

-- Allow read access to authenticated users
CREATE POLICY "Allow read access to authenticated users"
    ON generated_reports FOR SELECT
    TO authenticated
    USING (true);

-- Allow service role to insert
CREATE POLICY "Allow service role to insert"
    ON generated_reports FOR INSERT
    TO service_role
    WITH CHECK (true);

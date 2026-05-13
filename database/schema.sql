-- ============================================
-- Supabase (PostgreSQL) Database Schema
-- Platform-Aware Fake Profile Detection System
-- ============================================
-- Run this in the Supabase SQL Editor to create the table

-- Predictions table — stores every prediction made
CREATE TABLE IF NOT EXISTS predictions (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    platform        TEXT NOT NULL CHECK (platform IN ('instagram', 'twitter')),
    username        TEXT DEFAULT '',
    followers_count NUMERIC DEFAULT 0,
    following_count NUMERIC DEFAULT 0,
    follower_ratio  NUMERIC DEFAULT 0,
    posts_or_tweets NUMERIC DEFAULT 0,
    account_age_days NUMERIC DEFAULT 0,
    bio_length      NUMERIC DEFAULT 0,
    engagement_rate NUMERIC DEFAULT 0,
    prediction      INTEGER NOT NULL CHECK (prediction IN (0, 1)),
    probability     NUMERIC NOT NULL,
    risk_level      TEXT CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    source          TEXT DEFAULT 'manual' CHECK (source IN ('manual', 'bulk', 'api'))
);

-- Create indexes for common queries
CREATE INDEX idx_predictions_platform ON predictions(platform);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX idx_predictions_prediction ON predictions(prediction);

-- Row Level Security (RLS) — enable for production
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Allow read access for authenticated users
CREATE POLICY "Allow read access" ON predictions
    FOR SELECT USING (true);

-- Allow insert access for authenticated users
CREATE POLICY "Allow insert access" ON predictions
    FOR INSERT WITH CHECK (true);

-- ============================================
-- Optional: Create a view for dashboard analytics
-- ============================================
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT
    COUNT(*) AS total_scans,
    COUNT(*) FILTER (WHERE prediction = 1) AS fake_count,
    COUNT(*) FILTER (WHERE prediction = 0) AS real_count,
    ROUND(COUNT(*) FILTER (WHERE prediction = 1)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1) AS fake_percentage,
    ROUND(AVG(probability), 4) AS avg_probability,
    COUNT(*) FILTER (WHERE platform = 'instagram') AS instagram_total,
    COUNT(*) FILTER (WHERE platform = 'twitter') AS twitter_total
FROM predictions;

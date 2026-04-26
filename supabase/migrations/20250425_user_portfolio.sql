-- User Portfolio Holdings Schema
-- Stores user's actual stock holdings for personalized recommendations

-- Drop existing tables if they exist
DROP TABLE IF EXISTS user_holdings CASCADE;

-- User Holdings Table
CREATE TABLE user_holdings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT DEFAULT 'default_user', -- In production, this would be from auth
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL CHECK (shares > 0),
    average_cost DECIMAL(12, 4) CHECK (average_cost >= 0),
    sector TEXT,
    market TEXT DEFAULT 'US', -- US or IN
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_user_holdings_user_id ON user_holdings(user_id);
CREATE INDEX idx_user_holdings_symbol ON user_holdings(symbol);
CREATE INDEX idx_user_holdings_market ON user_holdings(market);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_user_holdings_updated_at
    BEFORE UPDATE ON user_holdings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Portfolio Analysis Results Table
CREATE TABLE portfolio_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT DEFAULT 'default_user',
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_value DECIMAL(15, 2),
    daily_change DECIMAL(15, 2),
    daily_change_percent DECIMAL(8, 4),
    sector_allocation JSONB,
    risk_score DECIMAL(5, 2),
    sentiment_score DECIMAL(5, 2),
    geopolitical_risk JSONB,
    short_term_strategy JSONB,
    long_term_strategy JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_portfolio_analysis_user_id ON portfolio_analysis(user_id);
CREATE INDEX idx_portfolio_analysis_date ON portfolio_analysis(analysis_date);

-- Comment on tables
COMMENT ON TABLE user_holdings IS 'Stores user''s actual stock holdings for personalized recommendations';
COMMENT ON TABLE portfolio_analysis IS 'Stores analysis results for user''s portfolio';

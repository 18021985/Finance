-- Drop existing objects if they exist to avoid schema conflicts
DROP VIEW IF EXISTS recommendation_stats CASCADE;
DROP FUNCTION IF EXISTS evaluate_recommendation_accuracy() CASCADE;
DROP FUNCTION IF EXISTS auto_evaluate_recommendations() CASCADE;
DROP TABLE IF EXISTS recommendation_performance CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS market_data_snapshots CASCADE;

-- Create recommendations tracking table
CREATE TABLE recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('buy', 'sell', 'hold')),
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    target_price FLOAT,
    entry_price FLOAT NOT NULL,
    stop_loss FLOAT,
    take_profit FLOAT,
    time_horizon VARCHAR(20) NOT NULL CHECK (time_horizon IN ('short-term', 'medium-term', 'long-term')),
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    sector VARCHAR(50),
    expected_return FLOAT,
    position_size FLOAT,
    reasoning JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled', 'expired'))
);

-- Create recommendation performance tracking table
CREATE TABLE IF NOT EXISTS recommendation_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    recommendation_id UUID REFERENCES recommendations(id) ON DELETE CASCADE,
    actual_price_at_expiry FLOAT,
    actual_return FLOAT,
    accuracy_score FLOAT CHECK (accuracy_score >= 0 AND accuracy <= 1),
    hit_target BOOLEAN,
    hit_stop_loss BOOLEAN,
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- Create market data snapshot table for comparison
CREATE TABLE IF NOT EXISTS market_data_snapshots (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price FLOAT NOT NULL,
    volume BIGINT,
    market_cap BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'yahoo_finance'
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_recommendations_symbol ON recommendations(symbol);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON recommendations(created_at);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_recommendations_time_horizon ON recommendations(time_horizon);
CREATE INDEX IF NOT EXISTS idx_recommendation_performance_rec_id ON recommendation_performance(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_market_data_snapshots_symbol ON market_data_snapshots(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_snapshots_timestamp ON market_data_snapshots(timestamp);

-- Create function to evaluate recommendation accuracy
CREATE OR REPLACE FUNCTION evaluate_recommendation_accuracy()
RETURNS TABLE (
    rec_id UUID,
    symbol VARCHAR(20),
    action VARCHAR(10),
    accuracy_score FLOAT,
    actual_return FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.symbol,
        r.action,
        CASE 
            WHEN r.action = 'buy' AND m.price >= r.target_price THEN 1.0
            WHEN r.action = 'buy' AND m.price >= r.entry_price THEN 
                GREATEST(0, (m.price - r.entry_price) / r.entry_price)
            WHEN r.action = 'sell' AND m.price <= r.target_price THEN 1.0
            WHEN r.action = 'sell' AND m.price <= r.entry_price THEN 
                GREATEST(0, (r.entry_price - m.price) / r.entry_price)
            ELSE 0.0
        END as accuracy_score,
        CASE 
            WHEN r.action = 'buy' THEN (m.price - r.entry_price) / r.entry_price
            WHEN r.action = 'sell' THEN (r.entry_price - m.price) / r.entry_price
            ELSE 0
        END as actual_return
    FROM recommendations r
    LEFT JOIN market_data_snapshots m ON r.symbol = m.symbol
    WHERE r.status = 'active' 
    AND r.expires_at <= NOW()
    AND m.timestamp = (
        SELECT MAX(timestamp) 
        FROM market_data_snapshots 
        WHERE symbol = r.symbol
    );
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically evaluate expired recommendations
CREATE OR REPLACE FUNCTION auto_evaluate_recommendations()
RETURNS TRIGGER AS $$
BEGIN
    -- This function would be called by a scheduled job
    -- to evaluate recommendations that have expired
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create view for recommendation statistics
CREATE OR REPLACE VIEW recommendation_stats AS
SELECT 
    time_horizon,
    action,
    COUNT(*) as total_recommendations,
    AVG(accuracy_score) as avg_accuracy,
    AVG(actual_return) as avg_return,
    SUM(CASE WHEN hit_target THEN 1 ELSE 0 END) as target_hits,
    SUM(CASE WHEN hit_stop_loss THEN 1 ELSE 0 END) as stop_loss_hits
FROM recommendation_performance rp
JOIN recommendations r ON rp.recommendation_id = r.id
GROUP BY time_horizon, action;

-- Grant permissions (adjust based on your Supabase setup)
-- GRANT ALL ON recommendations TO authenticated;
-- GRANT ALL ON recommendation_performance TO authenticated;
-- GRANT ALL ON market_data_snapshots TO authenticated;
-- GRANT EXECUTE ON FUNCTION evaluate_recommendation_accuracy TO authenticated;

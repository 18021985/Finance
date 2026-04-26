-- Supabase Schema for Financial Intelligence System
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    predicted_direction VARCHAR(20) NOT NULL, -- 'bullish', 'bearish', 'neutral'
    predicted_probability FLOAT NOT NULL,
    actual_direction VARCHAR(20),
    actual_return FLOAT,
    confidence FLOAT DEFAULT 0.0,
    model_used VARCHAR(100),
    features JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    sharpe_ratio FLOAT NOT NULL,
    max_drawdown FLOAT NOT NULL,
    win_rate FLOAT NOT NULL,
    total_predictions INTEGER NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    model_version VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Models table
CREATE TABLE IF NOT EXISTS models (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'ensemble', 'lstm', 'rl', etc.
    version VARCHAR(50) NOT NULL,
    hyperparameters JSONB,
    accuracy FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE
);

-- Feature importance table
CREATE TABLE IF NOT EXISTS feature_importance (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    model_id UUID REFERENCES models(id) ON DELETE CASCADE,
    feature_name VARCHAR(100) NOT NULL,
    importance_score FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Watchlist table
CREATE TABLE IF NOT EXISTS watchlist (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_analyzed TIMESTAMP WITH TIME ZONE
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- 'price', 'signal', 'pattern'
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info', -- 'info', 'warning', 'critical'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendations table (persisted outputs for monitoring + expiry tracking)
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(20) NOT NULL, -- buy/sell/hold/increase/reduce/watch
    confidence FLOAT NOT NULL,
    target_price FLOAT,
    entry_price FLOAT,
    stop_loss FLOAT,
    take_profit FLOAT,
    time_horizon VARCHAR(30),
    risk_level VARCHAR(20),
    sector VARCHAR(100),
    expected_return FLOAT DEFAULT 0.0,
    position_size FLOAT DEFAULT 0.0,
    reasoning JSONB,
    trace JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_recommendations_symbol_created ON recommendations(symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_expires ON recommendations(expires_at);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(symbol);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_used);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_period ON performance_metrics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_alerts_read ON alerts(is_read);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for predictions table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'update_predictions_updated_at'
    ) THEN
        CREATE TRIGGER update_predictions_updated_at
            BEFORE UPDATE ON predictions
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END;
$$;

-- Insert sample model
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM models WHERE model_name = 'Ensemble Predictor' AND version = '1.0.0') THEN
        INSERT INTO models (model_name, model_type, version, hyperparameters, is_active)
        VALUES ('Ensemble Predictor', 'ensemble', '1.0.0', '{"n_estimators": 100, "max_depth": 6}'::jsonb, TRUE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM models WHERE model_name = 'LSTM Model' AND version = '1.0.0') THEN
        INSERT INTO models (model_name, model_type, version, hyperparameters, is_active)
        VALUES ('LSTM Model', 'deep_learning', '1.0.0', '{"sequence_length": 50, "epochs": 50}'::jsonb, FALSE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM models WHERE model_name = 'RL Trader' AND version = '1.0.0') THEN
        INSERT INTO models (model_name, model_type, version, hyperparameters, is_active)
        VALUES ('RL Trader', 'reinforcement_learning', '1.0.0', '{"algorithm": "PPO", "timesteps": 10000}'::jsonb, FALSE);
    END IF;
END;
$$;

-- Create view for recent predictions
CREATE OR REPLACE VIEW recent_predictions AS
SELECT 
    symbol,
    predicted_direction,
    predicted_probability,
    confidence,
    model_used,
    timestamp
FROM predictions
ORDER BY timestamp DESC
LIMIT 100;

-- Create view for performance summary
CREATE OR REPLACE VIEW performance_summary AS
SELECT 
    model_version,
    AVG(accuracy) as avg_accuracy,
    AVG(sharpe_ratio) as avg_sharpe,
    AVG(win_rate) as avg_win_rate,
    COUNT(*) as total_evaluations
FROM performance_metrics
GROUP BY model_version
ORDER BY avg_accuracy DESC;

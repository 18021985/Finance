-- Comprehensive schema fix: drop all existing objects to allow clean recreation
DO $$
BEGIN
    -- Drop view if it exists
    DROP VIEW IF EXISTS recommendation_stats CASCADE;
    
    -- Drop functions if they exist
    DROP FUNCTION IF EXISTS evaluate_recommendation_accuracy() CASCADE;
    DROP FUNCTION IF EXISTS auto_evaluate_recommendations() CASCADE;
    
    -- Drop tables if they exist (this will remove any old schema/constraints)
    DROP TABLE IF EXISTS recommendation_performance CASCADE;
    DROP TABLE IF EXISTS recommendations CASCADE;
    DROP TABLE IF EXISTS market_data_snapshots CASCADE;
END $$;

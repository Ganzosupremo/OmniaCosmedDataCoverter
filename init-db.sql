-- Initialize the Phase Analyzer database
-- This script sets up the initial database structure and data

-- Create initial bucket in MinIO (will be done via API call)
-- The actual table creation is handled by SQLAlchemy models

-- You can add any initial data here if needed
-- For example, default plan configurations, admin users, etc.

-- Create extension for UUID generation if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Example: Insert default plan configurations
-- This is optional since plan limits are handled in code
INSERT INTO public.users (id, email, name, plan, stripe_customer_id, created_at, is_active) 
VALUES (1, 'admin@phaseanalyzer.com', 'Admin User', 'team', 'cus_admin', NOW(), true)
ON CONFLICT (email) DO NOTHING;

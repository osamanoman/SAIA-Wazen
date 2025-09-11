-- Initialize SAIA Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the main database if it doesn't exist
SELECT 'CREATE DATABASE saia_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'saia_db')\gexec

-- Connect to the saia_db database
\c saia_db;

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant all privileges to the saia_user
GRANT ALL PRIVILEGES ON DATABASE saia_db TO saia_user;
GRANT ALL ON SCHEMA public TO saia_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO saia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO saia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO saia_user;

-- Create a comment
COMMENT ON DATABASE saia_db IS 'SAIA Business Management System Database';

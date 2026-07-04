-- Step 2d: read-only role for Redash and LLM SQL agent
-- Run after 001_init_schema.sql and ETL load:
--   psql postgresql://postgres:postgres@localhost:5433/youtube_analytics -f infra/sql/002_redash_reader.sql

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'redash_reader') THEN
        CREATE ROLE redash_reader LOGIN PASSWORD 'redash_reader';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA youtube TO redash_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA youtube TO redash_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA youtube GRANT SELECT ON TABLES TO redash_reader;

-- Redash connection string (read-only):
-- postgresql://redash_reader:redash_reader@localhost:5433/youtube_analytics

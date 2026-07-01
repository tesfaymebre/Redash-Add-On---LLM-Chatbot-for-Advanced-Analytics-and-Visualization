-- Task 2: YouTube Analytics schema for Redash + LLM chatbot
-- Run: psql -U postgres -d youtube_analytics -f infra/sql/001_init_schema.sql

CREATE SCHEMA IF NOT EXISTS youtube;

-- ---------------------------------------------------------------------------
-- Channel-level daily KPIs (from "Viewership by Date" / Totals exports)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS youtube.viewership_daily (
    view_date               DATE PRIMARY KEY,
    views                   INTEGER NOT NULL CHECK (views >= 0),
    watch_time_hours        NUMERIC(12, 4),
    avg_view_duration_sec   INTEGER CHECK (avg_view_duration_sec >= 0)
);

COMMENT ON TABLE youtube.viewership_daily IS
    'Daily channel-level views and watch time. Grain: one row per calendar day.';

-- ---------------------------------------------------------------------------
-- Long-format daily metrics for all Chart data.csv files
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS youtube.dimension_metrics_daily (
    id                  SERIAL PRIMARY KEY,
    view_date           DATE NOT NULL,
    report_type         VARCHAR(50) NOT NULL,
    dimension_value     VARCHAR(255) NOT NULL,
    metric_name         VARCHAR(50) NOT NULL,   -- views | shares | subscribers
    metric_value        NUMERIC NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_dimension_metrics_daily
        UNIQUE (view_date, report_type, dimension_value, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_dim_metrics_report_date
    ON youtube.dimension_metrics_daily (report_type, view_date);

CREATE INDEX IF NOT EXISTS idx_dim_metrics_dimension
    ON youtube.dimension_metrics_daily (report_type, dimension_value);

COMMENT ON TABLE youtube.dimension_metrics_daily IS
    'Daily time-series per report dimension. report_type matches Data/ folder slug.';

-- ---------------------------------------------------------------------------
-- Period snapshot summaries (from Table data.csv, excluding Total rows)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS youtube.dimension_snapshots (
    id                      SERIAL PRIMARY KEY,
    report_type             VARCHAR(50) NOT NULL,
    dimension_value         VARCHAR(255) NOT NULL,

    -- Common metrics (nullable — not every report has all)
    views                   INTEGER,
    watch_time_hours        NUMERIC(12, 4),
    avg_view_duration_sec   INTEGER,
    shares                  INTEGER,

    -- Traffic source extras
    impressions             BIGINT,
    impressions_ctr_pct     NUMERIC(6, 2),

    -- Subscription source extras
    subscribers             INTEGER,
    subscribers_gained      INTEGER,
    subscribers_lost        INTEGER,

    -- Demographics (age / gender) — percentage-based reports
    views_pct               NUMERIC(6, 2),
    watch_time_pct          NUMERIC(6, 2),
    avg_pct_viewed          NUMERIC(6, 2),

    -- Cities extras
    city_place_id           VARCHAR(100),
    geography_code          VARCHAR(10),

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_dimension_snapshots
        UNIQUE (report_type, dimension_value)
);

CREATE INDEX IF NOT EXISTS idx_dim_snapshots_report
    ON youtube.dimension_snapshots (report_type);

COMMENT ON TABLE youtube.dimension_snapshots IS
    'Period-aggregate snapshot per dimension value (YouTube Table data export).';

-- ---------------------------------------------------------------------------
-- LLM / RAG metadata — business descriptions per report
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS youtube.report_metadata (
    report_type         VARCHAR(50) PRIMARY KEY,
    display_name        VARCHAR(100) NOT NULL,
    description         TEXT NOT NULL,
    grain               VARCHAR(100) NOT NULL,
    source_files        TEXT[] NOT NULL,
    example_questions   TEXT[] NOT NULL
);

-- ---------------------------------------------------------------------------
-- Placeholder: per-video data (challenge scope — not in current Data/ export)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS youtube.videos (
    video_id            VARCHAR(20) PRIMARY KEY,
    title               TEXT,
    published_at        TIMESTAMPTZ,
    duration_sec        INTEGER,
    category            VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS youtube.video_metrics_daily (
    video_id            VARCHAR(20) NOT NULL REFERENCES youtube.videos(video_id),
    view_date           DATE NOT NULL,
    views               INTEGER NOT NULL DEFAULT 0,
    watch_time_hours    NUMERIC(12, 4),
    PRIMARY KEY (video_id, view_date)
);

-- ---------------------------------------------------------------------------
-- Seed report_metadata (critical for Task 4 NL→SQL)
-- ---------------------------------------------------------------------------
INSERT INTO youtube.report_metadata
    (report_type, display_name, description, grain, source_files, example_questions)
VALUES
    ('viewership_daily', 'Viewership by Date',
     'Channel-wide daily views, watch time, and average view duration.',
     'one row per day',
     ARRAY['Viewership by Date/Table data.csv'],
     ARRAY['What were total views last week?', 'Show daily view trend for December 2023']),

    ('device_type', 'Device Type',
     'Breakdown of views by device: Computer, Mobile phone, Tablet, TV.',
     'daily per device OR period snapshot',
     ARRAY['Device type/Table data.csv', 'Device type/Chart data.csv'],
     ARRAY['How many views came from mobile?', 'Compare computer vs mobile views over time']),

    ('geography', 'Geography',
     'Views by country using ISO 3166-1 alpha-2 codes (ET=Ethiopia, US=United States).',
     'daily per country OR period snapshot',
     ARRAY['Geography/Table data.csv', 'Geography/Chart data.csv'],
     ARRAY['Which country has the most views?', 'Views from Ethiopia over time']),

    ('cities', 'Cities',
     'Views by city with Google place IDs and linked country codes.',
     'daily per city OR period snapshot',
     ARRAY['Cities/Table data.csv', 'Cities/Chart data.csv'],
     ARRAY['Top cities by views', 'Views in Addis Ababa over time']),

    ('traffic_source', 'Traffic Source',
     'How viewers found the channel: search, suggested videos, browse, external, etc. Includes impressions and CTR.',
     'period snapshot with impressions',
     ARRAY['Traffic source/Table data.csv', 'Traffic source/Chart data.csv'],
     ARRAY['Top traffic sources by views', 'What is the click-through rate from YouTube search?']),

    ('operating_system', 'Operating System',
     'Views broken down by OS (Windows, Android, iOS, etc.).',
     'daily per OS OR period snapshot',
     ARRAY['Operating system/Table data.csv', 'Operating system/Chart data.csv'],
     ARRAY['Views by operating system', 'Android vs iOS views trend']),

    ('content_type', 'Content Type',
     'Views by content format (e.g., video on demand, shorts).',
     'daily per content type OR period snapshot',
     ARRAY['Content type/Table data.csv', 'Content type/Chart data.csv'],
     ARRAY['Views by content type']),

    ('subscription_status', 'Subscription Status',
     'Views from subscribed vs not-subscribed viewers.',
     'daily per status OR period snapshot',
     ARRAY['Subscription status/Table data.csv', 'Subscription status/Chart data.csv'],
     ARRAY['Views from subscribed users', 'Subscribed vs unsubscribed view trend']),

    ('subscription_source', 'Subscription Source',
     'Where subscribers came from; includes gained/lost counts.',
     'daily per source OR period snapshot',
     ARRAY['Subscription source/Table data.csv', 'Subscription source/Chart data.csv'],
     ARRAY['How many subscribers gained from YouTube search?', 'Net subscriber growth by source']),

    ('new_returning_viewers', 'New and Returning Viewers',
     'Views from new, returning, or unknown audience segments.',
     'daily per segment OR period snapshot',
     ARRAY['New and returning viewers/Table data.csv', 'New and returning viewers/Chart data.csv'],
     ARRAY['New vs returning viewer views']),

    ('sharing_service', 'Sharing Service',
     'How many times content was shared via Facebook, WhatsApp, etc.',
     'daily per service — metric is shares',
     ARRAY['Sharing service/Table data.csv', 'Sharing service/Chart data.csv'],
     ARRAY['Total shares by platform', 'Facebook shares over time']),

    ('subtitles_cc', 'Subtitles and CC',
     'Views with subtitles or closed captions enabled vs disabled.',
     'daily per subtitle status OR period snapshot',
     ARRAY['Subtitles and CC/Table data.csv', 'Subtitles and CC/Chart data.csv'],
     ARRAY['Views with subtitles enabled']),

    ('viewer_age', 'Viewer Age',
     'Audience age distribution with percentage-based view and watch time metrics.',
     'period snapshot only (no daily chart)',
     ARRAY['Viewer age/Table data.csv'],
     ARRAY['What age group watches the most?', 'Average view duration by age group']),

    ('viewer_gender', 'Viewer Gender',
     'Audience gender split with percentage-based metrics.',
     'period snapshot only',
     ARRAY['Viewer gender/Table data.csv'],
     ARRAY['Male vs female view percentage', 'Watch time by gender'])
ON CONFLICT (report_type) DO NOTHING;

-- Read-only role for Redash / LLM agent (apply after ETL in production)
-- CREATE ROLE redash_reader LOGIN PASSWORD 'changeme';
-- GRANT USAGE ON SCHEMA youtube TO redash_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA youtube TO redash_reader;

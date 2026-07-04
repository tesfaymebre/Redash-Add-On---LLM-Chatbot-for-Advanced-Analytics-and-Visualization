-- Starter queries for Redash dashboards (Task 2d)
-- Copy each block into Redash → New Query → PostgreSQL (YouTube Analytics)

-- ---------------------------------------------------------------------------
-- Q1: Daily views (line chart)
-- Table: viewership_daily | Viz: Line chart, x=view_date, y=views
-- ---------------------------------------------------------------------------
SELECT view_date, views, watch_time_hours, avg_view_duration_sec
FROM youtube.viewership_daily
ORDER BY view_date;

-- ---------------------------------------------------------------------------
-- Q2: Top 10 countries (bar chart)
-- Table: dimension_snapshots | Viz: Bar, x=country, y=views
-- ---------------------------------------------------------------------------
SELECT dimension_value AS country, views
FROM youtube.dimension_snapshots
WHERE report_type = 'geography'
ORDER BY views DESC
LIMIT 10;

-- ---------------------------------------------------------------------------
-- Q3: Device breakdown (pie or bar)
-- ---------------------------------------------------------------------------
SELECT dimension_value AS device, views
FROM youtube.dimension_snapshots
WHERE report_type = 'device_type'
ORDER BY views DESC;

-- ---------------------------------------------------------------------------
-- Q4: Traffic sources with CTR (table)
-- ---------------------------------------------------------------------------
SELECT
    dimension_value AS traffic_source,
    views,
    impressions,
    impressions_ctr_pct AS ctr_pct
FROM youtube.dimension_snapshots
WHERE report_type = 'traffic_source'
ORDER BY views DESC NULLS LAST;

-- ---------------------------------------------------------------------------
-- Q5: Mobile views over time (line chart)
-- Table: dimension_metrics_daily — use for dimension + date questions
-- ---------------------------------------------------------------------------
SELECT view_date, metric_value AS views
FROM youtube.dimension_metrics_daily
WHERE report_type = 'device_type'
  AND dimension_value = 'Mobile phone'
  AND metric_name = 'views'
ORDER BY view_date;

-- ---------------------------------------------------------------------------
-- Q6: Views last 30 days (counter / single value)
-- ---------------------------------------------------------------------------
SELECT SUM(views) AS views_last_30_days
FROM youtube.viewership_daily
WHERE view_date >= CURRENT_DATE - INTERVAL '30 days';

-- ---------------------------------------------------------------------------
-- Q7: Audience demographics (table)
-- ---------------------------------------------------------------------------
SELECT report_type, dimension_value, views_pct, watch_time_pct
FROM youtube.dimension_snapshots
WHERE report_type IN ('viewer_age', 'viewer_gender')
ORDER BY report_type, views_pct DESC NULLS LAST;

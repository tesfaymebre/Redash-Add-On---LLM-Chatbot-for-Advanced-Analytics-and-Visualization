# Task 2: YouTube Analytics Database Schema

## 1. What Task 2 Delivers

| Step | Deliverable | Status |
|------|-------------|--------|
| **2a** (this step) | Data profile + schema design + DDL | In progress |
| 2b | ETL scripts to load `Data/` → PostgreSQL | Next |
| 2c | EDA notebook / summary statistics | Next |
| 2d | Redash data source connection guide | Next |

---

## 2. Raw Data Profile (`Data/`)

YouTube Studio exports **14 report dimensions**. Each folder contains up to three file types:

| File type | Grain | Typical columns | Use in analytics |
|-----------|-------|-----------------|------------------|
| **Table data.csv** | Period snapshot (no date column) | Dimension + Views + Watch time + Avg duration | Summary tables, pie/bar charts |
| **Chart data.csv** | Daily time series | Date + Dimension + metric (Views/Shares/Subscribers) | Line charts, trends |
| **Totals.csv** | Channel-level daily rollup | Date + single metric | Overall KPI trend |

**Channel totals (all Table data "Total" rows):** 26,625 views · 2,157.35 watch hours · ~4:51 avg duration  
**Date range (Totals / Chart data):** ~2020-06-28 → 2023-12-28 (~1,279 daily rows per series)

### Report inventory

| Report folder | Table rows | Chart rows | Totals rows | Notes |
|---------------|-----------|------------|-------------|-------|
| Viewership by Date | 503 | — | 1,280 | Core daily KPIs |
| Device type | 6 | 5,117 | 1,280 | Computer dominates (~72% views) |
| Geography | 31 | 37,092 | 1,280 | ISO country codes (ET top) |
| Cities | 10 | 6,396 | 1,280 | City name + Google place ID |
| Traffic source | 12 | 11,512 | 1,280 | Includes impressions + CTR |
| Operating system | 18 | 20,465 | 1,280 | |
| Content type | 4 | 2,559 | 1,280 | |
| Subscription status | 4 | 2,559 | 1,280 | Subscribed vs Not subscribed |
| Subscription source | 10 | 10,233 | 1,280 | Subscribers gained/lost |
| New and returning viewers | 5 | 3,838 | 1,280 | |
| Sharing service | 11 | 11,512 | 1,280 | Metric = Shares |
| Subtitles and CC | 10 | 10,233 | 1,280 | |
| Viewer age | 5 | — | — | Percentage-based metrics only |
| Viewer gender | 3 | — | — | Percentage-based metrics only |

### Data quality notes (for ETL)

1. **"Total" rows** in Table data are rollups — exclude on load (or load to separate summary table).
2. **`Average view duration`** is `H:MM:SS` text — parse to `INTEGER` seconds in ETL.
3. **Duplicate column** in Cities Table data: `Geography` appears twice — rename on ingest.
4. **Empty cells** in Traffic source (impressions for some rows) — store as `NULL`.
5. **Chart vs Table grain differs** — never join them without aggregating to a common grain.

---

## 3. Schema Design Decisions

### Why not one giant table?

YouTube exports are **heterogeneous** (different columns per report). A single "universal" table forces many NULL columns and confuses LLM text-to-SQL. We use a **hybrid model**:

```
┌─────────────────────────────────────────────────────────────┐
│  MART LAYER (what Redash + LLM query)                       │
├─────────────────────────────────────────────────────────────┤
│  viewership_daily          ← channel KPIs by date           │
│  dimension_metrics_daily   ← all Chart data (long format)   │
│  dimension_snapshots       ← all Table data (period totals)  │
│  report_metadata           ← LLM-friendly descriptions      │
└─────────────────────────────────────────────────────────────┘
```

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Long format for time series** | One `dimension_metrics_daily` table powers all "X over time" questions |
| **`report_type` discriminator** | LLM filters `WHERE report_type = 'device_type'` instead of guessing table names |
| **Snapshots separate from daily** | Avoids invalid joins between period summaries and daily data |
| **`report_metadata` table** | Business descriptions + example questions for RAG (Task 4) |
| **PostgreSQL** | Native Redash support, `information_schema` for agents, pgvector later |

### What about video-level metadata?

The challenge mentions video metadata, comments, and transcripts. Our `Data/` folder contains **channel-level YouTube Studio analytics exports** only — no per-video rows. The schema includes placeholder tables for future video-level data; they stay empty until that data is provided.

---

## 4. Entity Relationship (simplified)

```
report_metadata (1) ── describes ──> (N) dimension_metrics_daily
                                 └──> (N) dimension_snapshots

viewership_daily — standalone channel time series (from Viewership by Date)
```

There are **no foreign keys** between dimension reports (Geography ≠ Device type at row level). Cross-report analysis happens in SQL/Redash by aggregating channel totals or by date alignment.

---

## 5. Example Queries (validation targets for ETL + LLM)

```sql
-- Q1: Daily view trend (last 30 days)
SELECT view_date, views FROM youtube.viewership_daily
ORDER BY view_date DESC LIMIT 30;

-- Q2: Top 5 countries by views (snapshot)
SELECT dimension_value AS country, views
FROM youtube.dimension_snapshots
WHERE report_type = 'geography' AND dimension_value != 'Total'
ORDER BY views DESC LIMIT 5;

-- Q3: Mobile views trend in December 2023
SELECT view_date, metric_value AS views
FROM youtube.dimension_metrics_daily
WHERE report_type = 'device_type'
  AND dimension_value = 'Mobile phone'
  AND metric_name = 'views'
  AND view_date >= '2023-12-01'
ORDER BY view_date;

-- Q4: Traffic source with impressions
SELECT dimension_value, views, impressions, impressions_ctr_pct
FROM youtube.dimension_snapshots
WHERE report_type = 'traffic_source';
```

---

## 6. Redash Connection (preview for Step 2d)

Redash connects to PostgreSQL via **Data Source → PostgreSQL**:

| Setting | Value |
|---------|-------|
| Host | `localhost` (or `db` in docker-compose) |
| Port | `5433` (host; Docker maps to 5432 in container) |
| Database | `youtube_analytics` |
| User | `postgres` (read-only user `redash_reader` in production) |

Redash will introspect `youtube` schema tables for the query editor. Our LLM backend uses the same connection string, so **one source of truth** for both dashboards and chatbot.

---

## 7. Next Step (2b)

Implement `scripts/load_youtube_data.py` to:
1. Parse duration strings → seconds
2. Skip `Total` rows in Table data
3. Load Chart data → `dimension_metrics_daily`
4. Load Table data → `dimension_snapshots`
5. Seed `report_metadata` with descriptions

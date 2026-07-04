# Task 2d: Redash Data Source Connection Guide

Connect Redash to the YouTube analytics PostgreSQL mart built in Steps 2a–2c.

---

## 1. Why this step matters

Redash is the **visualization layer** of our project. The LLM chatbot (Tasks 3–4) will eventually:

- Run the **same SQL** Redash uses
- Summarize **existing dashboard widgets**
- Create **new queries** that land in this data source

One PostgreSQL database → one source of truth for dashboards and chat.

---

## 2. Prerequisites

Ensure data is loaded:

```bash
make db-up && make db-init && make db-load
```

Verify:

```bash
make db-psql
```

```sql
SELECT COUNT(*) FROM youtube.viewership_daily;        -- expect 500
SELECT COUNT(*) FROM youtube.dimension_snapshots;     -- expect ~105
```

---

## 3. Connection settings

### Option A — Postgres in Docker (`make db-up`), Redash on your Mac

Use this when Postgres runs via `make db-up` and Redash runs **natively on the host** (not in Docker):

| Field | Value |
|-------|-------|
| **Type** | PostgreSQL |
| **Name** | `YouTube Analytics` |
| **Host** | `localhost` |
| **Port** | `5433` |
| **User** | `postgres` |
| **Password** | `postgres` |
| **Database** | `youtube_analytics` |

Connection string:

```
postgresql://postgres:postgres@localhost:5433/youtube_analytics
```

### Option A′ — Both stacks in Docker (macOS dev setup)

If you installed Redash with `make up` in the `getredash/redash` repo, Redash runs **inside Docker**. From inside that container, `localhost` is the Redash container itself — **not** your Mac — so the test fails with *Connection refused*.

Use Docker Desktop's host alias instead:

| Field | Value |
|-------|-------|
| **Type** | PostgreSQL |
| **Name** | `YouTube Analytics` |
| **Host** | `host.docker.internal` |
| **Port** | `5433` |
| **User** | `postgres` |
| **Password** | `postgres` |
| **Database** | `youtube_analytics` |

Connection string:

```
postgresql://postgres:postgres@host.docker.internal:5433/youtube_analytics
```

> Port **5433** is the host mapping from our project's `infra/docker-compose.yml`. Inside the YouTube Postgres container it listens on 5432. We use 5433 on the host to avoid conflict with a local Postgres on 5432.

### Option B — Redash and Postgres both in Docker (Task 3+)

When Redash runs in the same `docker-compose` network:

| Field | Value |
|-------|-------|
| **Host** | `db` |
| **Port** | `5432` |
| **User** | `postgres` |
| **Password** | `postgres` |
| **Database** | `youtube_analytics` |

### Option C — Read-only user (recommended for demos / LLM agent)

Apply the reader role:

```bash
psql postgresql://postgres:postgres@localhost:5433/youtube_analytics \
  -f infra/sql/002_redash_reader.sql
```

| Field | Value |
|-------|-------|
| **User** | `redash_reader` |
| **Password** | `redash_reader` |

The LLM backend should use this role in production so generated SQL cannot mutate data.

---

## 4. Install Redash locally (if you don't have it yet)

Redash uses **two GitHub repos** — don't mix them up:

| Repo | Purpose | Has `setup.sh`? |
|------|---------|-----------------|
| [getredash/redash](https://github.com/getredash/redash) | Source code / **dev** Docker stack | No |
| [getredash/setup](https://github.com/getredash/setup) | Production Docker deploy (Linux servers) | Yes |

`setup.sh` was moved out of `getredash/redash` into `getredash/setup`. It also requires **Linux + root** and installs to `/opt/redash`, so it does **not** run on macOS.

### macOS — recommended dev setup

With [Docker Desktop](https://www.docker.com/products/docker-desktop/) running:

```bash
# In a separate folder (Redash is its own stack)
git clone https://github.com/getredash/redash.git
cd redash
make up
```

First run builds images and can take several minutes. Default UI: [http://localhost:5001](http://localhost:5001) (dev stack maps host **5001** → container 5000).

Create an admin account on first visit.

> **macOS note:** If the UI returns a 500 error about "no secret key", `make up` may have created an empty `.env` because `pwgen` is not installed by default. Fix with:
> ```bash
> cat > .env <<EOF
> REDASH_COOKIE_SECRET=$(openssl rand -hex 16)
> REDASH_SECRET_KEY=$(openssl rand -hex 16)
> EOF
> docker compose up -d --force-recreate server scheduler worker
> ```

> **Frontend missing (`client/dist/index.html`):** The dev `compose.yaml` skips the frontend build and mounts your local folder over `/app`. After `make up`, build the UI assets once:
> ```bash
> docker compose build --build-arg skip_frontend_build= server
> docker create --name redash-dist-tmp redash-server:latest
> docker cp redash-dist-tmp:/app/client/dist client/dist
> docker rm redash-dist-tmp
> docker compose up -d --force-recreate server scheduler worker
> ```

### Linux — production-style setup

```bash
git clone https://github.com/getredash/setup.git
cd setup
sudo ./setup.sh
```

Default UI: [http://localhost:5000](http://localhost:5000)

### Connect to our database

1. **Settings** (gear) → **Data Sources** → **New Data Source**
2. Choose **PostgreSQL**
3. Enter settings from **Option A′** above (use `host.docker.internal` if Redash runs in Docker)
4. Click **Save**
5. Click **Test Connection** — should succeed

---

## 5. Schema visibility in Redash

Redash introspects tables in the `youtube` schema. You should see:

| Table | Use for |
|-------|---------|
| `youtube.viewership_daily` | Date-range channel KPIs |
| `youtube.dimension_snapshots` | Period summaries (geo, device, traffic…) |
| `youtube.dimension_metrics_daily` | Daily time series by dimension |
| `youtube.report_metadata` | Descriptions (for LLM context, not charts) |

**Search path tip:** Always qualify tables: `youtube.viewership_daily`, not bare `viewership_daily`.

---

## 6. Which table for which question?

This routing logic is what the LLM agent will learn in Task 4:

| User question pattern | Query table | Why |
|----------------------|-------------|-----|
| "Views last month", "daily trend" | `viewership_daily` | Has `view_date` — one row per day |
| "Top countries", "device split" | `dimension_snapshots` | Period totals, no date column |
| "Mobile views over time" | `dimension_metrics_daily` | Date + dimension + metric |
| "What columns exist for geography?" | `report_metadata` | Business docs |

Your answer from Step 2c was correct: **time-range questions → `viewership_daily`** because it carries `view_date`.

---

## 7. Create your first dashboard (15 min exercise)

Use queries from `docs/architecture/redash-starter-queries.sql`.

### Dashboard: YouTube Channel Overview

| Widget | Query | Visualization |
|--------|-------|---------------|
| Daily views | Q1 | Line chart (`view_date` × `views`) |
| Top countries | Q2 | Bar chart |
| Device mix | Q3 | Pie or bar |
| Traffic sources | Q4 | Table |
| 30-day views | Q6 | Counter |

**Steps:**

1. **Create New Query** → paste Q1 → **Execute** → **New Visualization** → Line
2. Repeat for Q2–Q4, Q6
3. **Create Dashboard** → **Add widget** for each query
4. Arrange and save as **YouTube Channel Overview**

Expected highlights (from EDA):

- Ethiopia (`ET`) top country
- Computer > Mobile devices
- Channel pages lead traffic sources

---

## 8. Redash capabilities relevant to our chatbot

| Redash feature | Chatbot integration (Task 3+) |
|----------------|--------------------------------|
| **Query editor** | Chat panel lives here — NL → SQL → execute |
| **Visualizations** | Chat summarizes chart data in context |
| **Dashboards** | "What does this dashboard show?" |
| **Query API** | Backend creates/runs queries programmatically |
| **Schema browser** | Same metadata LLM uses for text-to-SQL |
| **Parameters** | `{{ date_range }}` — chat can fill these later |

---

## 9. Troubleshooting

| Problem | Fix |
|---------|-----|
| Connection refused | If Redash runs in Docker, use **`host.docker.internal`** (not `localhost`) as the host. Also run `make db-up`. |
| Wrong port | Use **5433** from host, not 5432 |
| Empty tables | `make db-load` |
| Schema not listed | Qualify as `youtube.table_name` in SQL |
| SSL error | Disable SSL in Redash data source settings (local dev) |
| Permission denied | Re-run `002_redash_reader.sql` or use `postgres` user |

Test from terminal:

```bash
psql postgresql://postgres:postgres@localhost:5433/youtube_analytics \
  -c "SELECT COUNT(*) FROM youtube.viewership_daily;"
```

---

## 10. Makefile shortcuts

```bash
make db-up          # start Postgres
make db-init        # apply schema
make db-load        # load CSV data
make db-psql        # open SQL shell
make db-reader      # create redash_reader role
```

---

## 11. Task 2 complete — checklist

- [x] **2a** Schema design + DDL
- [x] **2b** ETL loader (`make db-load`)
- [x] **2c** EDA notebook + findings
- [x] **2d** Redash connection + starter dashboard queries

**Next:** **Task 3** — Redash chat add-on (React) + Quart backend API.

---

## References

- [Redash documentation](https://redash.io/help/)
- Project schema: `docs/architecture/database-schema.md`
- EDA findings: `docs/architecture/eda-findings.md`
- Starter SQL: `docs/architecture/redash-starter-queries.sql`

# Task 3: Redash Chat Add-on — Architecture

> **Step 3a** ✓ API contract + Quart backend stub  
> **Step 3b** ✓ Standalone React chat UI  
> **Step 3c** (next): Embed in Redash query editor  
> **Step 3d** (next): Dashboard widget context chat  

---

## 1. Design principle: thin add-on, smart backend

Unlike the Sample project (LLM inside `redash/handlers/chat.py`), we split layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Redash (React)          │  Our add-on (thin)               │
│  Query editor / Dashboard│  ChatPanel.jsx → fetch()         │
└──────────────────────────┴──────────────────────────────────┘
                                    │ HTTP JSON
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│  Quart backend (:8000)                                      │
│  POST /api/chat  →  route by intent  →  services            │
│    ├─ summarize (dashboard context)     Task 3d             │
│    ├─ sql (NL→SQL + execute)            Task 4              │
│    └─ insight (multi-step EDA)          Task 5              │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    PostgreSQL       OpenAI API      Redash API
    (youtube.*)      (Task 4)        (Task 5)
```

**Why:** Testable without Redash running, reusable API, clear Task 4/5 boundaries.

---

## 2. Docker networking recap

| Client location | Postgres host:port | Reason |
|-----------------|-------------------|--------|
| Your Mac (Redash native, psql) | `localhost:5433` | Host → published Docker port |
| Container on same network | `db:5432` | Docker DNS service name, internal port |
| Quart backend in compose | `db:5432` | Same network as Postgres |

`localhost` inside a container refers to **that container**, not your Mac — hence `db`, not `localhost`.

---

## 3. API contract (Step 3a)

### `POST /api/chat`

**Request:**

```json
{
  "question": "How many views came from mobile?",
  "context": {
    "type": "query_editor",
    "query_id": null,
    "query_sql": null,
    "dashboard_id": null,
    "widget_id": null,
    "data_source_id": null
  },
  "session_id": "optional-uuid-for-multi-turn"
}
```

| Field | Purpose |
|-------|---------|
| `question` | User's natural language input (required) |
| `context.type` | `query_editor` \| `dashboard_widget` — drives routing |
| `context.query_sql` | SQL behind a widget (for summarize/explain) |
| `session_id` | Conversation memory (Task 4) |

**Response (200):**

```json
{
  "answer": "Mobile phone accounts for 6,885 views (26% of total).",
  "sql": null,
  "route": "stub",
  "session_id": "abc-123"
}
```

| Field | When populated |
|-------|----------------|
| `answer` | Always — human-readable reply |
| `sql` | Task 4+ — generated SQL for Redash query editor |
| `route` | Which handler processed the request |

**Errors:**

| Code | Body | Cause |
|------|------|-------|
| 400 | `{"error": "question is required"}` | Missing/empty question |
| 500 | `{"error": "..."}` | Unhandled server error |

### `GET /health`

Unchanged — liveness probe for Docker/CI.

---

## 4. Backend module layout

```
backend/src/redash_chatbot/
├── app.py              # create_app(), CORS, register blueprints
├── config.py           # env-based settings
├── routes/
│   ├── health.py
│   └── chat.py         # POST /api/chat
└── services/
    └── chat_service.py # business logic (stub → LLM in Task 4)
```

---

## 5. Frontend layout (Step 3b preview)

```
frontend/
├── package.json
├── src/
│   ├── components/
│   │   └── ChatPanel.jsx    # reusable chat UI
│   ├── api/
│   │   └── chatClient.js    # fetch wrapper for /api/chat
│   └── index.jsx            # dev sandbox (standalone)
└── README.md
```

Redash fork integration (Step 3c) copies `ChatPanel.jsx` into `redash/client/app/...`.

---

## 6. Task 3 milestone map

| Step | Deliverable | LLM? |
|------|-------------|------|
| **3a** ✓ | Architecture + `/api/chat` stub + tests | No |
| **3b** ✓ | React ChatPanel + dev sandbox (`make frontend-dev`) | No |
| 3c | Redash query editor integration | No |
| 3d | Dashboard widget pop-up + context | No |
| Task 4 | LangChain SQL agent in `chat_service` | Yes |

---

## 7. Local dev (Step 3a)

```bash
make db-up db-load          # data layer
make run                    # Quart on :8000
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"How many views from mobile?"}'
```

---

## 8. Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://...@localhost:5433/youtube_analytics` | Postgres (Task 4) |
| `CORS_ORIGINS` | `*` | Allowed browser origins (Redash URL in prod) |
| `CHATBOT_BACKEND_URL` | `http://localhost:8000` | Used by frontend |
| `OPENAI_API_KEY` | — | Task 4 |

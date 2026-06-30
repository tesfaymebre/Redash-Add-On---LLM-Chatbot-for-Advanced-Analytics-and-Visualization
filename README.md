# Redash Add-On — LLM Chatbot for Advanced Analytics and Visualization

Natural-language chat add-on for Redash: summarize dashboards, explain query results, generate SQL, and build visualizations from YouTube analytics data.

## Architecture (planned)

| Layer | Stack | Responsibility |
|-------|-------|----------------|
| Frontend | React (Redash add-on) | Chat UI in query editor & dashboard widgets |
| Backend | Quart (async Python) | NL → SQL, insights, visualization specs |
| Intelligence | OpenAI + LangChain + vector DB | Schema-aware retrieval, prompt orchestration |
| Data | MySQL/PostgreSQL | YouTube metadata, time-series, comments, transcripts |
| Ops | Docker, GitHub Actions | CI (lint/test), CD (image builds) |

## Repository layout

```
backend/          # Quart API service
frontend/         # Redash React add-on (Task 3)
infra/            # docker-compose, deployment scripts
scripts/          # ETL and data-loading utilities
docs/             # research notes, architecture decisions
Data/             # raw YouTube CSV exports (local only, not committed)
```

## Quick start (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
hypercorn redash_chatbot.app:app --reload --bind 0.0.0.0:8000
```

Health check: `GET http://localhost:8000/health`

## Branch strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready releases |
| `dev` | Integration / staging |
| `feature/*`, `task/*`, `chore/*` | Short-lived work branches |

## License

Academic / challenge project — 10 Academy Cohort A.

# Frontend — Redash Chat Add-on

React chat UI for Redash (Task 3).

## Task 3 roadmap

| Step | Status | Deliverable |
|------|--------|-------------|
| 3a | Done | Quart `POST /api/chat` stub — see `docs/architecture/task-03-addon-architecture.md` |
| 3b | Next | Standalone `ChatPanel` React component |
| 3c | Planned | Embed in Redash query editor |
| 3d | Planned | Dashboard widget pop-up |

## Test backend (Step 3a)

```bash
make run

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"How many views from mobile?","context":{"type":"query_editor"}}'
```

The add-on calls `CHATBOT_BACKEND_URL/api/chat` — not Redash's internal Flask handlers.

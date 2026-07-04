# Frontend — Redash Chat Add-on

React chat UI for the Redash add-on (Task 3).

## Task 3 roadmap

| Step | Status | Deliverable |
|------|--------|-------------|
| 3a | Done | Quart `POST /api/chat` stub |
| 3b | Done | Standalone `ChatPanel` + dev sandbox |
| 3c | Done | Query editor embed — see `task-03c-redash-integration.md` |
| 3d | Done | Dashboard widget chat — see `task-03d-dashboard-widget-chat.md` |

## Quick start (Step 3b / 3d)

Terminal 1 — backend:

```bash
make run
```

Terminal 2 — frontend:

```bash
make frontend-dev
```

Open [http://localhost:5173](http://localhost:5173):

- **Query editor (3b)** — standalone chat panel
- **Dashboard widget (3d)** — mock chart + “Ask AI” modal

## Project structure

```
frontend/src/
├── api/chatClient.js       # fetch wrapper → POST /api/chat
├── components/
│   ├── ChatPanel.jsx       # reusable chat UI (embed in Redash in 3c)
│   └── ChatPanel.css
├── App.jsx                 # dev sandbox layout
└── main.jsx
```

## Configuration

Copy `frontend/.env.example` → `frontend/.env.local`:

```
VITE_CHATBOT_BACKEND_URL=http://localhost:8000
```

## Build for production

```bash
cd frontend && npm run build
```

Output: `frontend/dist/` — static assets for the Vite dev sandbox.

## Redash integration (Step 3c)

See [docs/architecture/task-03c-redash-integration.md](../docs/architecture/task-03c-redash-integration.md).

```bash
make redash-install REDASH_PATH=Sample/redash
cd Sample/redash
patch -p1 < ../../frontend/redash-integration/QuerySource.patch
patch -p1 < ../../frontend/redash-integration/QuerySource.less.patch
patch -p1 < ../../frontend/redash-integration/VisualizationWidget.patch
# Add window.CHATBOT_BACKEND_URL in client/app/config/index.js
yarn build
```

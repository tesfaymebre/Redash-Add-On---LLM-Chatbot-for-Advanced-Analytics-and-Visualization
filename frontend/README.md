# Frontend — Redash Chat Add-on

React chat UI for the Redash add-on (Task 3).

## Task 3 roadmap

| Step | Status | Deliverable |
|------|--------|-------------|
| 3a | Done | Quart `POST /api/chat` stub |
| 3b | Done | Standalone `ChatPanel` + dev sandbox |
| 3c | Next | Embed in Redash query editor |
| 3d | Planned | Dashboard widget pop-up |

## Quick start (Step 3b)

Terminal 1 — backend:

```bash
make run
```

Terminal 2 — frontend:

```bash
make frontend-dev
```

Open [http://localhost:5173](http://localhost:5173) and ask a question.

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

Output: `frontend/dist/` — static assets for Redash integration (Step 3c).

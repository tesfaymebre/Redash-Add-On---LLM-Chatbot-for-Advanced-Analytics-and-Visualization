# Task 3c: Embed Chat Add-on in Redash Query Editor

> **Goal:** Show `ChatPanel` beside the SQL editor in Redash, calling our **Quart backend** (not Redash's Flask `/api/chat`).

---

## 1. How Redash query editor is structured

```
QuerySource.jsx (page)
└── .row.editor
    ├── .query-editor-wrapper
    │   ├── QueryEditor (Ace SQL editor)
    │   └── QueryEditor.Controls (Execute, Save…)
    └── QueryEditorChatSidebar  ← we add this (Task 3c)
```

**Sample project's approach (what we improve):**

| Sample | Our approach |
|--------|--------------|
| `ChatBox` in global `ApplicationLayout` | Chat **inside query editor only** |
| Calls Redash `/api/chat` (Flask + OpenAI in-process) | Calls Quart `http://localhost:8000/api/chat` |
| No query context passed | Sends `query_sql`, `query_id`, `data_source_id` |

---

## 2. Integration architecture

```
Redash QuerySource.jsx
    └── QueryEditorChatSidebar
            └── ChatPanel (from Step 3b)
                    └── chatClient.js → POST /api/chat
                            └── Quart backend (:8000)
```

**Context sent to backend:**

```json
{
  "question": "Top 5 countries by views",
  "context": {
    "type": "query_editor",
    "query_id": 42,
    "query_sql": "SELECT ...",
    "data_source_id": 1
  },
  "session_id": "uuid-from-previous-turn"
}
```

Task 4 will use `query_sql` for follow-ups and `data_source_id` to pick the right schema.

---

## 3. Prerequisites

```bash
# Terminal 1 — backend (required for chat to respond)
make run
```

You need a **Redash clone** (use `Sample/redash` or official [getredash/redash](https://github.com/getredash/redash)).

Optional API smoke test:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"test","context":{"type":"query_editor"}}'
```

---

## 3b. Quick start checklist

> **Important:** Your running Redash Docker container mounts a specific folder (check with `docker inspect redash-server-1 --format '{{range .Mounts}}{{.Source}}{{end}}'`). Run `make redash-install` and `make redash-build` against **that** path — not necessarily `Sample/redash`.

| Step | Command / action | Notes |
|------|------------------|-------|
| 1 | `make run` | Backend on `:8000` |
| 2 | Find Docker Redash path | e.g. `~/Documents/tes/ML projects/redash` |
| 3 | `make redash-install REDASH_PATH="/path/to/your/redash"` | Copies chat components |
| 4 | Patch `QuerySource.jsx` + config (see §5) | Skip if already applied |
| 5 | `make redash-build REDASH_PATH="/path/to/your/redash"` | Rebuild frontend |
| 6 | Hard-refresh browser (`Cmd+Shift+R`) | |
| 7 | Open a query (not the list page) | **AI** tab appears on the right of the SQL editor |

---

## 4. Install add-on files (automated)

```bash
chmod +x frontend/redash-integration/install-to-redash.sh

# Using Sample fork:
./frontend/redash-integration/install-to-redash.sh Sample/redash

# Or your own clone:
./frontend/redash-integration/install-to-redash.sh ~/projects/redash
```

This copies to `client/app/components/chatbot/`:

- `ChatPanel.jsx` / `ChatPanel.css`
- `chatClient.js`
- `QueryEditorChatSidebar.jsx` / `.less`

---

## 5. Manual patches (3 files)

### 5a. Config — backend URL

**Edit the file** `Sample/redash/client/app/config/index.js` (do **not** paste this in the terminal):

```javascript
window.CHATBOT_BACKEND_URL = "http://localhost:8000";
```

Add it after the `import "./antd-spinner";` line. See `frontend/redash-integration/config.snippet.js`.

| Redash runs on | Backend URL |
|----------------|-------------|
| Mac (native), backend on Mac | `http://localhost:8000` |
| Docker compose (same network) | `http://backend:8000` |

### 5b. QuerySource.jsx

> **Already patched?** If `patch` prints `Reversed (or previously applied) patch detected`, answer **`n`** and skip this step — your files are already updated.

Apply `frontend/redash-integration/QuerySource.patch`:

```bash
cd Sample/redash
patch -p1 < ../../frontend/redash-integration/QuerySource.patch
```

Or apply manually:

1. **Import** at top of `QuerySource.jsx`:

```javascript
import QueryEditorChatSidebar from "@/components/chatbot/QueryEditorChatSidebar";
```

2. **Add class** `editor-with-chatbot` to the editor row div.

3. **Insert sidebar** after `</section>` closing `query-editor-wrapper`:

```jsx
<QueryEditorChatSidebar
  query={query}
  dataSourceId={dataSource ? dataSource.id : null}
  onQueryChange={(sql) => {
    handleQueryEditorChange(sql);
    editorRef.current?.editor?.setValue(sql, -1);
  }}
/>
```

The `onQueryChange` callback updates both Redash state and the Ace editor — so when Task 4 returns SQL, it appears in the editor.

### 5c. QuerySource.less

Apply `QuerySource.less.patch` for flex layout (editor + sidebar side-by-side).

---

## 6. Rebuild Redash frontend

Redash requires **Node 16** (see `Sample/redash/.nvmrc`). Node 18+ will fail with an engine error.

```bash
cd Sample/redash

# Option A — nvm (recommended)
nvm install 16
nvm use 16

# Option B — Node 18+ (workarounds for old Redash webpack)
# Add to Sample/redash/.yarnrc:  ignore-engines true
PUPPETEER_SKIP_DOWNLOAD=true yarn install
PUPPETEER_SKIP_DOWNLOAD=true NODE_OPTIONS=--openssl-legacy-provider yarn build

# Or from repo root (applies both workarounds automatically):
make redash-build

# Normal install (Node 16 active)
yarn install
yarn build
```

Restart Redash. Open any query → you should see an **AI** tab on the right of the SQL editor.

---

## 7. Verify integration

| Check | Expected |
|-------|----------|
| Sidebar visible in query editor | Collapsible "AI" strip on the right |
| Send message | Stub reply from Quart backend |
| Browser network tab | `POST http://localhost:8000/api/chat` (not Redash origin) |
| Context in request body | `query_sql`, `data_source_id` populated |
| CORS | No browser error (backend sends `Access-Control-Allow-Origin`) |

**Common issues:**

| Problem | Fix |
|---------|-----|
| `zsh: command not found: window.CHATBOT_BACKEND_URL` | You pasted JS in the terminal — edit `client/app/config/index.js` instead |
| `Reversed (or previously applied) patch` | Patches already applied — skip step 5b/5c |
| `engine "node" is incompatible` on `yarn build` | Add `ignore-engines true` to `Sample/redash/.yarnrc` — `make redash-build` does this |
| `digital envelope routines::unsupported` (OpenSSL) | `NODE_OPTIONS=--openssl-legacy-provider` — included in `make redash-build` |
| `React is not defined` in ChatPanel | Redash needs `import React from "react"` — fixed in source; re-run install + build |
| Puppeteer / chromium arm64 error during install | `PUPPETEER_SKIP_DOWNLOAD=true yarn install --ignore-engines` |
| `ENOSPC: no space left on device` | Free disk space, then re-run `make redash-build` |
| CORS error | Ensure `make run` is active; check `CORS_ORIGINS` in backend |
| Connection refused | Backend not running on :8000 |
| Sidebar empty / 404 on chat | Files not copied; re-run install script |
| Built `Sample/redash` but Docker uses another folder | Check mount: `docker inspect redash-server-1 --format '{{range .Mounts}}{{.Source}}{{end}}'` |
| Sidebar only on query **editor** | Open **New Query** or click a query name — not visible on the queries list page |
| SQL not updating editor | Check `editorRef.current?.editor?.setValue` in patch |

---

## 8. Comparison: Sample vs our integration

```6:26:Sample/redash/client/app/components/ApplicationArea/ApplicationLayout/index.jsx
import ChatBox from "@/components/chat/chat/ChatBox";
// ...
<DynamicComponent name="ApplicationDesktopChat">
  <ChatBox/>
</DynamicComponent>
```

Sample mounts chat **globally**. We mount **only in the query editor** with richer context — better UX and closer to the challenge requirement.

---

## 9. Task 3 progress

| Step | Status |
|------|--------|
| 3a API stub | ✓ |
| 3b React ChatPanel | ✓ |
| **3c Query editor embed** | ✓ (this guide) |
| 3d Dashboard widget chat | Next |

---

## 10. Makefile shortcut

```bash
make redash-install REDASH_PATH=Sample/redash
```

Then apply patches and rebuild Redash manually (steps 5–6).

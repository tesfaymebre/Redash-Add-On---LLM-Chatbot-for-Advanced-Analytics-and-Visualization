# Task 3d: Dashboard Widget Chat Pop-up

> **Goal:** Let users ask questions about a specific dashboard visualization. The chat modal sends widget SQL, metadata, and a preview of result rows to the Quart backend.

---

## 1. How it fits Task 3

| Step | Where | Context type |
|------|-------|--------------|
| 3b | Vite dev sandbox | `query_editor` or `dashboard_widget` |
| 3c | Query editor sidebar | `query_editor` |
| **3d** | Dashboard widget footer → modal | `dashboard_widget` |

```
Dashboard page
└── VisualizationWidget
    └── footer: "Ask AI" button (comment icon)
            └── DashboardWidgetChatDialog (modal)
                    └── ChatPanel → POST /api/chat
```

---

## 2. Context payload

When a user opens chat from a widget, the frontend sends:

```json
{
  "question": "Summarize this chart",
  "context": {
    "type": "dashboard_widget",
    "dashboard_id": 7,
    "widget_id": 101,
    "query_id": 42,
    "query_name": "Top Countries by Views",
    "query_sql": "SELECT ...",
    "data_source_id": 1,
    "visualization_type": "CHART",
    "visualization_name": "Bar Chart",
    "result_preview": {
      "columns": ["country_code", "views"],
      "rows": [{ "country_code": "ET", "views": 8420 }],
      "total_rows": 8
    }
  },
  "session_id": "uuid-from-prior-turn"
}
```

| Field | Purpose |
|-------|---------|
| `query_sql` | SQL behind the chart (Task 4 explain / refine) |
| `result_preview` | First 5 rows + column names (Task 4 summarize) |
| `visualization_*` | Chart type for routing (Task 5 viz suggestions) |
| `session_id` | Multi-turn conversation memory (Task 4) |

Backend stub returns `route: "stub_dashboard"` when `context.type === "dashboard_widget"`.

---

## 3. Dev sandbox (no Redash required)

```bash
make run              # Terminal 1 — Quart :8000
make frontend-dev     # Terminal 2 — Vite :5173
```

Open [http://localhost:5173](http://localhost:5173) → tab **Dashboard widget (3d)** → click **Ask AI about this chart**.

The mock widget simulates Redash's `widget.getQuery()` / `getQueryResult()` API using sample geography data.

---

## 4. Redash integration

### 4a. Install chatbot files

```bash
make redash-install REDASH_PATH=Sample/redash
```

Copies to `client/app/components/chatbot/`:

- `DashboardWidgetChatDialog.jsx` / `.less`
- `src/lib/widgetContext.js` (copied to Redash on install)
- (plus Step 3c files: `ChatPanel`, `QueryEditorChatSidebar`, `chatClient.js`)

### 4b. Apply patches

```bash
cd Sample/redash
patch -p1 < ../../frontend/redash-integration/QuerySource.patch
patch -p1 < ../../frontend/redash-integration/QuerySource.less.patch
patch -p1 < ../../frontend/redash-integration/VisualizationWidget.patch
```

**VisualizationWidget.patch** adds:

1. Import `DashboardWidgetChatDialog`
2. Comment icon button in widget footer (next to fullscreen)
3. `openWidgetChat()` → `DashboardWidgetChatDialog.showModal({ widget, dashboard })`

### 4c. Config

In `client/app/config/index.js`:

```javascript
window.CHATBOT_BACKEND_URL = "http://localhost:8000";
```

### 4d. Rebuild

```bash
cd Sample/redash
yarn build
```

Open a dashboard with a chart widget → click the **comment** icon in the widget footer → chat modal opens.

---

## 5. Verify

| Check | Expected |
|-------|----------|
| Comment button visible on widget footer | Only on non-public dashboards |
| Modal title | Visualization name + query name |
| Network tab | `POST http://localhost:8000/api/chat` |
| Request body | `context.type: "dashboard_widget"`, `result_preview` populated |
| Response | `route: "stub_dashboard"`, mentions query name |
| Multi-turn | Same `session_id` on follow-up messages |

---

## 6. Comparison: Sample vs our approach

| Sample `ChatBox` | Our Step 3d |
|------------------|-------------|
| Global floating chat, no widget context | Per-widget modal with SQL + data preview |
| Calls Redash `/api/chat` | Calls Quart backend |
| Same UI everywhere | Query editor sidebar (3c) vs widget modal (3d) |

---

## 7. Task 3 complete

| Step | Status |
|------|--------|
| 3a API stub | ✓ |
| 3b React ChatPanel | ✓ |
| 3c Query editor embed | ✓ |
| **3d Dashboard widget chat** | ✓ |
| Task 4 NL→SQL + memory | Next |

---

## 8. Files reference

```
frontend/src/lib/
├── widgetContext.js                # buildWidgetChatContext() — copied to Redash on install

frontend/redash-integration/

frontend/src/components/
├── DashboardWidgetDemo.jsx         # Dev sandbox mock widget
└── ChatPanel.jsx                   # + welcomeMessage prop
```

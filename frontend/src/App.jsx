import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import DashboardWidgetDemo from "./components/DashboardWidgetDemo";
import { CHATBOT_BACKEND_URL } from "./api/chatClient";
import "./App.css";

const MODES = {
  query: "query_editor",
  dashboard: "dashboard_widget",
};

/**
 * Dev sandbox — simulates chat add-on outside Redash (Steps 3b + 3d).
 */
export default function App() {
  const [mode, setMode] = useState(MODES.query);

  return (
    <div className="sandbox">
      <aside className="sandbox__sidebar">
        <h1>Redash Chat Add-on</h1>
        <p className="sandbox__subtitle">Task 3 — dev sandbox</p>

        <div className="sandbox__tabs">
          <button
            type="button"
            className={mode === MODES.query ? "sandbox__tab sandbox__tab--active" : "sandbox__tab"}
            onClick={() => setMode(MODES.query)}
          >
            Query editor (3b)
          </button>
          <button
            type="button"
            className={mode === MODES.dashboard ? "sandbox__tab sandbox__tab--active" : "sandbox__tab"}
            onClick={() => setMode(MODES.dashboard)}
          >
            Dashboard widget (3d)
          </button>
        </div>

        <dl className="sandbox__meta">
          <dt>Backend</dt>
          <dd>{CHATBOT_BACKEND_URL}</dd>
          <dt>Endpoint</dt>
          <dd>POST /api/chat</dd>
          <dt>Context</dt>
          <dd>{mode}</dd>
        </dl>

        <section className="sandbox__hints">
          <h2>Try asking</h2>
          <ul>
            {mode === MODES.query ? (
              <>
                <li>How many views from mobile?</li>
                <li>Which country has the most views?</li>
                <li>Show daily view trend</li>
              </>
            ) : (
              <>
                <li>Summarize this chart</li>
                <li>Which country leads?</li>
                <li>What insight stands out?</li>
              </>
            )}
          </ul>
        </section>

        <p className="sandbox__note">
          Start backend: <code>make run</code>
        </p>
      </aside>

      <main className="sandbox__chat">
        {mode === MODES.query ? (
          <ChatPanel
            contextType="query_editor"
            title="YouTube Analytics Assistant"
            placeholder="e.g. How many views from mobile?"
          />
        ) : (
          <DashboardWidgetDemo />
        )}
      </main>
    </div>
  );
}

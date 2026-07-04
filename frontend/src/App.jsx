import ChatPanel from "./components/ChatPanel";
import { CHATBOT_BACKEND_URL } from "./api/chatClient";
import "./App.css";

/**
 * Dev sandbox — simulates the chat add-on outside Redash.
 * Step 3c will embed ChatPanel inside Redash's query editor.
 */
export default function App() {
  return (
    <div className="sandbox">
      <aside className="sandbox__sidebar">
        <h1>Redash Chat Add-on</h1>
        <p className="sandbox__subtitle">Task 3b — standalone dev sandbox</p>

        <dl className="sandbox__meta">
          <dt>Backend</dt>
          <dd>{CHATBOT_BACKEND_URL}</dd>
          <dt>Endpoint</dt>
          <dd>POST /api/chat</dd>
        </dl>

        <section className="sandbox__hints">
          <h2>Try asking</h2>
          <ul>
            <li>How many views from mobile?</li>
            <li>Which country has the most views?</li>
            <li>Show daily view trend</li>
          </ul>
        </section>

        <p className="sandbox__note">
          Start backend: <code>make run</code>
        </p>
      </aside>

      <main className="sandbox__chat">
        <ChatPanel
          contextType="query_editor"
          title="YouTube Analytics Assistant"
          placeholder="e.g. How many views from mobile?"
        />
      </main>
    </div>
  );
}

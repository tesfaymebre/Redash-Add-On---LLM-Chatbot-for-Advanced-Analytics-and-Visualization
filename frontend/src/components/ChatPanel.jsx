import React, { useCallback, useEffect, useRef, useState } from "react";
import { sendChatMessage, CHATBOT_BACKEND_URL } from "../api/chatClient";
import "./ChatPanel.css";

/**
 * Reusable chat panel for Redash add-on (Step 3b).
 *
 * Props:
 *   contextType  - "query_editor" | "dashboard_widget"
 *   backendUrl   - Quart API base URL
 *   title        - Panel header text
 *   placeholder  - Input placeholder
 *   onSqlGenerated - callback when backend returns SQL (Task 4)
 */
export default function ChatPanel({
  contextType = "query_editor",
  contextExtras = {},
  backendUrl = CHATBOT_BACKEND_URL,
  title = "Analytics Assistant",
  placeholder = "Ask about your data…",
  onSqlGenerated = null,
}) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! Ask a question about your YouTube analytics. I'll generate SQL and insights once Task 4 is connected.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const listRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSubmit = useCallback(
    async (event) => {
      event.preventDefault();
      const question = input.trim();
      if (!question || loading) return;

      setInput("");
      setError(null);
      setMessages((prev) => [...prev, { role: "user", content: question }]);
      setLoading(true);

      try {
        const data = await sendChatMessage({
          question,
          context: { type: contextType, ...contextExtras },
          sessionId,
          backendUrl,
        });

        if (data.session_id) setSessionId(data.session_id);

        setMessages((prev) => [...prev, { role: "assistant", content: data.answer }]);

        if (data.sql && onSqlGenerated) {
          onSqlGenerated(data.sql);
        }
      } catch (err) {
        const message = err.message || "Something went wrong";
        setError(message);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Error: ${message}` },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [input, loading, sessionId, contextType, contextExtras, backendUrl, onSqlGenerated],
  );

  return (
    <div className="chat-panel" role="region" aria-label={title}>
      <header className="chat-panel__header">
        <span className="chat-panel__title">{title}</span>
        <span className="chat-panel__badge">{contextType.replace("_", " ")}</span>
      </header>

      <div className="chat-panel__messages" ref={listRef}>
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-panel__message chat-panel__message--${msg.role}`}
          >
            <span className="chat-panel__role">
              {msg.role === "user" ? "You" : "Assistant"}
            </span>
            <p>{msg.content}</p>
          </div>
        ))}
        {loading && (
          <div className="chat-panel__message chat-panel__message--assistant">
            <span className="chat-panel__role">Assistant</span>
            <p className="chat-panel__typing">Thinking…</p>
          </div>
        )}
      </div>

      {error && <div className="chat-panel__error">{error}</div>}

      <form className="chat-panel__form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          disabled={loading}
          aria-label="Chat message"
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

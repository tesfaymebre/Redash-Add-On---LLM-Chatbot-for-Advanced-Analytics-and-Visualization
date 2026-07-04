/**
 * HTTP client for the Quart chatbot backend.
 * Used by ChatPanel and later embedded in Redash (Step 3c).
 */

const DEFAULT_BACKEND =
  import.meta.env.VITE_CHATBOT_BACKEND_URL || "http://localhost:8000";

/**
 * Send a chat message to POST /api/chat.
 *
 * @param {object} params
 * @param {string} params.question - User question (required)
 * @param {object} [params.context] - Redash context (query_editor | dashboard_widget)
 * @param {string} [params.sessionId] - Conversation id for multi-turn
 * @param {string} [params.backendUrl] - Override backend base URL
 * @returns {Promise<{answer: string, sql: string|null, route: string, session_id: string}>}
 */
export async function sendChatMessage({
  question,
  context = { type: "query_editor" },
  sessionId = null,
  backendUrl = DEFAULT_BACKEND,
}) {
  const url = `${backendUrl.replace(/\/$/, "")}/api/chat`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      context,
      session_id: sessionId,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }

  return data;
}

export { DEFAULT_BACKEND as CHATBOT_BACKEND_URL };

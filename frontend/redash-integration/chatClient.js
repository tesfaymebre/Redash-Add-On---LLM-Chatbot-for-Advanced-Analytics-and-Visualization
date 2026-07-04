/**
 * HTTP client for the Quart chatbot backend (Redash/webpack build).
 * Vite sandbox uses frontend/src/api/chatClient.js instead.
 */

const DEFAULT_BACKEND =
  (typeof window !== "undefined" && window.CHATBOT_BACKEND_URL) ||
  "http://localhost:8000";

/**
 * @param {object} params
 * @param {string} params.question
 * @param {object} [params.context]
 * @param {string|null} [params.sessionId]
 * @param {string} [params.backendUrl]
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

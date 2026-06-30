"""
Minimal Quart application — foundation for Task 3+ backend work.

Why Quart (not Flask)?
  The challenge specifies Quart as the async sibling of Flask. Async I/O matters
  when we fan out to OpenAI, the database, and Redash APIs concurrently.
"""

from quart import Quart, jsonify

app = Quart(__name__)


@app.get("/health")
async def health():
    """Liveness probe used by Docker and CI smoke checks."""
    return jsonify({"status": "ok", "service": "redash-chatbot-backend"}), 200

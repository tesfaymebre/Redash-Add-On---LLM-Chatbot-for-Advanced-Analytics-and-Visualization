"""
Quart application factory for the Redash chatbot backend.

Step 3a: health + chat stub with CORS for browser-based add-on.
"""

from quart import Quart, Response

from redash_chatbot.config import settings
from redash_chatbot.routes.chat import chat_bp
from redash_chatbot.routes.health import health_bp


def _apply_cors(response: Response) -> Response:
    """Allow Redash frontend (different origin) to call the API."""
    origin = settings.CORS_ORIGINS
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def create_app() -> Quart:
    app = Quart(__name__)
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)

    @app.after_request
    async def add_cors_headers(response: Response) -> Response:
        return _apply_cors(response)

    @app.route("/api/chat", methods=["OPTIONS"])
    async def chat_preflight():
        return _apply_cors(Response("", status=204))

    return app


# ASGI entrypoint for hypercorn / tests
app = create_app()

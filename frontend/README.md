# Frontend — Redash Chat Add-on

React components that extend the Redash UI:

- Persistent chat panel in the query editor
- Contextual pop-up chat beside dashboard visualizations

Implementation starts in **Task 3**. The add-on will call the Quart backend at `/api/chat` (and related routes).

Reference: Sample project embeds chat in `redash/redash/handlers/chat.py` — we will separate concerns properly (thin Redash handler → dedicated backend service).

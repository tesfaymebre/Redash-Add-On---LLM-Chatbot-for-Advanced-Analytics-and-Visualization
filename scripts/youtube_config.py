"""Shared YouTube Data/ folder → database mappings (Task 2)."""

from __future__ import annotations

from datetime import date

import pandas as pd

# Data/ folder name → youtube.report_type slug
REPORT_SLUGS: dict[str, str] = {
    "Viewership by Date": "viewership_daily",
    "Device type": "device_type",
    "Geography": "geography",
    "Cities": "cities",
    "Traffic source": "traffic_source",
    "Operating system": "operating_system",
    "Content type": "content_type",
    "Subscription status": "subscription_status",
    "Subscription source": "subscription_source",
    "New and returning viewers": "new_returning_viewers",
    "Sharing service": "sharing_service",
    "Subtitles and CC": "subtitles_cc",
    "Viewer age": "viewer_age",
    "Viewer gender": "viewer_gender",
}

# Chart data.csv metric column → normalized metric_name
CHART_METRIC_COLUMNS: dict[str, str] = {
    "Views": "views",
    "Shares": "shares",
    "Subscribers": "subscribers",
}


def parse_duration_seconds(value: object) -> int | None:
    """Convert YouTube duration strings (H:MM:SS or M:SS) to seconds."""
    if value is None or (isinstance(value, float) and value != value):  # NaN
        return None
    text = str(value).strip()
    if not text or text.lower() == "total":
        return None
    parts = text.split(":")
    try:
        if len(parts) == 3:
            hours, minutes, seconds = (int(p) for p in parts)
            return hours * 3600 + minutes * 60 + seconds
        if len(parts) == 2:
            minutes, seconds = (int(p) for p in parts)
            return minutes * 60 + seconds
    except ValueError:
        return None
    return None


def safe_int(value: object) -> int | None:
    if value is None or (isinstance(value, float) and value != value):
        return None
    text = str(value).strip()
    if not text:
        return None
    return int(float(text))


def safe_float(value: object) -> float | None:
    if value is None or (isinstance(value, float) and value != value):
        return None
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def is_total_row(dimension_value: object) -> bool:
    return str(dimension_value).strip().lower() == "total"


def parse_date(value: object) -> date | None:
    """Parse date column; return None for footers like 'Showing top 500 results'."""
    if value is None or (isinstance(value, float) and value != value):
        return None
    text = str(value).strip()
    if not text or text.lower().startswith("showing"):
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def normalize_dimension_value(value: object) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "(unknown)"
    text = str(value).strip()
    return text if text else "(unknown)"

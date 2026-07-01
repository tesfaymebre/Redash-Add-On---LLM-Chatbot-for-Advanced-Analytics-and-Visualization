"""Unit tests for ETL helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from youtube_config import parse_duration_seconds, safe_int  # noqa: E402


def test_parse_duration_hms():
    assert parse_duration_seconds("0:04:51") == 291
    assert parse_duration_seconds("0:05:19") == 319


def test_parse_duration_ms():
    assert parse_duration_seconds("5:21") == 321


def test_parse_duration_empty():
    assert parse_duration_seconds("") is None
    assert parse_duration_seconds(None) is None


def test_safe_int():
    assert safe_int("1252") == 1252
    assert safe_int("") is None

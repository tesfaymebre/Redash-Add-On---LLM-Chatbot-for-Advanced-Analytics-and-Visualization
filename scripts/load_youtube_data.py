#!/usr/bin/env python3
"""
Task 2b — Load YouTube Studio CSV exports into PostgreSQL.

Run from repo root:
    make db-load
    python scripts/load_youtube_data.py --database-url "$DATABASE_URL"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow `python scripts/load_youtube_data.py` without installing as a package
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from youtube_config import (
    CHART_METRIC_COLUMNS,
    REPORT_SLUGS,
    is_total_row,
    normalize_dimension_value,
    parse_date,
    parse_duration_seconds,
    safe_float,
    safe_int,
)

DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5433/youtube_analytics"


def get_connection(database_url: str):
    return psycopg2.connect(database_url)


def truncate_tables(conn) -> None:
    """Clear loaded data; preserve report_metadata seeds."""
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                youtube.video_metrics_daily,
                youtube.videos,
                youtube.dimension_metrics_daily,
                youtube.dimension_snapshots,
                youtube.viewership_daily
            RESTART IDENTITY CASCADE
            """
        )
    conn.commit()


def load_viewership_daily(conn, path: Path) -> int:
    df = pd.read_csv(path)
    rows: list[tuple] = []

    for _, row in df.iterrows():
        if is_total_row(row["Date"]):
            continue
        view_date = parse_date(row["Date"])
        views = safe_int(row["Views"])
        if view_date is None or views is None:
            continue
        rows.append(
            (
                view_date,
                views,
                safe_float(row["Watch time (hours)"]),
                parse_duration_seconds(row["Average view duration"]),
            )
        )

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO youtube.viewership_daily
                (view_date, views, watch_time_hours, avg_view_duration_sec)
            VALUES %s
            ON CONFLICT (view_date) DO UPDATE SET
                views = EXCLUDED.views,
                watch_time_hours = EXCLUDED.watch_time_hours,
                avg_view_duration_sec = EXCLUDED.avg_view_duration_sec
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def load_chart_data(conn, report_type: str, path: Path) -> int:
    df = pd.read_csv(path)
    metric_col = next((c for c in CHART_METRIC_COLUMNS if c in df.columns), None)
    if metric_col is None:
        raise ValueError(f"No known metric column in {path}")

    metric_name = CHART_METRIC_COLUMNS[metric_col]
    dimension_col = [c for c in df.columns if c not in ("Date", metric_col)][0]

    rows: list[tuple] = []
    for _, row in df.iterrows():
        view_date = parse_date(row["Date"])
        metric_value = safe_float(row[metric_col])
        if view_date is None or metric_value is None:
            continue
        rows.append(
            (
                view_date,
                report_type,
                normalize_dimension_value(row[dimension_col]),
                metric_name,
                metric_value,
            )
        )

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO youtube.dimension_metrics_daily
                (view_date, report_type, dimension_value, metric_name, metric_value)
            VALUES %s
            ON CONFLICT (view_date, report_type, dimension_value, metric_name)
            DO UPDATE SET metric_value = EXCLUDED.metric_value
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def load_table_snapshot(conn, report_type: str, path: Path) -> int:
    df = pd.read_csv(path)
    dim_col = df.columns[0]
    rows: list[tuple] = []

    for _, row in df.iterrows():
        if is_total_row(row[dim_col]):
            continue

        record = _snapshot_record(report_type, dim_col, row)
        if record:
            rows.append(record)

    if not rows:
        return 0

    columns = [
        "report_type",
        "dimension_value",
        "views",
        "watch_time_hours",
        "avg_view_duration_sec",
        "shares",
        "impressions",
        "impressions_ctr_pct",
        "subscribers",
        "subscribers_gained",
        "subscribers_lost",
        "views_pct",
        "watch_time_pct",
        "avg_pct_viewed",
        "city_place_id",
        "geography_code",
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            f"""
            INSERT INTO youtube.dimension_snapshots
                ({", ".join(columns)})
            VALUES %s
            ON CONFLICT (report_type, dimension_value) DO UPDATE SET
                views = EXCLUDED.views,
                watch_time_hours = EXCLUDED.watch_time_hours,
                avg_view_duration_sec = EXCLUDED.avg_view_duration_sec,
                shares = EXCLUDED.shares,
                impressions = EXCLUDED.impressions,
                impressions_ctr_pct = EXCLUDED.impressions_ctr_pct,
                subscribers = EXCLUDED.subscribers,
                subscribers_gained = EXCLUDED.subscribers_gained,
                subscribers_lost = EXCLUDED.subscribers_lost,
                views_pct = EXCLUDED.views_pct,
                watch_time_pct = EXCLUDED.watch_time_pct,
                avg_pct_viewed = EXCLUDED.avg_pct_viewed,
                city_place_id = EXCLUDED.city_place_id,
                geography_code = EXCLUDED.geography_code
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def _snapshot_record(report_type: str, dim_col: str, row: pd.Series) -> tuple | None:
    """Map a Table data.csv row to dimension_snapshots insert tuple."""
    if report_type == "cities":
        return (
            report_type,
            normalize_dimension_value(row["City name"]),
            safe_int(row.get("Views")),
            safe_float(row.get("Watch time (hours)")),
            parse_duration_seconds(row.get("Average view duration")),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            normalize_dimension_value(row["Cities"]),
            str(row.get("Geography", "")).strip() or None,
        )

    if report_type == "sharing_service":
        return (
            report_type,
            normalize_dimension_value(row[dim_col]),
            None,
            None,
            None,
            safe_int(row.get("Shares")),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    if report_type == "subscription_source":
        return (
            report_type,
            normalize_dimension_value(row[dim_col]),
            None,
            None,
            None,
            None,
            None,
            None,
            safe_int(row.get("Subscribers")),
            safe_int(row.get("Subscribers gained")),
            safe_int(row.get("Subscribers lost")),
            None,
            None,
            None,
            None,
            None,
        )

    if report_type in ("viewer_age", "viewer_gender"):
        return (
            report_type,
            normalize_dimension_value(row[dim_col]),
            None,
            None,
            parse_duration_seconds(row.get("Average view duration")),
            None,
            None,
            None,
            None,
            None,
            None,
            safe_float(row.get("Views (%)")),
            safe_float(row.get("Watch time (hours) (%)")),
            safe_float(row.get("Average percentage viewed (%)")),
            None,
            None,
        )

    if report_type == "traffic_source":
        return (
            report_type,
            normalize_dimension_value(row[dim_col]),
            safe_int(row.get("Views")),
            safe_float(row.get("Watch time (hours)")),
            parse_duration_seconds(row.get("Average view duration")),
            None,
            safe_int(row.get("Impressions")),
            safe_float(row.get("Impressions click-through rate (%)")),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    # Standard dimension table: Views + Watch time + Avg duration
    return (
        report_type,
        normalize_dimension_value(row[dim_col]),
        safe_int(row.get("Views")),
        safe_float(row.get("Watch time (hours)")),
        parse_duration_seconds(row.get("Average view duration")),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def validate_load(conn) -> dict[str, int | float]:
    """Sanity checks after load."""
    checks: dict[str, int | float] = {}
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM youtube.viewership_daily")
        checks["viewership_daily_rows"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM youtube.dimension_metrics_daily")
        checks["dimension_metrics_daily_rows"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM youtube.dimension_snapshots")
        checks["dimension_snapshots_rows"] = cur.fetchone()[0]

        cur.execute(
            """
            SELECT views FROM youtube.dimension_snapshots
            WHERE report_type = 'device_type' AND dimension_value = 'Computer'
            """
        )
        row = cur.fetchone()
        checks["computer_views_snapshot"] = row[0] if row else 0

        cur.execute(
            """
            SELECT SUM(views) FROM youtube.viewership_daily
            WHERE view_date >= '2023-01-01'
            """
        )
        checks["views_2023_sum"] = float(cur.fetchone()[0] or 0)

    return checks


def load_all(data_dir: Path, database_url: str, truncate: bool = True) -> None:
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    conn = get_connection(database_url)
    try:
        if truncate:
            print("Truncating existing data tables...")
            truncate_tables(conn)

        totals = {"viewership": 0, "chart": 0, "snapshot": 0}

        for folder_name, report_type in REPORT_SLUGS.items():
            folder = data_dir / folder_name
            if not folder.is_dir():
                print(f"  SKIP missing folder: {folder_name}")
                continue

            table_path = folder / "Table data.csv"
            chart_path = folder / "Chart data.csv"

            if report_type == "viewership_daily" and table_path.exists():
                n = load_viewership_daily(conn, table_path)
                totals["viewership"] += n
                print(f"  viewership_daily: {n} rows")

            elif table_path.exists():
                n = load_table_snapshot(conn, report_type, table_path)
                totals["snapshot"] += n
                print(f"  {report_type} snapshot: {n} rows")

            if chart_path.exists():
                n = load_chart_data(conn, report_type, chart_path)
                totals["chart"] += n
                print(f"  {report_type} daily: {n} rows")

        print("\nValidation:")
        checks = validate_load(conn)
        for key, value in checks.items():
            print(f"  {key}: {value}")

        print(
            f"\nDone — viewership={totals['viewership']}, "
            f"snapshots={totals['snapshot']}, daily_metrics={totals['chart']}"
        )
    finally:
        conn.close()


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Load YouTube CSVs into PostgreSQL")
    parser.add_argument("--data-dir", type=Path, default=Path("Data"))
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DB_URL),
        help="PostgreSQL connection string",
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Append/upsert without truncating tables first",
    )
    args = parser.parse_args()

    try:
        load_all(args.data_dir, args.database_url, truncate=not args.no_truncate)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

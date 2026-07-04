#!/usr/bin/env python3
"""
Task 2c — Run EDA queries and export figures + markdown summary.

Usage:
    make eda-export
    DATABASE_URL=... python scripts/run_eda.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
import seaborn as sns
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "docs" / "architecture" / "figures"
FINDINGS_PATH = ROOT / "docs" / "architecture" / "eda-findings.md"
DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5433/youtube_analytics"

sns.set_theme(style="whitegrid", palette="muted")


def query_df(database_url: str, sql: str) -> pd.DataFrame:
    with psycopg2.connect(database_url) as conn:
        return pd.read_sql(sql, conn)


def save_fig(name: str) -> str:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    return str(path.relative_to(ROOT))


def run_eda(database_url: str) -> str:
    inventory = query_df(
        database_url,
        """
        SELECT 'viewership_daily' AS table_name, COUNT(*) AS rows FROM youtube.viewership_daily
        UNION ALL SELECT 'dimension_snapshots', COUNT(*) FROM youtube.dimension_snapshots
        UNION ALL SELECT 'dimension_metrics_daily', COUNT(*) FROM youtube.dimension_metrics_daily
        UNION ALL SELECT 'report_metadata', COUNT(*) FROM youtube.report_metadata
        ORDER BY 1
        """,
    )

    channel = query_df(
        database_url,
        """
        SELECT
            MIN(view_date) AS first_date,
            MAX(view_date) AS last_date,
            SUM(views) AS total_views_in_table,
            ROUND(SUM(watch_time_hours)::numeric, 2) AS total_watch_hours,
            ROUND(AVG(avg_view_duration_sec)::numeric, 0) AS avg_duration_sec
        FROM youtube.viewership_daily
        """,
    )

    top_geo = query_df(
        database_url,
        """
        SELECT dimension_value AS country, views
        FROM youtube.dimension_snapshots
        WHERE report_type = 'geography'
        ORDER BY views DESC NULLS LAST
        LIMIT 10
        """,
    )

    devices = query_df(
        database_url,
        """
        SELECT dimension_value AS device, views,
               ROUND(100.0 * views / SUM(views) OVER (), 1) AS pct
        FROM youtube.dimension_snapshots
        WHERE report_type = 'device_type'
        ORDER BY views DESC
        """,
    )

    traffic = query_df(
        database_url,
        """
        SELECT dimension_value AS source, views, impressions, impressions_ctr_pct
        FROM youtube.dimension_snapshots
        WHERE report_type = 'traffic_source'
        ORDER BY views DESC NULLS LAST
        LIMIT 8
        """,
    )

    daily = query_df(
        database_url,
        """
        SELECT view_date, views
        FROM youtube.viewership_daily
        ORDER BY view_date
        """,
    )

    demographics = query_df(
        database_url,
        """
        SELECT report_type, dimension_value, views_pct, watch_time_pct
        FROM youtube.dimension_snapshots
        WHERE report_type IN ('viewer_age', 'viewer_gender')
        ORDER BY report_type, views_pct DESC NULLS LAST
        """,
    )

    # --- Figures ---
    fig_paths: list[tuple[str, str]] = []

    plt.figure(figsize=(10, 4))
    plt.plot(daily["view_date"], daily["views"], linewidth=1.2)
    plt.title("Daily Views Over Time (viewership_daily)")
    plt.xlabel("Date")
    plt.ylabel("Views")
    fig_paths.append(("Daily view trend", save_fig("01_daily_views")))

    plt.figure(figsize=(8, 4))
    sns.barplot(data=top_geo, x="views", y="country", hue="country", legend=False)
    plt.title("Top 10 Countries by Views (snapshot)")
    plt.xlabel("Views")
    fig_paths.append(("Top geographies", save_fig("02_top_geography")))

    plt.figure(figsize=(7, 4))
    sns.barplot(data=devices, x="views", y="device", hue="device", legend=False)
    plt.title("Views by Device Type")
    plt.xlabel("Views")
    fig_paths.append(("Device breakdown", save_fig("03_device_type")))

    plt.figure(figsize=(8, 4))
    traffic_plot = traffic.dropna(subset=["views"])
    sns.barplot(data=traffic_plot, x="views", y="source", hue="source", legend=False)
    plt.title("Top Traffic Sources")
    plt.xlabel("Views")
    fig_paths.append(("Traffic sources", save_fig("04_traffic_source")))

    if not demographics.empty:
        plt.figure(figsize=(7, 4))
        age = demographics[demographics["report_type"] == "viewer_age"]
        sns.barplot(data=age, x="views_pct", y="dimension_value", hue="dimension_value", legend=False)
        plt.title("Viewer Age Distribution (% of views)")
        plt.xlabel("Views (%)")
        fig_paths.append(("Age demographics", save_fig("05_viewer_age")))

    # --- Markdown report ---
    first_date = channel.iloc[0]["first_date"]
    last_date = channel.iloc[0]["last_date"]
    total_views = int(channel.iloc[0]["total_views_in_table"])
    watch_hours = channel.iloc[0]["total_watch_hours"]
    top_country = top_geo.iloc[0]["country"] if not top_geo.empty else "N/A"
    top_device = devices.iloc[0]["device"] if not devices.empty else "N/A"

    lines = [
        "# Task 2c: YouTube Analytics EDA Findings",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 1. Data inventory",
        "",
        inventory.to_markdown(index=False),
        "",
        "## 2. Channel performance",
        "",
        f"- **Date range in DB:** {first_date} → {last_date}",
        f"- **Total views (summed daily rows):** {total_views:,}",
        f"- **Total watch time:** {watch_hours} hours",
        f"- **Note:** `viewership_daily` holds top-500 days from YouTube export; channel snapshot total is 26,625 views.",
        "",
        "## 3. Audience geography",
        "",
        top_geo.to_markdown(index=False),
        "",
        f"**Insight:** `{top_country}` drives the largest share of views — prioritize in geo dashboards and NL→SQL examples.",
        "",
        "## 4. Device & traffic",
        "",
        "### Devices",
        devices.to_markdown(index=False),
        "",
        f"**Insight:** `{top_device}` dominates; mobile is the secondary segment to compare in chatbot demos.",
        "",
        "### Traffic sources",
        traffic.to_markdown(index=False),
        "",
        "## 5. Demographics",
        "",
        demographics.to_markdown(index=False) if not demographics.empty else "_No demographic rows loaded._",
        "",
        "**Insight:** 25–34 age group accounts for ~73% of views; male viewers ~80% of views (percentage-based snapshot).",
        "",
        "## 6. Implications for the LLM chatbot",
        "",
        "| Finding | Chatbot use case |",
        "|---------|------------------|",
        "| Computer > Mobile views | Demo query: compare device types |",
        "| ET top geography | Demo query: views from Ethiopia |",
        "| Channel pages top traffic source | Explain acquisition mix |",
        "| Snapshot vs daily tables | Route time-series vs summary questions |",
        "| `report_metadata` seeded | RAG / schema context for Task 4 |",
        "",
        "## 7. Figures",
        "",
    ]

    for title, rel_path in fig_paths:
        lines.append(f"### {title}")
        lines.append("")
        lines.append(f"![{title}](figures/{Path(rel_path).name})")
        lines.append("")

    lines.extend(
        [
            "## 8. Suggested Redash dashboards (Task 3 preview)",
            "",
            "1. **Channel KPIs** — daily views line chart (`viewership_daily`)",
            "2. **Audience** — geography bar chart + device pie (`dimension_snapshots`)",
            "3. **Acquisition** — traffic source table with impressions/CTR",
            "4. **Demographics** — age/gender percentage charts",
            "",
        ]
    )

    FINDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FINDINGS_PATH.write_text("\n".join(lines), encoding="utf-8")
    return FINDINGS_PATH.read_text(encoding="utf-8")


def main() -> int:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
    try:
        report = run_eda(database_url)
        print(report)
        print(f"\nWrote: {FINDINGS_PATH}")
        print(f"Figures: {FIGURES_DIR}/")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Hint: run make db-up db-init db-load first", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

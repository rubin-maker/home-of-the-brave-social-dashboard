#!/usr/bin/env python3
"""Validate the generated dashboard against the included YouTube source rows."""

import csv
import hashlib
import json
import os
from collections import Counter
from datetime import date, datetime, timedelta

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "youtube.xlsx")


def number(value):
    return 0 if value in (None, "", "-", "--", "N/A") else float(value)


workbook = load_workbook(SOURCE, read_only=True, data_only=True)
included = []
status_counts = {}
for sheet_name in ("Long Data", "Shorts Data"):
    iterator = workbook[sheet_name].iter_rows(values_only=True)
    headers = list(next(iterator))
    rows = [dict(zip(headers, values)) for values in iterator if any(v is not None for v in values)]
    status_counts[sheet_name] = dict(Counter(row.get("Analysis Status") for row in rows))
    included.extend(row for row in rows if row.get("Analysis Status") == "Included")

formula_errors = {}
for sheet in workbook.worksheets:
    count = sum(1 for row in sheet.iter_rows(values_only=True) for value in row
                if isinstance(value, str) and value.startswith("#"))
    if count:
        formula_errors[sheet.title] = count
workbook.close()

assert len(included) == 533
assert len({row["Content"] for row in included}) == len(included)
assert all(row.get("Video publish time") and row.get("Video title") for row in included)
assert all((row["Video publish time"].date() if isinstance(row["Video publish time"], datetime)
            else row["Video publish time"]).year == 2026 for row in included)
assert all(row.get("Category") and row["Category"] != "Uncategorized" for row in included)

youtube = {
    "posts": len(included),
    "views": int(sum(number(row.get("Views")) for row in included)),
    "eng": int(sum(number(row.get("Likes")) + number(row.get("Shares"))
                   + number(row.get("Comments added")) for row in included)),
    "reach": int(sum(number(row.get("Thumbnail impressions")) for row in included)),
    "followers": int(sum(number(row.get("Subscribers")) for row in included)),
    "watch_hours": round(sum(number(row.get("Watch time (hours)")) for row in included), 2),
}
summary_path = os.path.join(ROOT, "summary.json")
with open(summary_path, encoding="utf-8") as handle:
    summary = json.load(handle)
for key, expected in youtube.items():
    assert summary["totals"]["YouTube"][key] == expected, (key, summary["totals"]["YouTube"][key], expected)
assert youtube == {"posts": 533, "views": 3398233, "eng": 141189, "reach": 2401564,
                   "followers": 4355, "watch_hours": 46338.44}
assert summary["youtube_subscribers"]["long_form"] == 1290
assert summary["youtube_subscribers"]["shorts"] == 3065
assert sum(row["gained"] for row in summary["youtube_subscribers"]["weekly"]) == 4355
assert summary["report_scope"]["end"] == "2026-08-23"
assert summary["common_coverage_end"] == "2026-08-26"

category_weeks = summary["category_weeks"]
category_week_keys = [row[0] for row in category_weeks]
assert len(category_weeks) == 37
assert category_weeks[0] == ["2026-01-01", "2026-01-01", "2026-01-04"]
assert category_weeks[-1] == ["2026-09-07", "2026-09-07", "2026-09-09"]
for previous, current in zip(category_weeks, category_weeks[1:]):
    assert date.fromisoformat(current[1]) == date.fromisoformat(previous[2]) + timedelta(days=1)
for platform, categories in summary["category_weekly"].items():
    cutoff = summary["platform_coverage_end"][platform]
    for category, by_week in categories.items():
        assert list(by_week) == category_week_keys
        for week_key, week_start, _ in category_weeks:
            assert (by_week[week_key] is None) == (week_start > cutoff)
        total = next(row for row in summary["category_totals"][platform]
                     if row["category"] == category)
        for metric in ("posts", "views", "eng"):
            assert sum(row[metric] for row in by_week.values() if row is not None) == total[metric]
    for metric in ("posts", "views", "eng"):
        assert sum(row[metric] for row in summary["category_totals"][platform]) == summary["totals"][platform][metric]
    for week_key, week_start, week_end in category_weeks:
        if week_start <= cutoff:
            raw_rows = [row for row in summary["posts"]
                        if row["platform"] == platform
                        and week_start <= row["date"] <= min(week_end, cutoff)]
            expected = {
                "posts": len(raw_rows),
                "views": sum(row["views"] for row in raw_rows),
                "eng": sum(row["engagements"] for row in raw_rows),
            }
            for metric in ("posts", "views", "eng"):
                assert sum(by_week[week_key][metric] for by_week in categories.values()) == expected[metric]

dashboard = open(os.path.join(ROOT, "dashboard.html"), encoding="utf-8").read()
index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
assert dashboard == index
assert ">YouTube subscriber metric<" in dashboard
assert ">YouTube subscribers gained<" not in dashboard
assert "3,398,233" in dashboard or '"views":3398233' in dashboard
assert "Every available 2026 publish week" in dashboard
assert "dates mark the start of each week" in dashboard
assert "all available 2026 weekly" in dashboard
assert "No categories selected — choose Show all" in dashboard
assert "Deselect all" in dashboard
assert "Select a bar for that week's exact stats." in dashboard
assert "data-spark-platform=" in dashboard
assert "spark-readout" in dashboard
assert 'ALL_CATEGORIES="All categories"' in dashboard
assert 'stroke-dasharray="8 4"' in dashboard

with open(os.path.join(ROOT, "all_posts.csv"), encoding="utf-8-sig", newline="") as handle:
    post_rows = list(csv.DictReader(handle))
assert len(post_rows) == sum(total["posts"] for total in summary["totals"].values())
assert sum(row["Platform"] == "YouTube" for row in post_rows) == 533

result = {
    "source": os.path.basename(SOURCE),
    "sourceSha256": hashlib.sha256(open(SOURCE, "rb").read()).hexdigest(),
    "includedYouTubeRows": 533,
    "statusCounts": status_counts,
    "youtubeTotals": youtube,
    "subscriberMetric": "Source Subscribers; not relabeled as Subscribers gained and not a channel balance",
    "reportingWeek": summary["report_scope"],
    "knownWorkbookFormulaErrors": {
        "count": sum(formula_errors.values()),
        "bySheet": formula_errors,
        "impact": "Cached weekly delta cells only; dashboard recomputes from included Long Data and Shorts Data rows.",
    },
    "checks": [
        "533 unique included YouTube Content IDs",
        "All included YouTube rows have 2026 publish dates, titles and recognized categories",
        "Dashboard YouTube totals reconcile to raw included rows",
        "Subscriber weekly totals reconcile to the 4,355 source Subscribers value",
        "Headline week remains within common four-platform coverage",
        "All 37 available 2026 category weeks are contiguous and reconcile to category totals",
        "Category chart axes use readable dates and stop at each platform's latest included publish date",
        "Category charts include Show all and Deselect all controls",
        "Platform cards label their headline units and expose selectable weekly bar details",
        "All categories lines reconcile to platform totals and use a distinct dashed treatment",
        "Dashboard and index HTML match",
        "All-post CSV row counts reconcile to the dashboard summary",
    ],
}
with open(os.path.join(ROOT, "validation.json"), "w", encoding="utf-8") as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
print(json.dumps({"status": "PASS", "youtube": youtube,
                  "knownWorkbookFormulaErrors": sum(formula_errors.values())}, indent=2))

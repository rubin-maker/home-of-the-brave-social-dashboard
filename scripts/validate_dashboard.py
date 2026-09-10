#!/usr/bin/env python3
"""Validate the generated dashboard against the included YouTube source rows."""

import csv
import hashlib
import json
import os
from collections import Counter
from datetime import date, datetime

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

dashboard = open(os.path.join(ROOT, "dashboard.html"), encoding="utf-8").read()
index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
assert dashboard == index
assert ">YouTube subscriber metric<" in dashboard
assert ">YouTube subscribers gained<" not in dashboard
assert "3,398,233" in dashboard or '"views":3398233' in dashboard

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
        "Dashboard and index HTML match",
        "All-post CSV row counts reconcile to the dashboard summary",
    ],
}
with open(os.path.join(ROOT, "validation.json"), "w", encoding="utf-8") as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
print(json.dumps({"status": "PASS", "youtube": youtube,
                  "knownWorkbookFormulaErrors": sum(formula_errors.values())}, indent=2))

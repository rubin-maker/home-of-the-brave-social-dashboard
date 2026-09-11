#!/usr/bin/env python3
"""Normalize the four Home of the Brave workbooks into one dashboard data layer."""

import csv
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta

try:
    from openpyxl import load_workbook
    from openpyxl.utils.datetime import from_excel
except ImportError:
    print("openpyxl is required — run: python3 -m pip install -r requirements.txt")
    raise SystemExit(1)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources")
BRAND = "Home of the Brave"
WEEKLY_CONTEXT_WEEKS = 8
CATEGORY_TREND_PLATFORMS = ("Instagram", "YouTube", "TikTok")

SOURCES = {
    "YouTube": os.path.join(SRC, "youtube.xlsx"),
    "Instagram": os.path.join(SRC, "instagram.xlsx"),
    "TikTok": os.path.join(SRC, "tiktok.xlsx"),
    "X": os.path.join(SRC, "x.xlsx"),
}

METRIC_DEFINITIONS = {
    "YouTube": {
        "views": "Views",
        "engagements": "Likes + shares + comments",
        "audience": "Impressions",
        "metric_label": "views",
        "subscribers": "Source-reported Subscribers attributed to exported videos; not a current channel subscriber count or net subscriber growth.",
    },
    "Instagram": {
        "views": "Views",
        "engagements": "Likes + comments + shares + saves",
        "audience": "Reach",
        "metric_label": "views",
    },
    "TikTok": {
        "views": "Views",
        "engagements": "Likes + comments + shares + bookmarks",
        "audience": "Not available",
        "metric_label": "views",
    },
    "X": {
        "views": "Impressions (reported as Views in the source workbook)",
        "engagements": "Source-reported total engagements",
        "audience": "Not available",
        "metric_label": "impressions",
    },
}


def clean_text(value):
    text = "\n".join(line.rstrip() for line in str(value or "").splitlines()).strip()
    replacements = {
        "‚Äú": "“", "‚Äù": "”", "‚Äô": "’", "‚Ä¶": "…",
        "â€œ": "“", "â€": "”", "â€™": "’", "â€¦": "…",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def number(value):
    if value in (None, "", "-", "--", "N/A"):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def iso_date(value, epoch):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (int, float)):
        return from_excel(value, epoch).date().isoformat()
    text = clean_text(value)
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized date: {value!r}")


def monday_of(iso):
    current = date.fromisoformat(iso)
    return current - timedelta(days=current.weekday())


def read_rows(workbook_path, sheet_name):
    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        ws = wb[sheet_name]
        iterator = ws.iter_rows(values_only=True)
        headers = [clean_text(v) for v in next(iterator)]
        for values in iterator:
            if not any(v is not None for v in values):
                continue
            yield dict(zip(headers, values)), wb.epoch
    finally:
        wb.close()


def youtube_posts():
    posts = []
    for sheet_name in ("Long Data", "Shorts Data"):
        for row, epoch in read_rows(SOURCES["YouTube"], sheet_name):
            status = clean_text(row.get("Analysis Status"))
            if status and status != "Included":
                continue
            content_id = clean_text(row.get("Content"))
            published = iso_date(row.get("Video publish time"), epoch)
            likes = int(number(row.get("Likes")))
            shares = int(number(row.get("Shares")))
            comments = int(number(row.get("Comments added")))
            subscriber_value = row.get("Subscribers gained")
            if subscriber_value is None:
                subscriber_value = row.get("Subscribers")
            subscribers = int(number(subscriber_value))
            posts.append({
                "id": content_id,
                "platform": "YouTube",
                "date": published,
                "title": clean_text(row.get("Video title")),
                "url": f"https://www.youtube.com/watch?v={content_id}" if content_id else "",
                "views": int(number(row.get("Views"))),
                "reach": int(number(row.get("Impressions") if row.get("Impressions") is not None
                                    else row.get("Thumbnail impressions"))),
                "engagements": likes + shares + comments,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": 0,
                "followers": subscribers,
                "type": clean_text(row.get("Product")),
                "category": clean_text(row.get("Category")) or "Other",
                "duration_sec": int(number(row.get("Duration"))),
                "watch_hours": round(number(row.get("Watch time (hours)")), 4),
            })
    return posts


def instagram_posts():
    posts = []
    for row, epoch in read_rows(SOURCES["Instagram"], "IG Data"):
        likes = int(number(row.get("Likes")))
        comments = int(number(row.get("Comments")))
        shares = int(number(row.get("Shares")))
        saves = int(number(row.get("Saves")))
        posts.append({
            "id": clean_text(row.get("Post ID")),
            "platform": "Instagram",
            "date": iso_date(row.get("Publish time"), epoch),
            "title": clean_text(row.get("Description")),
            "url": clean_text(row.get("Permalink")),
            "views": int(number(row.get("Views"))),
            "reach": int(number(row.get("Reach"))),
            "engagements": likes + comments + shares + saves,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "followers": int(number(row.get("Follows"))),
            "type": clean_text(row.get("Post type")),
            "category": clean_text(row.get("Category")) or "Other",
            "duration_sec": int(number(row.get("Duration (sec)"))),
            "watch_hours": 0,
        })
    return posts


def tiktok_posts():
    posts = []
    for row, epoch in read_rows(SOURCES["TikTok"], "TT Data"):
        likes = int(number(row.get("Likes")))
        comments = int(number(row.get("Comments")))
        shares = int(number(row.get("Shares")))
        saves = int(number(row.get("Bookmarks")))
        posts.append({
            "id": clean_text(row.get("Post ID")),
            "platform": "TikTok",
            "date": iso_date(row.get("Publish time"), epoch),
            "title": clean_text(row.get("Post text")),
            "url": clean_text(row.get("URL")),
            "views": int(number(row.get("Views"))),
            "reach": 0,
            "engagements": int(number(row.get("Total Engagements"))) or likes + comments + shares + saves,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "followers": 0,
            "type": "Video",
            "category": clean_text(row.get("Category")) or "Other",
            "duration_sec": int(number(row.get("Duration (sec)"))),
            "watch_hours": 0,
        })
    return posts


def x_posts():
    posts = []
    for row, epoch in read_rows(SOURCES["X"], "X Data"):
        likes = int(number(row.get("Likes")))
        comments = int(number(row.get("Replies")))
        shares = int(number(row.get("Reposts")))
        saves = int(number(row.get("Bookmarks")))
        posts.append({
            "id": clean_text(row.get("Post ID")),
            "platform": "X",
            "date": iso_date(row.get("Date"), epoch),
            "title": clean_text(row.get("Post text")),
            "url": clean_text(row.get("URL")),
            "views": int(number(row.get("Views"))),
            "reach": 0,
            "engagements": int(number(row.get("Engagements"))),
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "followers": 0,
            "type": clean_text(row.get("Source")),
            "category": clean_text(row.get("Category")) or "Other",
            "duration_sec": 0,
            "watch_hours": 0,
        })
    return posts


def aggregate(rows):
    views = sum(p["views"] for p in rows)
    engagements = sum(p["engagements"] for p in rows)
    return {
        "posts": len(rows),
        "views": views,
        "eng": engagements,
        "reach": sum(p["reach"] for p in rows),
        "followers": sum(p["followers"] for p in rows),
        "watch_hours": round(sum(p["watch_hours"] for p in rows), 2),
        "er": round(100 * engagements / views, 2) if views else None,
        "avg_views": round(views / len(rows)) if rows else 0,
    }


posts = youtube_posts() + instagram_posts() + tiktok_posts() + x_posts()
posts.sort(key=lambda p: (p["date"], p["platform"], p["id"]))
platforms = list(SOURCES)

if not posts:
    raise SystemExit("No source rows found.")

period_start = min(p["date"] for p in posts)
period_end = max(p["date"] for p in posts)
platform_ends = {
    platform: max(p["date"] for p in posts if p["platform"] == platform)
    for platform in platforms
}
common_coverage_end = min(platform_ends.values())
latest_complete_sunday = monday_of(common_coverage_end) - timedelta(days=1)
report_start = latest_complete_sunday - timedelta(days=6)
report_end = latest_complete_sunday

week_starts = []
cursor = monday_of(period_start)
while cursor <= report_start:
    week_starts.append(cursor)
    cursor += timedelta(days=7)
context_starts = week_starts[-WEEKLY_CONTEXT_WEEKS:]
weeks = []
for start in context_starts:
    end = start + timedelta(days=6)
    name = f"Week {start.isocalendar().week}"
    weeks.append([name, start.isoformat(), end.isoformat()])

for post in posts:
    post_week_start = monday_of(post["date"])
    post["week"] = f"Week {post_week_start.isocalendar().week}"

# Category charts retain every available 2026 publish week. The first and last
# labels are clipped to the available period. After the partial opening week,
# each aggregation key is the Monday that owns the week.
category_weeks = []
category_cursor = monday_of(period_start)
category_last_start = monday_of(period_end)
period_start_date = date.fromisoformat(period_start)
period_end_date = date.fromisoformat(period_end)
while category_cursor <= category_last_start:
    category_end = category_cursor + timedelta(days=6)
    display_start = max(category_cursor, period_start_date)
    display_end = min(category_end, period_end_date)
    category_weeks.append([
        display_start.isoformat(),
        display_start.isoformat(),
        display_end.isoformat(),
    ])
    category_cursor += timedelta(days=7)

totals = {p: aggregate([x for x in posts if x["platform"] == p]) for p in platforms}
youtube_rows = [post for post in posts if post["platform"] == "YouTube"]
youtube_workbook = load_workbook(SOURCES["YouTube"], read_only=True, data_only=True)
try:
    cutoff = next(
        row[1] for row in youtube_workbook["Definitions"].iter_rows(values_only=True)
        if clean_text(row[0]) == "Data cutoff"
    )
    youtube_cutoff = iso_date(cutoff, youtube_workbook.epoch)
finally:
    youtube_workbook.close()
youtube_subscribers = {
    "gained": totals["YouTube"]["followers"],
    "long_form": sum(post["followers"] for post in youtube_rows if post["type"] == "Long-Form"),
    "shorts": sum(post["followers"] for post in youtube_rows if post["type"] == "Shorts"),
    "video_count": len(youtube_rows),
    "as_of": youtube_cutoff,
    "channel_total": None,
    "definition": METRIC_DEFINITIONS["YouTube"]["subscribers"],
    "source": "sources/youtube.xlsx · Long Data and Shorts Data · Subscribers",
}
assert youtube_subscribers["long_form"] + youtube_subscribers["shorts"] == youtube_subscribers["gained"]
subscriber_weeks = []
subscriber_week = monday_of(min(post["date"] for post in youtube_rows))
last_subscriber_week = monday_of(max(post["date"] for post in youtube_rows))
while subscriber_week <= last_subscriber_week:
    subscriber_end = subscriber_week + timedelta(days=6)
    cohort = [post for post in youtube_rows
              if subscriber_week.isoformat() <= post["date"] <= subscriber_end.isoformat()]
    subscriber_weeks.append({
        "start": subscriber_week.isoformat(),
        "end": subscriber_end.isoformat(),
        "gained": sum(post["followers"] for post in cohort),
        "long_form": sum(post["followers"] for post in cohort if post["type"] == "Long-Form"),
        "shorts": sum(post["followers"] for post in cohort if post["type"] == "Shorts"),
        "video_count": len(cohort),
        "complete": subscriber_end.isoformat() <= youtube_cutoff,
    })
    subscriber_week += timedelta(days=7)
youtube_subscribers["weekly"] = subscriber_weeks
youtube_subscribers["weekly_definition"] = (
    "Source-reported Subscribers attributed to exported videos, grouped by Monday–Sunday publish week. "
    "These are not subscribers gained during the week or the channel subscriber balance at week-end. "
    "A zero-video week means no videos in the supplied export, not zero channel activity. "
    "Weeks ending after the export cutoff are partial."
)
assert sum(row["gained"] for row in subscriber_weeks) == youtube_subscribers["gained"]
assert sum(row["video_count"] for row in subscriber_weeks) == youtube_subscribers["video_count"]
assert all(row["long_form"] + row["shorts"] == row["gained"] for row in subscriber_weeks)
weekly = {}
top5 = {}
for name, start, end in weeks:
    weekly[name] = {}
    top5[name] = {}
    for platform in platforms:
        subset = [x for x in posts if x["platform"] == platform and start <= x["date"] <= end]
        weekly[name][platform] = aggregate(subset)
        top5[name][platform] = sorted(subset, key=lambda x: (-x["views"], x["date"], x["id"]))[:5]

report_name = weeks[-1][0]
report_posts = [p for p in posts if report_start.isoformat() <= p["date"] <= report_end.isoformat()]
report_totals = {p: aggregate([x for x in report_posts if x["platform"] == p]) for p in platforms}
report_scope = {
    "week": report_name,
    "start": report_start.isoformat(),
    "end": report_end.isoformat(),
    "totals": report_totals,
    "posts": len(report_posts),
    "views": sum(x["views"] for x in report_posts),
    "eng": sum(x["engagements"] for x in report_posts),
}

category_totals = {}
for platform in platforms:
    category_totals[platform] = []
    categories = sorted({p["category"] for p in posts if p["platform"] == platform})
    for category in categories:
        subset = [p for p in posts if p["platform"] == platform and p["category"] == category]
        category_totals[platform].append({"category": category, **aggregate(subset)})
    category_totals[platform].sort(key=lambda x: (-x["views"], x["category"]))

category_weekly = {}
for platform in CATEGORY_TREND_PLATFORMS:
    category_weekly[platform] = {}
    for category_row in category_totals[platform]:
        category = category_row["category"]
        category_weekly[platform][category] = {}
        for week_key, week_start, week_end in category_weeks:
            if week_start > platform_ends[platform]:
                category_weekly[platform][category][week_key] = None
                continue
            subset = [
                post for post in posts
                if post["platform"] == platform
                and post["category"] == category
                and week_start <= post["date"] <= min(week_end, platform_ends[platform])
            ]
            category_weekly[platform][category][week_key] = aggregate(subset)

source_notes = [
    f"YouTube: cumulative per-video metrics through {youtube_cutoff}; "
    f"{sum(p['type'] == 'Long-Form' for p in youtube_rows)} included long-form videos and "
    f"{sum(p['type'] == 'Shorts' for p in youtube_rows)} included Shorts.",
    "YouTube subscriber metric: sum of the source-reported Subscribers column across included videos. "
    "The workbook says not to relabel it as Subscribers gained; it is not the current channel subscriber total.",
    "YouTube exclusions retained in the source workbook but omitted from dashboard analysis: aggregate rows, rows without a publish date, and rows outside 2026.",
    "The source workbook has cached #VALUE! cells in weekly delta columns for blank weeks. The dashboard does not use those formulas; it recomputes from included raw rows.",
    f"Instagram: Meta Business Suite export with published-post coverage through {platform_ends['Instagram']}; "
    f"{totals['Instagram']['posts']} reviewed posts.",
    "TikTok: per-post export through Aug 27, 2026; 563 reviewed posts.",
    f"X: combined analytics export and scrape with authored-post coverage through {platform_ends['X']}; "
    f"{totals['X']['posts']:,} authored posts; rows that are themselves reposted posts were excluded upstream.",
    "X engagement uses the source-reported Engagements field. Analytics-export and earlier raw-scrape rows can include actions beyond likes, replies, reposts, and bookmarks; the 41 Sep 10 scrape rows use the visible component sum. Reposts interaction counts are retained.",
    f"The headline reporting week is based on common cross-platform coverage through {common_coverage_end}; individual source freshness differs.",
]

summary = {
    "brand": BRAND,
    "period": {"start": period_start, "end": period_end},
    "platform_coverage_end": platform_ends,
    "common_coverage_end": common_coverage_end,
    "weeks": weeks,
    "category_weeks": category_weeks,
    "report_scope": report_scope,
    "totals": totals,
    "youtube_subscribers": youtube_subscribers,
    "weekly": weekly,
    "top5": top5,
    "category_totals": category_totals,
    "category_weekly": category_weekly,
    "metric_definitions": METRIC_DEFINITIONS,
    "source_notes": source_notes,
    "posts": posts,
}
with open(os.path.join(ROOT, "summary.json"), "w", encoding="utf-8") as handle:
    json.dump(summary, handle, ensure_ascii=False, indent=1, sort_keys=True)

csv_path = os.path.join(ROOT, "all_posts.csv")
with open(csv_path, "w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow([
        "Platform", "Date", "Week", "Category", "Type", "Title / Text", "Link",
        "Views / Impressions", "Reach / Impressions", "Engagements", "Engagement Rate %",
        "Likes", "Comments / Replies", "Shares / Reposts", "Saves / Bookmarks", "Followers / Subs",
    ])
    for post in sorted(posts, key=lambda p: (-p["views"], p["platform"], p["date"])):
        rate = round(100 * post["engagements"] / post["views"], 2) if post["views"] else ""
        writer.writerow([
            post["platform"], post["date"], post["week"], post["category"], post["type"],
            post["title"], post["url"], post["views"], post["reach"], post["engagements"], rate,
            post["likes"], post["comments"], post["shares"], post["saves"], post["followers"],
        ])

print(f"=== {BRAND} · full file {period_start}..{period_end} ===")
for platform in platforms:
    total = totals[platform]
    label = METRIC_DEFINITIONS[platform]["metric_label"]
    print(f"  {platform:10s} {total['posts']:4d} posts | {total['views']:>12,} {label:11s} | {total['eng']:>9,} engagements")
print(f"--- reporting week: {report_start}..{report_end} ---")
print(f"  {report_scope['posts']} posts | {report_scope['views']:,} views/impressions | {report_scope['eng']:,} engagements")
print(f"summary.json + {csv_path}")

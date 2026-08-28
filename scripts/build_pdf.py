#!/usr/bin/env python3
"""Build a printable HOTB summary from the normalized summary.json."""

import json
import os
import unicodedata

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ImportError:
    print("reportlab not installed — skipping PDF (install with requirements.txt)")
    raise SystemExit(0)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "summary.json"), encoding="utf-8") as handle:
    S = json.load(handle)

BRAND = S["brand"]
REPORT = S["report_scope"]
PLATFORMS = list(S["totals"])
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def span(start, end):
    first_month, first_day = MONTHS[int(start[5:7]) - 1], int(start[8:10])
    last_month, last_day = MONTHS[int(end[5:7]) - 1], int(end[8:10])
    return f"{first_month} {first_day}-{last_day}" if first_month == last_month else f"{first_month} {first_day}-{last_month} {last_day}"


def full(value):
    return f"{(value or 0):,.0f}"


def compact(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{round(value / 1_000):,}K"
    return full(value)


def ascii_text(value):
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."}
    text = str(value or "")
    for source, target in replacements.items():
        text = text.replace(source, target)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def safe(value):
    return ascii_text(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


COLORS = {
    "YouTube": "#ff3155", "Instagram": "#c13584", "TikTok": "#00a6a6", "X": "#68707c",
}
INK = colors.HexColor("#171512")
INK2 = colors.HexColor("#5f5a52")
MUTED = colors.HexColor("#847e74")
GRID = colors.HexColor("#e4ded4")
SURFACE = colors.HexColor("#f5f2eb")

styles = getSampleStyleSheet()


def style(**kwargs):
    kwargs.setdefault("fontName", "Helvetica")
    return ParagraphStyle("custom", parent=styles["Normal"], **kwargs)


H1 = style(fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=3)
H2 = style(fontName="Helvetica-Bold", fontSize=14, leading=18, spaceBefore=14, spaceAfter=6)
H3 = style(fontName="Helvetica-Bold", fontSize=10.5, leading=13, spaceBefore=8, spaceAfter=4)
SUB = style(fontSize=9.5, leading=13, textColor=INK2)
NOTE = style(fontSize=8, leading=11, textColor=MUTED, spaceBefore=5)
CELL = style(fontSize=8, leading=10.5)


def make_table(data, widths, alignments=None, font_size=8):
    result = Table(data, colWidths=widths, repeatRows=1)
    rules = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK2),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#c8c0b4")),
        ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
    ]
    if alignments:
        for index, alignment in enumerate(alignments):
            if alignment == "R":
                rules.append(("ALIGN", (index, 0), (index, -1), "RIGHT"))
    result.setStyle(TableStyle(rules))
    return result


scope_label = span(REPORT["start"], REPORT["end"])
year = S["period"]["end"][:4]
week_labels = {name: f"W{name.split()[-1]} - {span(start, end)}" for name, start, end in S["weeks"]}

story = [
    Paragraph(f"{BRAND} - Social Performance Summary", H1),
    Paragraph(f"<b>{scope_label}, {year}</b> - YouTube, Instagram, TikTok, and X - latest complete Monday-Sunday week", SUB),
    Spacer(1, 10),
]

rows = [["Platform", "Posts", "Views / impressions", "Engagements", "Rate", "YTD views / impressions"]]
for platform in sorted(PLATFORMS, key=lambda p: -REPORT["totals"][p]["views"]):
    scoped = REPORT["totals"][platform]
    rows.append([
        platform,
        full(scoped["posts"]),
        full(scoped["views"]),
        full(scoped["eng"]),
        f"{scoped['er']:.2f}%" if scoped["er"] is not None else "—",
        full(S["totals"][platform]["views"]),
    ])
rows.append([
    "TOTAL", full(REPORT["posts"]), full(REPORT["views"]), full(REPORT["eng"]),
    f"{100 * REPORT['eng'] / REPORT['views']:.2f}%" if REPORT["views"] else "—",
    full(sum(S["totals"][p]["views"] for p in PLATFORMS)),
])
score = make_table(rows, [1.35 * inch, .75 * inch, 1.65 * inch, 1.25 * inch, .85 * inch, 1.75 * inch], ["L", "R", "R", "R", "R", "R"], 8.5)
score.setStyle(TableStyle([("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("LINEABOVE", (0, -1), (-1, -1), .8, colors.HexColor("#c8c0b4"))]))
story.extend([score, Paragraph("X contributes impressions; YouTube, Instagram, and TikTok contribute views. The blended rate is directional, not a standardized cross-platform KPI.", NOTE)])

story.append(Paragraph("Eight-week trend", H2))
weeks = [week[0] for week in S["weeks"]]
weekly_rows = [["Platform"] + [label.replace(" - ", "\n", 1) for label in (week_labels[w] for w in weeks)]]
for platform in PLATFORMS:
    weekly_rows.append([platform] + [compact(S["weekly"][week][platform]["views"]) for week in weeks])
trend = make_table(weekly_rows, [1.15 * inch] + [.96 * inch] * len(weeks), ["L"] + ["R"] * len(weeks), 7.6)
story.extend([trend, Paragraph("Current cumulative metrics are attributed to the post's publish week; recent weeks have had less time to mature.", NOTE)])

story.append(Paragraph("Year-to-date category leaders", H2))
category_rows = [["Platform", "Leading category", "Posts", "Views / impressions", "Avg / post", "Engagements"]]
for platform in PLATFORMS:
    leader = S["category_totals"][platform][0]
    category_rows.append([platform, leader["category"], full(leader["posts"]), full(leader["views"]), full(leader["avg_views"]), full(leader["eng"])])
story.append(make_table(category_rows, [1.05 * inch, 2.05 * inch, .65 * inch, 1.25 * inch, .95 * inch, 1.05 * inch], ["L", "L", "R", "R", "R", "R"], 8.3))

story.append(PageBreak())
story.append(Paragraph(f"Top five posts - {week_labels[REPORT['week']]}", H2))
for platform in PLATFORMS:
    top_posts = [post for post in S["top5"][REPORT["week"]].get(platform, []) if post["views"] > 0]
    if not top_posts:
        continue
    block = [Paragraph(f'<font color="{COLORS[platform]}">&#9632;</font>&nbsp; {platform}', H3)]
    post_rows = [["#", "Date", "Category", "Post", "Views / impr.", "Eng."]]
    for index, post in enumerate(top_posts, 1):
        title = safe((post["title"] or "").replace("\n", " ")[:135] or "(no text)")
        if post["url"]:
            title = f'<a href="{safe(post["url"])}" color="#8f1e2c"><u>{title}</u></a>'
        post_rows.append([
            str(index), post["date"][5:], post["category"], Paragraph(title, CELL), full(post["views"]), full(post["engagements"]),
        ])
    block.append(make_table(post_rows, [.28 * inch, .52 * inch, 1.15 * inch, 5.05 * inch, .9 * inch, .7 * inch], ["L", "L", "L", "L", "R", "R"], 7.6))
    story.extend([KeepTogether(block), Spacer(1, 4)])

story.append(Paragraph("Source coverage", H2))
source_rows = [[Paragraph(f"- {safe(note)}", NOTE)] for note in S["source_notes"]]
source_table = Table(source_rows, colWidths=[9.2 * inch])
source_table.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 1),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
]))
story.append(source_table)

output = os.path.join(ROOT, "summary.pdf")
SimpleDocTemplate(
    output,
    pagesize=landscape(letter),
    leftMargin=.55 * inch,
    rightMargin=.55 * inch,
    topMargin=.5 * inch,
    bottomMargin=.5 * inch,
    title=f"{BRAND} - Social Performance Summary, {scope_label} {year}",
    author=BRAND,
).build(story)
print(output, f"{os.path.getsize(output) / 1024:.0f} KB")

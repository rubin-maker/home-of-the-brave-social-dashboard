# HOTB Social Dashboard — Data Handoff

## Source contracts

The build reads only the normalized raw-data tabs below. Overview and category sheets remain useful for human review, but the dashboard recomputes every total from post-level rows.

| Platform | Workbook | Source sheet(s) | Publish date | Headline metric | Engagements |
|---|---|---|---|---|---|
| YouTube | `youtube.xlsx` | `Long Data`, `Shorts Data` | `Video publish time` | Views | Likes + shares + comments |
| Instagram | `instagram.xlsx` | `IG Data` | `Publish time` | Views | Likes + comments + shares + saves |
| TikTok | `tiktok.xlsx` | `TT Data` | `Publish time` | Views | Source `Total Engagements` |
| X | `x.xlsx` | `X Data` | `Date` | Impressions (source column is named `Views`) | Source `Engagements` |

The combined headline is therefore labeled **views / impressions**. It is useful as a volume indicator, but it is not a standardized cross-platform measure. Engagement rate is calculated as engagements divided by the platform's headline metric.

## Reporting scope

- The YouTube subscriber card sums the source workbook's `Subscribers` field across included Long Data and Shorts Data rows. The workbook explicitly says not to relabel it as `Subscribers gained`. It is not a live channel subscriber count or net growth.
- The subscriber table groups that same source metric by Monday–Sunday publish week, with long-form, Shorts, and total columns. The selector shows the latest eight complete weeks or all exported weeks. Weeks ending after YouTube's source cutoff are labeled partial. Shown-weeks and all-weeks totals reconcile to the same included rows. These are cumulative video-attributed source values, not weekly-earned gains or week-end subscriber balances.

- Weeks run Monday–Sunday and are assigned by publish date.
- The reporting week is the latest fully closed week supported by all four platforms. It uses the earliest platform coverage end, while full-file totals retain each platform's own available period.
- The trend table keeps the latest eight complete weeks.
- The Instagram, YouTube, and TikTok category line charts retain every available 2026 publish week. Their axes use week-start dates instead of ISO week numbers, and each chart stops at that platform's latest included publish date.
- Year-to-date totals, category tables, and the post explorer use every source row.
- Metrics are current cumulative values attributed to publish date; they are not activity earned only during that week.

## Validation before sharing

1. Compare the build digest's post and view totals with each workbook Overview total.
2. Confirm the reported week is fully complete for all four sources.
3. Scan the final days in `all_posts.csv` for unexpected zero-value or duplicate rows.
4. Check that old weeks do not move unexpectedly when replacing a workbook.
5. Open `dashboard.html` and test the category tabs, full-year category-chart scrolling and date labels, week tabs, platform filter, search, and outbound post links.

## 2026 source coverage in this build

- YouTube: cumulative per-video data through Sep 10; 533 included videos (55 long-form and 478 Shorts).
- Instagram: reviewed Meta export through Aug 26; 582 posts.
- TikTok: reviewed export through Aug 27; 563 posts.
- X: merged account analytics and scrape through Aug 26; 969 authored posts, reposts excluded.
- The updated YouTube workbook retains but excludes aggregate rows, 244 undated long-form rows, and rows outside 2026, matching its `Analysis Status` field.
- The workbook has 1,002 cached `#VALUE!` cells in weekly delta columns for blank weeks. The dashboard does not use those formulas; it recomputes every displayed YouTube metric from the 533 included raw rows.

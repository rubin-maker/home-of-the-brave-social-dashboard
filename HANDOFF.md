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

- The YouTube subscriber card sums `Subscribers gained` across all exported Long Data and Shorts Data videos. It is not the separate `Subscribers` field, a live channel subscriber count, or net growth. The current channel total is unavailable in these files.
- The subscriber table groups those same gains by Monday–Sunday publish week, with long-form, Shorts, and total columns. The local selector shows the latest eight complete weeks or all exported weeks. Weeks ending after YouTube's source cutoff are labeled partial; the shown-weeks sum reconciles to the selected rows, and the all-weeks sum reconciles to the subscriber card. These are cumulative video-attributed gains, not weekly-earned gains or week-end subscriber balances.

- Weeks run Monday–Sunday and are assigned by publish date.
- The reporting week is the latest fully closed week before the newest post date in the source files.
- The trend table keeps the latest eight complete weeks.
- Year-to-date totals, category tables, and the post explorer use every source row.
- Metrics are current cumulative values attributed to publish date; they are not activity earned only during that week.

## Validation before sharing

1. Compare the build digest's post and view totals with each workbook Overview total.
2. Confirm the reported week is fully complete for all four sources.
3. Scan the final days in `all_posts.csv` for unexpected zero-value or duplicate rows.
4. Check that old weeks do not move unexpectedly when replacing a workbook.
5. Open `dashboard.html` and test the category tabs, week tabs, platform filter, search, and outbound post links.

## 2026 source coverage in this build

- YouTube: cumulative per-video data through Aug 25; 477 videos.
- Instagram: reviewed Meta export through Aug 26; 582 posts.
- TikTok: reviewed export through Aug 27; 563 posts.
- X: merged account analytics and scrape through Aug 26; 969 authored posts, reposts excluded.

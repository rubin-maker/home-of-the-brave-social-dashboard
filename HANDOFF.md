# HOTB Social Dashboard — Data Handoff

## Source contracts

The build reads only the normalized raw-data tabs below. Overview and category sheets remain useful for human review, but the dashboard recomputes every total from post-level rows.

| Platform | Workbook | Source sheet(s) | Publish date | Headline metric | Engagements |
|---|---|---|---|---|---|
| YouTube | `youtube_long.csv` + `youtube.xlsx` + `youtube_shorts_likes.csv` | current long-form snapshot + reviewed `Shorts Data` + five-video Likes patch | `Video publish time` | Views | Likes + shares + comments |
| Instagram | `instagram.xlsx` | `IG Data` | `Publish time` | Views | Likes + comments + shares + saves |
| TikTok | `tiktok.xlsx` | `TT Data` | `Publish time` | Views | Likes + comments + shares + bookmarks |
| X | `x.xlsx` | `X Data` | `Date` | Impressions (source column is named `Views`) | Source `Engagements` |

The combined headline is therefore labeled **views / impressions**. It is useful as a volume indicator, but it is not a standardized cross-platform measure. Engagement rate is calculated as engagements divided by the platform's headline metric.

For X, the dashboard preserves the source-reported `Engagements` field. Analytics-export and earlier raw-scrape rows can include actions beyond likes, replies, reposts, and bookmarks, while the 41 Sep 10 scrape rows use the visible component sum. Those source eras are therefore not perfectly identical engagement definitions. Rows that are themselves reposted posts were excluded upstream; the `Reposts` interaction count is retained.

For TikTok, eight refreshed rows have a `Total Engagements` value that disagrees with their visible components. The dashboard therefore uses the same explicit component sum for all 636 rows: Likes + Comments + Shares + Bookmarks. The source total remains available for audit but is not mixed into the dashboard metric.

## Reporting scope

- The YouTube subscriber card sums the source workbook's `Subscribers` field across included Long Data and Shorts Data rows. The workbook explicitly says not to relabel it as `Subscribers gained`. It is not a live channel subscriber count or net growth.
- The subscriber table groups that same source metric by Monday–Sunday publish week, with long-form, Shorts, and total columns. The selector shows the latest eight complete weeks or all exported weeks. Weeks ending after the Sep 10 full-Shorts cutoff are labeled partial source-mix weeks. Shown-weeks and all-weeks totals reconcile to the same included rows. These are cumulative video-attributed source values, not weekly-earned gains or week-end subscriber balances.

- Weeks run Monday–Sunday and are assigned by publish date.
- The reporting week is the latest fully closed week supported by complete source coverage on all four platforms. Publishing coverage extends through Sep 18, but YouTube's full Shorts catalog is complete only through Sep 10, so the shared headline remains Week 36 (Aug 31–Sep 6).
- The trend table keeps the latest eight complete weeks.
- The top-five selector retains those shared context weeks and extends through the latest publish week available in any source. It opens on the newest week with no partially covered platform; newer partial weeks remain selectable. Each platform remains visible and is labeled complete, partial, or unavailable; unavailable coverage is never presented as zero posts.
- Each platform card's mini bars use that platform's latest eight consecutive publish weeks through its own source cutoff, including zero-post weeks. A cutoff in the middle of a week produces an outlined partial bar labeled with its exact covered dates and day count. YouTube also outlines W37 and W38 as partial source-mix weeks because the full Shorts catalog stops Sep 10.
- Each platform-card headline defaults to that source's latest complete week and shows the exact date range; the hero and trend table retain the shared complete comparison week. Selecting any mini bar updates only that card with the chosen week's exact metrics and coverage status.
- The Instagram, YouTube, and TikTok category line charts retain every available 2026 publish week. Their axes use week-start dates instead of ISO week numbers, and each chart stops at that platform's latest included publish date.
- Each category chart includes a thicker dashed **All categories** line that sums every category for that platform and week.
- Every category-chart point is selectable. Its detail panel lists the top three videos or posts published in that exact week, ranked by the active metric, with exact publish dates and outbound links. In Posts mode, contributors are ranked by views.
- Year-to-date totals, category tables, and the post explorer use every source row.
- Metrics are current cumulative values attributed to publish date; they are not activity earned only during that week.

## Validation before sharing

1. Compare the build digest's post and view totals with each workbook Overview total.
2. Confirm the reported week is fully complete for all four sources.
3. Scan the final days in `all_posts.csv` for unexpected zero-value or duplicate rows.
4. Check that old weeks do not move unexpectedly when replacing a workbook.
5. Open `dashboard.html` and test the selectable eight-week platform bars, category tabs, **Show all** and **Deselect all** controls, full-year category-chart scrolling and date labels, top-five week tabs and mobile selector (including partial and unavailable states), platform filter, search, and outbound post links.

## 2026 source coverage in this build

- YouTube: 535 included videos (57 refreshed long-form and 478 retained Shorts). Long-form is refreshed through Sep 18. The full Shorts catalog and all non-Likes Shorts metrics remain at the reviewed Sep 10 snapshot; Likes were refreshed through Sep 17 for five matched Shorts only.
- Instagram: publishing coverage through Sep 18, 659 reviewed posts, latest post Sep 17. One Empathy Tour collaboration remains flagged in the source for authorship review and is included.
- TikTok: publishing coverage through Sep 18, 636 reviewed posts, latest post Sep 17. Dashboard engagements total 81,331 from visible components; the inconsistent source `Total Engagements` column sums to 80,838.
- X: publishing coverage through Sep 18, 1,037 authored posts, latest post Sep 17. Rows that are themselves reposted posts were excluded upstream.
- Recent-post metrics were refreshed Sep 18; earlier rows can retain prior export snapshots as documented in each workbook's Definitions sheet.
- The long-form YouTube CSV retains but excludes one aggregate row, 245 undated rows, and 19 rows outside 2026.

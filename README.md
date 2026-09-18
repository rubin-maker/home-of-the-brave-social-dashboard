# Home of the Brave Social Dashboard

A reproducible 2026 reporting project for YouTube, Instagram, TikTok, and X. It turns the four reviewed platform workbooks in `sources/` into:

- `dashboard.html` — self-contained interactive dashboard
- `index.html` — deployment entry point (same dashboard)
- `summary.pdf` — printable weekly summary
- `all_posts.csv` — normalized year-to-date post-level dataset
- `summary.json` — one shared data layer used by both reports
- `validation.json` — reconciliation checks for the generated dashboard

## Build

```bash
python3 -m pip install -r requirements.txt
./build.sh
```

You can select a different Python interpreter with:

```bash
PYTHON=/path/to/python ./build.sh
```

## Updating the data

Replace these files with refreshed sources that preserve the current raw-data sheet names and headers:

- `sources/youtube.xlsx` — reviewed full Shorts catalog and category map
- `sources/youtube_long.csv` — authoritative current long-form snapshot
- `sources/youtube_shorts_likes.csv` — optional daily Likes patch for matched Shorts
- `sources/instagram.xlsx`
- `sources/tiktok.xlsx`
- `sources/x.xlsx`

Then run `./build.sh`. The headline period is selected automatically as the newest fully complete Monday–Sunday week across the source coverage dates. The platform trend table keeps eight complete weeks of shared context. The top-post selector retains those context weeks and extends through the newest covered publish week, labeling complete, partial, mixed-source, and unavailable coverage separately. The category line charts show every available 2026 publish week through each platform's data-through date, with week-start dates on the axis. Their **Subscribers / Follows** mode uses Instagram `Follows` and YouTube `Subscribers`; TikTok is labeled unavailable because its export has no comparable field. These values are current post- or video-attributed source metrics grouped by publish week, not account balances or a record of when audience changes occurred. The post explorer retains the entire available file.

The YouTube importer uses the current long-form CSV for dated 2026 long videos and preserves reviewed categories from `youtube.xlsx`. The full `Shorts Data` tab remains authoritative for the Shorts catalog and all non-Likes metrics. The supplied Sep 18 Shorts CSV contains daily Likes for only five existing videos, so it patches only those five Likes totals; it does not replace the Shorts catalog. Aggregate rows, undated rows, and rows outside 2026 remain outside dashboard analysis.

TikTok engagements are recomputed consistently as Likes + Comments + Shares + Bookmarks. This avoids mixing the workbook's eight inconsistent `Total Engagements` cells with component-derived rows.

See `HANDOFF.md` for metric definitions, source-sheet assumptions, and validation checks.

## Railway deployment

The included zero-dependency Node server serves the generated dashboard and downloads while listening on Railway's assigned `PORT`.

```bash
npm start
```

The public routes are `/`, `/summary.pdf`, and `/all_posts.csv`.

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

Replace these files with refreshed workbooks that preserve the current raw-data sheet names and headers:

- `sources/youtube.xlsx`
- `sources/instagram.xlsx`
- `sources/tiktok.xlsx`
- `sources/x.xlsx`

Then run `./build.sh`. The headline period is selected automatically as the newest fully complete Monday–Sunday week across the file dates. The platform trend table and top-post tabs keep eight complete weeks of context. The category line charts show every available 2026 publish week through each platform's latest included publish date, with week-start dates on the axis. The post explorer retains the entire available file.

The YouTube importer honors the workbook's `Analysis Status` field when it is present, using only `Included` rows. It accepts the legacy `Subscribers gained` and current `Subscribers` column names, but preserves the current workbook's metric label in the dashboard. Aggregate rows, undated rows, and rows outside 2026 stay in the source workbook and remain outside dashboard analysis.

See `HANDOFF.md` for metric definitions, source-sheet assumptions, and validation checks.

## Railway deployment

The included zero-dependency Node server serves the generated dashboard and downloads while listening on Railway's assigned `PORT`.

```bash
npm start
```

The public routes are `/`, `/summary.pdf`, and `/all_posts.csv`.

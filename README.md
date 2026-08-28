# Home of the Brave Social Dashboard

A reproducible 2026 reporting project for YouTube, Instagram, TikTok, and X. It turns the four reviewed platform workbooks in `sources/` into:

- `dashboard.html` — self-contained interactive dashboard
- `index.html` — deployment entry point (same dashboard)
- `summary.pdf` — printable weekly summary
- `all_posts.csv` — normalized year-to-date post-level dataset
- `summary.json` — one shared data layer used by both reports

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

Then run `./build.sh`. The headline period is selected automatically as the newest fully complete Monday–Sunday week across the file dates. The dashboard keeps eight complete weeks of trend context and the entire available file in its post explorer.

See `HANDOFF.md` for metric definitions, source-sheet assumptions, and validation checks.

## Railway deployment

The included zero-dependency Node server serves the generated dashboard and downloads while listening on Railway's assigned `PORT`.

```bash
npm start
```

The public routes are `/`, `/summary.pdf`, and `/all_posts.csv`.

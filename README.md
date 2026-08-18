# Weekly GitHub Hot Repositories

Automatically fetches the hottest GitHub repositories from the past 7 days, organized into 18 categories (TOP 10 each), and publishes as a GitHub Pages site every Monday.

## Setup

1. Push this repository to GitHub.
2. Enable **Settings → Pages → Source: GitHub Actions**.
3. Run the workflow manually once (**Actions → Weekly GitHub Hot Repositories → Run workflow**), or wait for the next Monday at 09:00 UTC.

## Site Structure

After the first run, the deployed site will have the following structure:

```
/                   ← Archive listing (index of all weekly reports)
/latest.html        ← Redirects to the most recent report
/reports/
  2026-W33.html     ← Individual weekly report (ISO week number)
  2026-W32.html
  ...
```

- **Archive page (`/`)** — Lists every historical report with its week number, date range, and a direct link. Newest reports appear first.
- **Latest report (`/latest.html`)** — Always redirects to the most recently generated report.
- **Individual reports (`/reports/YYYY-WXX.html`)** — Standalone HTML pages with the full TOP 10 per category for that week. Each report includes a navigation bar to return to the archive.

## How History Is Preserved

Each workflow run:
1. Generates a new report file at `site/reports/YYYY-WXX.html`.
2. Regenerates `site/index.html` (archive listing) and `site/latest.html` (redirect).
3. **Commits all files in `site/` back to the main branch**, so historical reports accumulate in the repository over time.
4. Deploys the updated `site/` directory to GitHub Pages.

Because reports are committed to the repository, they are never lost between runs.

## Notes

- Rankings are based on recent pushes, stars, and forks. GitHub does not expose a single official field for stars gained in exactly seven days.
- A `GITHUB_TOKEN` with default permissions is sufficient; no additional secrets are required.
- If fewer than 10 repositories match a category's topics in the 7-day window, only the available results are shown — no data is fabricated.

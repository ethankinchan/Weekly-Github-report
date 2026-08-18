import os, html, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

TOKEN = os.getenv('GITHUB_TOKEN', '')
OUT = Path('site')
DAYS = 7
LIMIT = 10

CATS = {
    'AI / LLM / Agents': ['artificial-intelligence', 'llm', 'agents'],
    'Productivity / Workflow Automation': ['automation', 'productivity', 'workflow'],
    'Developer Tools / CLI / IDE': ['developer-tools', 'cli', 'ide'],
    'DevOps / Cloud / Infrastructure': ['devops', 'cloud', 'infrastructure'],
    'Data Engineering / Analytics': ['data-engineering', 'analytics', 'data-analysis'],
    'Web Development / Frontend': ['web', 'frontend', 'javascript'],
    'Mobile Development': ['android', 'ios', 'mobile-development'],
    'Security / Privacy / Cybersecurity': ['security', 'privacy', 'cybersecurity'],
    'Design / UI / UX': ['design', 'ui', 'ux'],
    'Education / Learning / Knowledge Management': ['education', 'learning', 'knowledge-management'],
    'Personal Life / Utilities': ['utilities', 'self-hosted', 'personal'],
    'Writing / Docs / Note-taking': ['documentation', 'notes', 'markdown'],
    'Finance / Investing / Personal Finance': ['finance', 'fintech', 'personal-finance'],
    'Multimedia / Image / Video / Audio': ['multimedia', 'image-processing', 'video'],
    'System Tools / Terminal / OS Utilities': ['terminal', 'linux', 'system-tools'],
    'Research / Science / Academic Tools': ['research', 'science', 'academic'],
    'Translation / Localization / Language Tools': ['translation', 'localization', 'nlp'],
    'Home / Smart Home / IoT': ['home-automation', 'smart-home', 'iot'],
}

CSS = '''body{margin:0;background:#0b1020;color:#e9eefc;font:14px/1.5 system-ui,sans-serif}.wrap{max-width:1800px;margin:auto;padding:24px 16px 56px}a{color:#9fc0ff;text-decoration:none}a:hover{text-decoration:underline}.hero,.panel,.cat{border:1px solid #26314f;border-radius:18px;background:#121a33}.hero{padding:24px;background:linear-gradient(135deg,#17294a,#122b32)}h1{margin:0 0 8px}.muted{color:#aab5d3}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}.stat{padding:14px;border:1px solid #26314f;border-radius:14px;background:#0f1730}.stat b{display:block;font-size:24px}.panel{margin-top:16px;padding:16px}.toc a{display:inline-block;margin:4px;padding:6px 10px;border:1px solid #26314f;border-radius:999px;font-size:12px}.cat{margin-top:16px;overflow:hidden}.head{padding:16px;border-bottom:1px solid #26314f;background:#151f3b}.head h2{margin:0}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;min-width:1200px}th,td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #202b48}th{color:#aab5d3;background:#0f1730;position:sticky;top:0}.rank{font-size:18px;color:#7cf0c5;font-weight:bold}.repo{font-weight:bold;font-size:15px}.pill{display:inline-block;border:1px solid #334263;border-radius:999px;padding:3px 7px;font-size:11px;margin:2px}.empty{padding:16px;color:#ffd166}.footer{margin-top:20px;color:#8f9bbb;font-size:12px}.nav-bar{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}.nav-bar a{padding:6px 14px;border:1px solid #26314f;border-radius:999px;font-size:13px;background:#121a33}.archive-list{list-style:none;margin:0;padding:0}.archive-list li{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid #202b48;flex-wrap:wrap;gap:8px}.archive-list li:last-child{border-bottom:none}.archive-list li:hover{background:#151f3b}.archive-week{font-weight:bold;font-size:15px;color:#7cf0c5}.archive-range{color:#aab5d3;font-size:13px}.archive-link{padding:5px 14px;border:1px solid #26314f;border-radius:999px;font-size:12px;background:#0f1730}.latest-badge{display:inline-block;margin-left:8px;padding:2px 8px;border-radius:999px;background:#7cf0c5;color:#0b1020;font-size:11px;font-weight:bold}@media(max-width:700px){.stats{grid-template-columns:repeat(2,1fr)}}'''


def api(path):
    h = {'Accept': 'application/vnd.github+json', 'User-Agent': 'weekly-report'}
    if TOKEN:
        h['Authorization'] = 'Bearer ' + TOKEN
    with urlopen(Request('https://api.github.com' + path, headers=h), timeout=30) as r:
        return json.loads(r.read())


def esc(x):
    return html.escape(str(x or ''))


def week_date_range(week_id):
    """Return (monday, sunday) datetime objects for a given 'YYYY-WXX' week_id."""
    year_str, week_str = week_id.split('-W')
    year, week = int(year_str), int(week_str)
    monday = datetime.strptime(f'{year}-W{week:02d}-1', '%G-W%V-%u')
    sunday = monday + timedelta(days=6)
    return monday, sunday


def format_date_range(week_id):
    """Return a human-readable date range string like 'Aug 10 – Aug 16, 2026'."""
    monday, sunday = week_date_range(week_id)
    if monday.year == sunday.year and monday.month == sunday.month:
        return f"{monday.strftime('%b %-d')} – {sunday.strftime('%-d, %Y')}"
    elif monday.year == sunday.year:
        return f"{monday.strftime('%b %-d')} – {sunday.strftime('%b %-d, %Y')}"
    else:
        return f"{monday.strftime('%b %-d, %Y')} – {sunday.strftime('%b %-d, %Y')}"


def generate_report_html(result, allrows, now, week_id):
    """Generate the full HTML for a weekly report page."""
    date_range = format_date_range(week_id)
    o = [
        "<!doctype html><html><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Weekly GitHub Hot Repositories — {week_id}</title>"
        "<style>", CSS, "</style></head><body><main class='wrap'>"
    ]
    # Navigation bar
    o.append(
        "<nav class='nav-bar'>"
        "<a href='../index.html'>🗂️ Archive</a>"
        "<a href='../latest.html'>⚡ Latest</a>"
        "</nav>"
    )
    # Hero section
    o.append(
        f"<section class='hero'>"
        f"<h1>🔥 Weekly GitHub Hot Repositories</h1>"
        f"<p class='muted'>{date_range} · Generated {now.strftime('%Y-%m-%d %H:%M UTC')}</p>"
        f"<div class='stats'>"
        f"<div class='stat'><b>{len(CATS)}</b><span class='muted'>categories</span></div>"
        f"<div class='stat'><b>{len(allrows)}</b><span class='muted'>repositories</span></div>"
        f"<div class='stat'><b>{LIMIT}</b><span class='muted'>target/category</span></div>"
        f"<div class='stat'><b>7d</b><span class='muted'>activity window</span></div>"
        f"</div></section>"
    )
    # TOC
    o.append(
        "<section class='panel toc'><h2>Categories</h2>"
        + ''.join(f"<a href='#{quote(c, safe='')}'>{esc(c)}</a>" for c in CATS)
        + "</section>"
    )
    # Top picks
    o.append(
        "<section class='panel'><h2>🏆 Top Picks</h2><ol>"
        + ''.join(
            f"<li><a target='_blank' href='{esc(r['html_url'])}'>{esc(r['full_name'])}</a>"
            f" — {esc(r.get('description') or 'No description')}</li>"
            for r in allrows[:10]
        )
        + "</ol></section>"
    )
    # Category sections
    for cat, rows in result.items():
        o.append(
            f"<section class='cat' id='{quote(cat, safe='')}'>"
            f"<div class='head'><h2>{esc(cat)}</h2>"
            f"<p class='muted'>{len(rows)} result(s) found. "
            f"Fewer than 10 strong results are shown when applicable.</p></div>"
        )
        if not rows:
            o.append("<div class='empty'>No strong results found in this window.</div>")
        else:
            o.append(
                "<div class='scroll'><table><thead><tr>"
                "<th>Rank</th><th>Repository</th><th>Summary</th>"
                "<th>Features</th><th>Tools / technologies</th>"
                "<th>Language</th><th>Stars</th><th>Forks</th>"
                "<th>Last updated</th><th>Why useful / trending</th>"
                "</tr></thead><tbody>"
            )
            for i, r in enumerate(rows, 1):
                topics = r.get('topics') or []
                features = ''.join(f"<span class='pill'>{esc(t)}</span>" for t in topics[:8]) or '—'
                tech = ', '.join(topics[:6]) or 'See repository documentation'
                pushed = (r.get('pushed_at') or '')[:10] or '—'
                why = (
                    f"Recent activity in the last {DAYS} days; "
                    f"{r.get('stargazers_count', 0):,} stars and "
                    f"{r.get('forks_count', 0):,} forks."
                )
                o.append(
                    f"<tr>"
                    f"<td class='rank'>{i}</td>"
                    f"<td class='repo'><a target='_blank' href='{esc(r['html_url'])}'>{esc(r['full_name'])}</a></td>"
                    f"<td>{esc(r.get('description') or 'No description')}</td>"
                    f"<td>{features}</td>"
                    f"<td>{esc(tech)}</td>"
                    f"<td>{esc(r.get('language') or '—')}</td>"
                    f"<td>{r.get('stargazers_count', 0):,}</td>"
                    f"<td>{r.get('forks_count', 0):,}</td>"
                    f"<td>{pushed}</td>"
                    f"<td>{esc(why)}</td>"
                    f"</tr>"
                )
            o.append('</tbody></table></div>')
        o.append('</section>')

    o.append(
        "<p class='footer'>Data source: official GitHub public API and repository pages. "
        "Check license, security, and maintenance before adoption.</p>"
        "</main></body></html>"
    )
    return ''.join(o)


def generate_index(out_dir, latest_week_id):
    """Generate site/index.html as an archive listing of all weekly reports."""
    reports_dir = out_dir / 'reports'
    report_files = sorted(reports_dir.glob('*.html'), reverse=True)

    rows_html = []
    for i, f in enumerate(report_files):
        week_id = f.stem  # e.g. "2026-W33"
        try:
            date_range = format_date_range(week_id)
        except Exception:
            date_range = '—'
        is_latest = (week_id == latest_week_id)
        badge = "<span class='latest-badge'>LATEST</span>" if is_latest else ""
        rows_html.append(
            f"<li>"
            f"<span><span class='archive-week'>{esc(week_id)}</span>{badge}</span>"
            f"<span class='archive-range'>{esc(date_range)}</span>"
            f"<a class='archive-link' href='reports/{esc(f.name)}'>View Report →</a>"
            f"</li>"
        )

    count = len(report_files)
    o = [
        "<!doctype html><html><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Weekly GitHub Hot Repositories — Archive</title>"
        "<style>", CSS, "</style></head><body><main class='wrap'>"
    ]
    o.append(
        "<section class='hero'>"
        "<h1>🗂️ Weekly GitHub Hot Repositories — Archive</h1>"
        "<p class='muted'>Browse all historical weekly reports. "
        "New reports are generated every Monday.</p>"
        "<div class='stats'>"
        f"<div class='stat'><b>{count}</b><span class='muted'>reports archived</span></div>"
        f"<div class='stat'><b>{len(CATS)}</b><span class='muted'>categories / report</span></div>"
        f"<div class='stat'><b>{LIMIT}</b><span class='muted'>repos / category</span></div>"
        "<div class='stat'><b>7d</b><span class='muted'>activity window</span></div>"
        "</div></section>"
    )
    o.append(
        "<section class='panel' style='margin-top:16px'>"
        "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px'>"
        "<h2 style='margin:0'>All Reports</h2>"
        "<a class='archive-link' href='latest.html'>⚡ View Latest Report →</a>"
        "</div>"
    )
    if rows_html:
        o.append("<ul class='archive-list'>" + ''.join(rows_html) + "</ul>")
    else:
        o.append("<p class='muted' style='padding:16px'>No reports generated yet. Run the workflow to generate the first report.</p>")
    o.append("</section>")
    o.append(
        "<p class='footer'>Data source: official GitHub public API and repository pages. "
        "Check license, security, and maintenance before adoption.</p>"
        "</main></body></html>"
    )
    (out_dir / 'index.html').write_text(''.join(o), encoding='utf-8')


def generate_latest(out_dir, week_id):
    """Generate site/latest.html that redirects to the most recent report."""
    report_url = f'reports/{week_id}.html'
    content = (
        "<!doctype html><html><head>"
        "<meta charset='utf-8'>"
        f"<meta http-equiv='refresh' content='0;url={report_url}'>"
        "<title>Latest Weekly Report — Redirecting…</title>"
        "<style>body{margin:0;background:#0b1020;color:#e9eefc;font:14px/1.5 system-ui,sans-serif;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh}"
        ".box{text-align:center;padding:32px}a{color:#9fc0ff}</style>"
        "</head><body>"
        "<div class='box'>"
        "<p>Redirecting to the latest report…</p>"
        f"<p><a href='{report_url}'>Click here if not redirected automatically</a></p>"
        "<p><a href='index.html'>← Back to Archive</a></p>"
        "</div>"
        "</body></html>"
    )
    (out_dir / 'latest.html').write_text(content, encoding='utf-8')


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'reports').mkdir(exist_ok=True)

    now = datetime.now(timezone.utc)
    week_id = now.strftime('%G-W%V')  # ISO week, e.g. "2026-W33"

    since = (now - timedelta(days=DAYS)).date().isoformat()
    result = {}
    seen = set()

    for cat, tags in CATS.items():
        q = quote('pushed:>' + since + ' ' + ' '.join('topic:' + t for t in tags))
        try:
            items = api('/search/repositories?q=' + q + '&sort=stars&order=desc&per_page=30').get('items', [])
        except Exception as e:
            print(cat, e)
            items = []
        rows = []
        for r in items:
            if r['full_name'] in seen:
                continue
            seen.add(r['full_name'])
            rows.append(r)
        result[cat] = rows[:LIMIT]

    allrows = [r for rows in result.values() for r in rows]
    allrows.sort(key=lambda r: (r.get('stargazers_count', 0), r.get('forks_count', 0)), reverse=True)

    # Save individual weekly report
    report_html = generate_report_html(result, allrows, now, week_id)
    report_path = OUT / 'reports' / f'{week_id}.html'
    report_path.write_text(report_html, encoding='utf-8')
    print(f'Report saved: {report_path}')

    # Generate archive index
    generate_index(OUT, week_id)
    print(f'Archive index updated: {OUT / "index.html"}')

    # Generate latest.html redirect
    generate_latest(OUT, week_id)
    print(f'Latest redirect updated: {OUT / "latest.html"}')


if __name__ == '__main__':
    main()

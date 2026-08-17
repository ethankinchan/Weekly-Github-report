import os, html, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
TOKEN=os.getenv('GITHUB_TOKEN',''); OUT=Path('site'); DAYS=7; LIMIT=10
CATS={
'AI / LLM / Agents':['artificial-intelligence','llm','agents'],'Productivity / Workflow Automation':['automation','productivity','workflow'],'Developer Tools / CLI / IDE':['developer-tools','cli','ide'],'DevOps / Cloud / Infrastructure':['devops','cloud','infrastructure'],'Data Engineering / Analytics':['data-engineering','analytics','data-analysis'],'Web Development / Frontend':['web','frontend','javascript'],'Mobile Development':['android','ios','mobile-development'],'Security / Privacy / Cybersecurity':['security','privacy','cybersecurity'],'Design / UI / UX':['design','ui','ux'],'Education / Learning / Knowledge Management':['education','learning','knowledge-management'],'Personal Life / Utilities':['utilities','self-hosted','personal'],'Writing / Docs / Note-taking':['documentation','notes','markdown'],'Finance / Investing / Personal Finance':['finance','fintech','personal-finance'],'Multimedia / Image / Video / Audio':['multimedia','image-processing','video'],'System Tools / Terminal / OS Utilities':['terminal','linux','system-tools'],'Research / Science / Academic Tools':['research','science','academic'],'Translation / Localization / Language Tools':['translation','localization','nlp'],'Home / Smart Home / IoT':['home-automation','smart-home','iot']}
CSS='''body{margin:0;background:#0b1020;color:#e9eefc;font:14px/1.5 system-ui,sans-serif}.wrap{max-width:1800px;margin:auto;padding:24px 16px 56px}a{color:#9fc0ff;text-decoration:none}a:hover{text-decoration:underline}.hero,.panel,.cat{border:1px solid #26314f;border-radius:18px;background:#121a33}.hero{padding:24px;background:linear-gradient(135deg,#17294a,#122b32)}h1{margin:0 0 8px}.muted{color:#aab5d3}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}.stat{padding:14px;border:1px solid #26314f;border-radius:14px;background:#0f1730}.stat b{display:block;font-size:24px}.panel{margin-top:16px;padding:16px}.toc a{display:inline-block;margin:4px;padding:6px 10px;border:1px solid #26314f;border-radius:999px;font-size:12px}.cat{margin-top:16px;overflow:hidden}.head{padding:16px;border-bottom:1px solid #26314f;background:#151f3b}.head h2{margin:0}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;min-width:1200px}th,td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #202b48}th{color:#aab5d3;background:#0f1730;position:sticky;top:0}.rank{font-size:18px;color:#7cf0c5;font-weight:bold}.repo{font-weight:bold;font-size:15px}.pill{display:inline-block;border:1px solid #334263;border-radius:999px;padding:3px 7px;font-size:11px;margin:2px}.empty{padding:16px;color:#ffd166}.footer{margin-top:20px;color:#8f9bbb;font-size:12px}@media(max-width:700px){.stats{grid-template-columns:repeat(2,1fr)}}'''
def api(path):
 h={'Accept':'application/vnd.github+json','User-Agent':'weekly-report'}
 if TOKEN:h['Authorization']='Bearer '+TOKEN
 with urlopen(Request('https://api.github.com'+path,headers=h),timeout=30) as r:return json.loads(r.read())
def esc(x):return html.escape(str(x or ''))
def main():
 OUT.mkdir(exist_ok=True); since=(datetime.now(timezone.utc)-timedelta(days=DAYS)).date().isoformat(); result={}; seen=set()
 for cat,tags in CATS.items():
  q=quote('pushed:>'+since+' '+' '.join('topic:'+t for t in tags))
  try: items=api('/search/repositories?q='+q+'&sort=stars&order=desc&per_page=30').get('items',[])
  except Exception as e: print(cat,e); items=[]
  rows=[]
  for r in items:
   if r['full_name'] in seen:continue
   seen.add(r['full_name']); rows.append(r)
  result[cat]=rows[:LIMIT]
 allrows=[r for rows in result.values() for r in rows]; allrows.sort(key=lambda r:(r.get('stargazers_count',0),r.get('forks_count',0)),reverse=True)
 o=["<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Weekly GitHub Hot Repositories</title><style>",CSS,"</style></head><body><main class='wrap'>"]
 o.append(f"<section class='hero'><h1>🔥 Weekly GitHub Hot Repositories</h1><p class='muted'>Last {DAYS} days · Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p><div class='stats'><div class='stat'><b>{len(CATS)}</b><span class='muted'>categories</span></div><div class='stat'><b>{len(allrows)}</b><span class='muted'>repositories</span></div><div class='stat'><b>{LIMIT}</b><span class='muted'>target/category</span></div><div class='stat'><b>7d</b><span class='muted'>activity window</span></div></div></section>")
 o.append("<section class='panel toc'><h2>Categories</h2>"+''.join(f"<a href='#{quote(c,safe='')}'>{esc(c)}</a>" for c in CATS)+"</section>")
 o.append("<section class='panel'><h2>🏆 Top Picks</h2><ol>"+''.join(f"<li><a target='_blank' href='{esc(r['html_url'])}'>{esc(r['full_name'])}</a> — {esc(r.get('description') or 'No description')}</li>" for r in allrows[:10])+"</ol></section>")
 for cat,rows in result.items():
  o.append(f"<section class='cat' id='{quote(cat,safe='')}'><div class='head'><h2>{esc(cat)}</h2><p class='muted'>{len(rows)} result(s) found. Fewer than 10 strong results are shown when applicable.</p></div>")
  if not rows:o.append("<div class='empty'>No strong results found in this window.</div>")
  else:
   o.append("<div class='scroll'><table><thead><tr><th>Rank</th><th>Repository</th><th>Summary</th><th>Features</th><th>Tools / technologies</th><th>Language</th><th>Stars</th><th>Forks</th><th>Last updated</th><th>Why useful / trending</th></tr></thead><tbody>")
   for i,r in enumerate(rows,1):
    topics=r.get('topics') or []; features=''.join(f"<span class='pill'>{esc(t)}</span>" for t in topics[:8]) or '—'; tech=', '.join(topics[:6]) or 'See repository documentation'; pushed=(r.get('pushed_at') or '')[:10] or '—'; why=f"Recent activity in the last {DAYS} days; {r.get('stargazers_count',0):,} stars and {r.get('forks_count',0):,} forks."
    o.append(f"<tr><td class='rank'>{i}</td><td class='repo'><a target='_blank' href='{esc(r['html_url'])}'>{esc(r['full_name'])}</a></td><td>{esc(r.get('description') or 'No description')}</td><td>{features}</td><td>{esc(tech)}</td><td>{esc(r.get('language') or '—')}</td><td>{r.get('stargazers_count',0):,}</td><td>{r.get('forks_count',0):,}</td><td>{pushed}</td><td>{esc(why)}</td></tr>")
   o.append('</tbody></table></div>')
  o.append('</section>')
 o.append("<p class='footer'>Data source: official GitHub public API and repository pages. Check license, security, and maintenance before adoption.</p></main></body></html>");(OUT/'index.html').write_text(''.join(o),encoding='utf-8')
if __name__=='__main__':main()

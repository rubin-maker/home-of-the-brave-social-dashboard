#!/usr/bin/env python3
"""Build a self-contained interactive HOTB social dashboard from summary.json."""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "summary.json"), encoding="utf-8") as handle:
    source = json.load(handle)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def span(start, end):
    first_month, first_day = MONTHS[int(start[5:7]) - 1], int(start[8:10])
    last_month, last_day = MONTHS[int(end[5:7]) - 1], int(end[8:10])
    return f"{first_month} {first_day}–{last_day}" if first_month == last_month else f"{first_month} {first_day}–{last_month} {last_day}"


report = source["report_scope"]
scope_label = span(report["start"], report["end"])
period_label = span(source["period"]["start"], source["period"]["end"])
year = source["period"]["end"][:4]
week_labels = {name: f"{name.replace('Week ', 'W')} · {span(start, end)}" for name, start, end in source["weeks"]}


def category_week_key(post_date):
    return next((key for key, start, end in source["category_weeks"]
                 if start <= post_date <= end), "")


def slim(post):
    return {
        "p": post["platform"], "w": post["week"], "cw": category_week_key(post["date"]), "d": post["date"],
        "t": (post["title"] or "")[:220], "u": post["url"], "v": post["views"],
        "e": post["engagements"], "c": post["category"], "y": post["type"],
    }


data = {
    "totals": source["totals"],
    "subscribers": source["youtube_subscribers"],
    "scope": report,
    "weeks": source["weeks"],
    "categoryWeeks": source["category_weeks"],
    "coverage": source["platform_coverage_end"],
    "weekly": source["weekly"],
    "top5": {
        week: {platform: [slim(post) for post in posts] for platform, posts in by_platform.items()}
        for week, by_platform in source["top5"].items()
    },
    "categories": source["category_totals"],
    "categoryWeekly": source["category_weekly"],
    "definitions": source["metric_definitions"],
    "sources": source["source_notes"],
    "posts": [slim(post) for post in sorted(source["posts"], key=lambda post: -post["views"])],
    "wlbl": week_labels,
    "reportWeek": report["week"],
}

palette = {
    "YouTube": "#ff3155",
    "Instagram": "#c13584",
    "TikTok": "#00a6a6",
    "X": "#68707c",
}

html = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__BRAND__ — Social Performance, __SCOPE__, __YEAR__</title>
<style>
:root{color-scheme:light;--page:#f5f2eb;--surface:#fffdfa;--surface2:#f1ede5;--ink:#171512;--ink2:#5f5a52;
 --muted:#847e74;--grid:#e4ded4;--axis:#c8c0b4;--border:rgba(23,21,18,.11);--accent:#a51d2d;
 --good:#087443;--bad:#c33c3c;--shadow:0 12px 36px rgba(71,55,33,.06)}
@media(prefers-color-scheme:dark){:root{color-scheme:dark;--page:#12110f;--surface:#1b1916;--surface2:#25221e;--ink:#f8f3ea;
 --ink2:#cec6bb;--muted:#a3998d;--grid:#36312b;--axis:#4a433b;--border:rgba(255,255,255,.10);--accent:#ef6472;
 --good:#5bd09b;--bad:#ff8585;--shadow:none}}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
 background:var(--page);color:var(--ink);font-size:14px;line-height:1.5;padding:0 20px 80px}
.wrap{max-width:1180px;margin:0 auto}.mast{padding:44px 0 30px;border-bottom:1px solid var(--axis);display:flex;gap:24px;justify-content:space-between;align-items:end}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:11px;font-weight:750;color:var(--accent);margin-bottom:8px}
h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(31px,5vw,53px);line-height:1.02;letter-spacing:-.035em;margin:0;max-width:760px}
h2{font-size:18px;line-height:1.25;margin:0 0 5px}h3{font-size:14px;margin:0 0 9px}.sub{color:var(--ink2);margin-top:11px;max-width:850px}
.stamp{font-size:12px;color:var(--ink2);text-align:right;white-space:nowrap}.stamp b{display:block;color:var(--ink);font-size:15px}
section{margin-top:40px}.section-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:12px}.note{font-size:12px;color:var(--muted)}
.grid{display:grid;gap:14px}.hero{grid-template-columns:repeat(4,minmax(0,1fr))}.platform-grid{grid-template-columns:repeat(4,minmax(0,1fr));margin-top:14px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 20px;box-shadow:var(--shadow)}
.tile .label{font-size:11px;text-transform:uppercase;letter-spacing:.065em;color:var(--ink2);font-weight:700}.tile .value{font-size:30px;font-weight:720;letter-spacing:-.035em;margin-top:5px}.tile .value-unit{font-size:14px;font-weight:700;letter-spacing:0;color:var(--ink2);margin-left:2px}
.tile .detail{font-size:12px;color:var(--muted);margin-top:4px}.platform-card{position:relative;overflow:hidden}.platform-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--platform)}
.subscriber-card{display:grid;grid-template-columns:minmax(180px,1fr) minmax(0,2fr);align-items:center;gap:20px}.subscriber-card .value{font-variant-numeric:tabular-nums}.subscriber-card .detail{max-width:75ch}
.subscriber-weekly-card{margin-top:14px}.subscriber-weekly-head{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:12px}.subscriber-range{display:flex;align-items:center;gap:9px;flex-wrap:wrap;max-width:100%;font-size:12px;color:var(--ink2)}.subscriber-range .select{width:auto;max-width:100%;min-width:0}.subscriber-weekly-card .note{margin-bottom:10px}
.platform-name{font-weight:730}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:var(--platform)}
.spark-help{font-size:11px;color:var(--muted);margin-top:9px}.spark{display:block;width:100%;height:38px;margin-top:4px;overflow:visible}.spark-bar{cursor:pointer;outline:none}.spark-hit{fill:transparent;pointer-events:all}.spark-fill{pointer-events:none;transition:opacity .14s ease,stroke-width .14s ease}.spark-fill.partial{stroke:var(--muted);stroke-width:1;stroke-dasharray:2 2}.spark-bar:hover .spark-fill,.spark-bar:focus .spark-fill,.spark-bar.selected .spark-fill{opacity:1;stroke:var(--ink);stroke-width:1.4}.spark-range{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:2px;font-size:9px;color:var(--muted);font-variant-numeric:tabular-nums}.spark-range b{color:var(--accent);font-weight:750}.spark-readout{min-height:53px;margin-top:8px;padding-top:8px;border-top:1px solid var(--grid);font-size:11px;color:var(--ink2);font-variant-numeric:tabular-nums}.spark-readout strong{display:block;color:var(--ink);font-size:11px;margin-bottom:2px}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}
th{color:var(--ink2);font-size:11px;text-transform:uppercase;letter-spacing:.045em;font-weight:700;text-align:left;padding:9px 10px;border-bottom:1px solid var(--axis);white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--grid);vertical-align:top}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}tr.total td{font-weight:750;border-top:1px solid var(--axis)}.delta{display:block;font-size:10px;font-weight:700;margin-top:1px}
.up{color:var(--good)}.down{color:var(--bad)}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.tabs{display:flex;gap:7px;overflow-x:auto;padding-bottom:7px}.tabs button,.select,input{font:inherit;border:1px solid var(--axis);border-radius:9px;background:var(--surface);color:var(--ink)}
.tabs button{padding:7px 12px;cursor:pointer;white-space:nowrap}.tabs button.on{background:var(--ink);border-color:var(--ink);color:var(--page)}
.category-charts{display:grid;gap:14px}.chart-card{overflow:hidden}.chart-head{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:8px}.chart-meta{display:flex;align-items:center;justify-content:flex-end;gap:9px;flex-wrap:wrap}.chart-reset{font:inherit;font-size:11px;border:1px solid var(--axis);border-radius:999px;background:var(--surface2);color:var(--ink);padding:4px 8px;cursor:pointer}
.chart-wrap{overflow-x:auto;overscroll-behavior-inline:contain}.line-chart{display:block;width:auto;min-width:100%;height:auto}.category-legend{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.category-key{font:inherit;font-size:11px;border:1px solid var(--grid);border-radius:999px;background:var(--surface2);color:var(--ink);padding:4px 8px;cursor:pointer}.category-key.total{font-weight:750;border-color:var(--category)}
.category-key.off{opacity:.42}.category-key .swatch{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:var(--category)}
.chart-point{cursor:pointer;outline:none}.point-hit{fill:transparent;pointer-events:all}.point-marker{pointer-events:none}.point-focus-ring{fill:none;stroke:transparent;pointer-events:none}.chart-point:hover .point-focus-ring,.chart-point:focus .point-focus-ring,.chart-point.selected .point-focus-ring{stroke:var(--accent);stroke-width:2.5}
.point-help{margin-top:12px;padding-top:11px;border-top:1px solid var(--grid);font-size:12px;color:var(--muted)}.point-detail{margin-top:12px;padding-top:13px;border-top:1px solid var(--grid)}
.point-detail-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.point-detail-kicker{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:750}.point-detail-title{display:block;margin-top:2px;font-size:14px}.point-actions{text-align:right}.point-total{font-size:18px;font-weight:750;white-space:nowrap}.point-detail-note{font-size:11px;color:var(--muted);margin:5px 0 10px}.point-close{font:inherit;font-size:11px;border:0;background:transparent;color:var(--accent);padding:0;cursor:pointer}
.point-posts{display:grid;gap:7px}.point-post{display:grid;grid-template-columns:25px minmax(0,1fr) auto;align-items:start;gap:9px;padding:9px 10px;border-radius:9px;background:var(--surface2)}.point-rank{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;background:var(--surface);color:var(--ink2);font-size:10px;font-weight:750}.point-post-title{font-weight:650;line-height:1.3}.point-post-meta,.point-post-stats{font-size:10px;color:var(--muted);margin-top:3px}.point-post-stats{text-align:right;white-space:nowrap}.point-post-open{display:block;margin-top:4px;font-size:11px;font-weight:700}
.controls{display:grid;grid-template-columns:minmax(210px,1fr) 180px;gap:10px;margin-bottom:10px}.select,input{padding:8px 10px;width:100%}
.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.definition{display:grid;grid-template-columns:110px 1fr;gap:4px 12px;font-size:12px}.definition b{color:var(--ink2)}
.sources{margin:0;padding-left:18px}.sources li{margin:5px 0;color:var(--ink2)}
.footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--axis);color:var(--muted);font-size:11px}
@media(max-width:900px){.hero,.platform-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mast{display:block}.stamp{text-align:left;margin-top:18px}}
@media(max-width:620px){body{padding-left:13px;padding-right:13px}.hero,.platform-grid,.metric-grid,.subscriber-card{grid-template-columns:1fr}.controls{grid-template-columns:1fr}.card{padding:15px}.mast{padding-top:28px}.chart-head{align-items:flex-start;flex-direction:column;gap:8px}.chart-meta{justify-content:space-between;width:100%}.point-detail-head{display:block}.point-total{margin-top:5px}.point-post{grid-template-columns:25px minmax(0,1fr)}.point-post-stats{grid-column:2;text-align:left;white-space:normal;margin-top:0}}
@media print{body{padding:0;background:#fff}.card{box-shadow:none;break-inside:avoid}.tabs,.controls{display:none}.wrap{max-width:none}}
</style></head><body><div class="wrap">
<header class="mast"><div><div class="eyebrow">2026 social intelligence</div><h1>__BRAND__ performance dashboard</h1>
<div class="sub">A unified view of YouTube, Instagram, TikTok, and X. Headline numbers cover the latest fully complete Monday–Sunday week; the explorer retains the full year-to-date file.</div></div>
<div class="stamp"><span>Reporting week</span><b>__SCOPE__, __YEAR__</b><span>Full file: __PERIOD__</span></div></header>

<section><div class="grid hero" id="hero"></div><div class="grid platform-grid" id="platforms"></div></section>

<section aria-labelledby="subscriber-heading"><div class="section-head"><h2 id="subscriber-heading">YouTube subscriber metric</h2></div>
<div class="card tile subscriber-card" id="subscribers"></div>
<div class="card subscriber-weekly-card" id="subscriber-weekly"><div class="subscriber-weekly-head"><h3>Subscribers by publish week</h3>
<label class="subscriber-range" for="subscriberRange">Publish weeks<select class="select" id="subscriberRange"><option value="recent">Latest 8 complete weeks</option><option value="all">All available weeks</option></select></label></div>
<div class="note">Source-reported Subscribers attributed to videos published that week—not subscribers gained during the week or the channel’s week-end subscriber balance.</div>
<div class="scroll" id="subscriberWeekly" aria-live="polite"></div></div></section>

<section><div class="section-head"><div><h2>Eight-week platform trend</h2><div class="note">Current cumulative post metrics, grouped by publish week.</div></div></div>
<div class="card scroll" id="weekly"></div>
<div class="note" style="margin-top:7px">This table keeps the eight complete comparison weeks through __SCOPE__. The mini bars above use each platform's latest eight available publish weeks and may include a partial final week. X uses impressions; the other platforms use views.</div></section>

<section><div class="section-head"><div><h2>Weekly category trends</h2><div class="note">Every available 2026 publish week for Instagram, YouTube, and TikTok; dates mark the start of each week.</div></div><div class="tabs" id="categoryMetricTabs"></div></div>
<div class="category-charts" id="categoryTrendCharts"></div>
<div class="note" style="margin-top:7px">Each chart uses its own scale and stops at that platform's latest included publish date. The thicker dashed All categories line is the weekly platform total. Select any chart point—including a spike—to see the top videos or posts published that week. Scroll horizontally on smaller screens.</div></section>

<section><div class="section-head"><div><h2>Year-to-date category performance</h2><div class="note">Categories follow the reviewed labels in each source workbook.</div></div></div>
<div class="card"><div class="tabs" id="categoryTabs"></div><div id="categories"></div></div></section>

<section><div class="section-head"><div><h2>Top five posts by platform</h2><div class="note">Select one of the eight complete context weeks.</div></div></div>
<div class="card"><div class="tabs" id="weekTabs"></div><div id="tops"></div></div></section>

<section><div class="section-head"><div><h2>All-posts explorer</h2><div class="note">Searches the full year-to-date dataset; rows are ranked by views/impressions.</div></div></div>
<div class="card"><div class="controls"><input id="search" placeholder="Search post text or category…"><select class="select" id="platformFilter"></select></div>
<div class="scroll" id="allPosts"></div><div class="note" style="margin-top:7px">Showing up to 500 matching rows. The complete dataset is in all_posts.csv.</div></div></section>

<section><div class="section-head"><div><h2>Metric definitions and coverage</h2><div class="note">Cross-platform totals combine similar, but not identical, platform measures.</div></div></div>
<div class="grid metric-grid" id="definitions"></div><div class="card" style="margin-top:14px"><h3>Source coverage</h3><ul class="sources" id="sources"></ul></div></section>

<div class="footer">Built from the four reviewed 2026 HOTB workbooks. Self-contained and usable offline; outbound post links require internet access.</div>
</div><script>
const D=__DATA__,PC=__PC__,PLATS=Object.keys(D.totals),TREND_PLATS=["Instagram","YouTube","TikTok"],ALL_CATEGORIES="All categories";
const CAT_COLORS=["#a51d2d","#2166ac","#2a9d8f","#d97706","#7c3aed","#0f766e","#c2410c","#be185d","#4d7c0f","#4338ca","#6b7280","#0891b2","#9333ea","#15803d"];
const ALL_CATS=[...new Set(TREND_PLATS.flatMap(p=>Object.keys(D.categoryWeekly[p]||{})))].sort();
const CAT_COLOR=Object.fromEntries(ALL_CATS.map((c,i)=>[c,CAT_COLORS[i%CAT_COLORS.length]]));
const full=n=>(n||0).toLocaleString();
const fmt=n=>n>=1e9?(n/1e9).toFixed(1)+"B":n>=1e6?(n/1e6).toFixed(1)+"M":n>=1e4?Math.round(n/1e3)+"K":full(n);
const esc=s=>(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
const chartDate=s=>new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",timeZone:"UTC"}).format(new Date(s+"T00:00:00Z"));
const shiftDate=(s,days)=>{const value=new Date(s+"T00:00:00Z");value.setUTCDate(value.getUTCDate()+days);return value.toISOString().slice(0,10)};
const coveredDays=(start,end)=>Math.round((new Date(end+"T00:00:00Z")-new Date(start+"T00:00:00Z"))/86400000)+1;
const rate=(e,v)=>v?(100*e/v).toFixed(2)+"%":"—";
const delta=(a,b)=>!a?"—":`${b>=a?"+":""}${Math.round(100*(b-a)/a)}%`;
const reportWeekKey=D.scope.start;
const platformSparkWeeks=Object.fromEntries(PLATS.map(platform=>{const cutoff=D.coverage[platform],weeks=D.categoryWeeks.filter(week=>week[1]<=cutoff).slice(-8).map(([key,start])=>{const scheduledEnd=shiftDate(start,6),end=scheduledEnd<cutoff?scheduledEnd:cutoff,posts=D.posts.filter(post=>post.p===platform&&post.cw===key&&post.d>=start&&post.d<=end),views=posts.reduce((sum,post)=>sum+post.v,0),eng=posts.reduce((sum,post)=>sum+post.e,0);return {key,start,end,complete:end===scheduledEnd,views,eng,posts:posts.length,er:views?(100*eng/views).toFixed(2):null}});if(weeks.length!==8||!weeks.some(week=>week.key===reportWeekKey))throw new Error(`${platform} mini chart cannot show eight latest weeks with the shared reporting week`);return [platform,weeks]}));
const sparkWeekMap=Object.fromEntries(PLATS.map(platform=>[platform,Object.fromEntries(platformSparkWeeks[platform].map(week=>[week.key,week]))]));
const sparkSelection=Object.fromEntries(PLATS.map(platform=>[platform,reportWeekKey]));
const sparkSummary=(platform,week)=>{const row=sparkWeekMap[platform][week],unit=D.definitions[platform].metric_label;return {value:`${fmt(row.views)} <span class="value-unit">${esc(unit)}</span>`,detail:`${fmt(row.eng)} engagements · ${row.posts} posts · ${row.er??"—"}% rate`}};
const sparkDetail=(platform,week)=>{const row=sparkWeekMap[platform][week],unit=D.definitions[platform].metric_label,coverage=row.complete?(row.key===reportWeekKey?"Latest complete comparison week":"Complete publish week"):`Partial publish week through ${chartDate(row.end)} · ${coveredDays(row.start,row.end)} of 7 days`;return `<strong>Selected week · ${esc(chartDate(row.start))}–${esc(chartDate(row.end))}, ${row.start.slice(0,4)}</strong><span>${full(row.views)} ${unit} · ${full(row.eng)} engagements · ${full(row.posts)} posts · ${row.er??"—"}% rate · ${coverage}</span>`};
const spark=(platform,color)=>{const unit=D.definitions[platform].metric_label,selected=sparkSelection[platform],weeks=platformSparkWeeks[platform],max=Math.max(...weeks.map(week=>week.views),1),first=weeks[0],last=weeks[weeks.length-1];return `<svg class="spark" viewBox="0 0 160 38" preserveAspectRatio="none" role="group" aria-label="${esc(platform)} latest ${weeks.length} available publish-week ${esc(unit)} trend. Select a bar for exact weekly stats; the final bar may be partial.">${weeks.map((week,i)=>{const value=week.views,h=Math.max(1,32*value/max),isSelected=week.key===selected,coverage=week.complete?"complete publish week":`partial publish week through ${chartDate(week.end)}, ${coveredDays(week.start,week.end)} of 7 days`,label=`${platform}, ${chartDate(week.start)}–${chartDate(week.end)}, ${week.start.slice(0,4)}: ${full(value)} ${unit}, ${full(week.eng)} engagements, ${full(week.posts)} posts, ${week.er??"—"}% engagement rate, ${coverage}`;return `<g class="spark-bar ${isSelected?"selected":""}" role="button" tabindex="0" focusable="true" aria-pressed="${isSelected}" aria-label="${esc(label)}" data-spark-platform="${esc(platform)}" data-spark-week="${esc(week.key)}"><rect class="spark-hit" x="${i*20}" y="0" width="20" height="38"/><rect class="spark-fill${week.complete?"":" partial"}" x="${i*20+2}" y="${36-h}" width="14" height="${h}" rx="2" fill="${color}" opacity=".48"/><title>${esc(label)}</title></g>`}).join("")}</svg><div class="spark-range" aria-hidden="true"><span>${esc(chartDate(first.start))}</span><span>${esc(chartDate(last.start))}–${esc(chartDate(last.end))}${last.complete?"":` · <b>partial ${coveredDays(last.start,last.end)}/7 days</b>`}</span></div>`};

let categoryMetric="views";
const hiddenCategories=Object.fromEntries(TREND_PLATS.map(p=>[p,new Set()]));
const categoryScroll=Object.fromEntries(TREND_PLATS.map(p=>[p,0]));
const categorySelection=Object.fromEntries(TREND_PLATS.map(p=>[p,null]));
const categoryFocus=Object.fromEntries(TREND_PLATS.map(p=>[p,{category:ALL_CATEGORIES,week:D.categoryWeeks[0][0]}]));
const safeUrl=url=>/^https?:\/\/[^\s]+$/i.test(url||"")?url:"";
const pointPostCount=(platform,category,weekKey)=>category===ALL_CATEGORIES
 ?Object.values(D.categoryWeekly[platform]||{}).reduce((sum,byWeek)=>sum+(byWeek[weekKey]?.posts||0),0)
 :(D.categoryWeekly[platform]?.[category]?.[weekKey]?.posts||0);
const niceScale=value=>{if(value<=0)return {max:1,step:1};const raw=value/4,power=10**Math.floor(Math.log10(raw)),fraction=raw/power,step=(fraction<1.5?1:fraction<3?2:fraction<7?5:10)*power;return {max:Math.ceil(value/step)*step,step}};
function categoryPointPanel(platform,weeks,series){
 const selection=categorySelection[platform],panelId=`point-detail-${platform.toLowerCase()}`;
 const selectedSeries=selection&&series.find(item=>item.category===selection.category),weekIndex=selection?weeks.findIndex(week=>week[0]===selection.week):-1;
 if(!selectedSeries||weekIndex<0||hiddenCategories[platform].has(selection.category))return `<div class="point-help" id="${panelId}" aria-live="polite">Select any point—including a spike—to see the top videos or posts published in that week. Keyboard: use arrow keys to move, then Enter or Space to select.</div>`;
 const week=weeks[weekIndex],cutoff=D.coverage[platform],end=week[2]<cutoff?week[2]:cutoff,total=selectedSeries.values[weekIndex],metricLabel={views:"views",eng:"engagements",posts:"posts"}[categoryMetric];
 const posts=D.posts.filter(post=>post.p===platform&&post.cw===week[0]&&(selection.category===ALL_CATEGORIES||post.c===selection.category));
 const rankField=categoryMetric==="eng"?"e":"v",rankLabel=categoryMetric==="eng"?"engagements":"views";
 const ranked=[...posts].sort((a,b)=>(b[rankField]-a[rankField])||(b.v-a.v)||(b.e-a.e)||a.d.localeCompare(b.d)||a.t.localeCompare(b.t)||a.u.localeCompare(b.u)).slice(0,3);
 const partial=(Date.parse(end+"T00:00:00Z")-Date.parse(week[1]+"T00:00:00Z"))/86400000<6;
 const detailNote=categoryMetric==="posts"
  ?`${full(posts.length)} ${posts.length===1?"post was":"posts were"} published in this weekly point; the highest-view posts are shown below.`
  :`Top contributors ranked by ${rankLabel}. These are current cumulative metrics grouped by publish week, so this identifies contributors—not when views or engagements were earned.`;
 const postCards=ranked.map((post,i)=>{const url=safeUrl(post.u),title=(post.t||"").trim()||"(no title or text)",share=total?Math.round(1000*post[rankField]/total)/10:0;
  const primary=categoryMetric==="eng"?`${full(post.e)} engagements`:`${full(post.v)} ${esc(D.definitions[platform].metric_label)}`;
  const secondary=categoryMetric==="eng"?`${full(post.v)} ${esc(D.definitions[platform].metric_label)}`:`${full(post.e)} engagements`;
  const contribution=categoryMetric==="posts"?secondary:`${secondary} · ${share}% of weekly ${rankLabel}`;
  return `<article class="point-post"><div class="point-rank">${i+1}</div><div><div class="point-post-title">${url?`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(title)}</a>`:esc(title)}</div><div class="point-post-meta">${esc(chartDate(post.d))}, ${post.d.slice(0,4)} · ${esc(post.c)} · ${esc(post.y)}</div>${url?`<a class="point-post-open" href="${esc(url)}" target="_blank" rel="noopener">Open video / post ↗</a>`:""}</div><div class="point-post-stats"><strong>${primary}</strong><br>${contribution}</div></article>`}).join("");
 return `<div class="point-detail" id="${panelId}" role="region" aria-label="${esc(platform)} selected chart point details" aria-live="polite"><div class="point-detail-head"><div><div class="point-detail-kicker">Posts behind this point${partial?" · Partial week":""}</div><strong class="point-detail-title">${esc(selection.category)} · ${esc(chartDate(week[1]))}–${esc(chartDate(end))}, ${week[1].slice(0,4)}</strong></div><div class="point-actions"><div class="point-total">${full(total)} ${metricLabel}</div><button type="button" class="point-close" data-clear-point="${esc(platform)}">Close details</button></div></div><div class="point-detail-note">${detailNote} Post dates below show the exact publish day.</div>${postCards?`<div class="point-posts">${postCards}</div>`:`<div class="note">No posts were published for this category and week.</div>`}</div>`;
}
function categoryChart(platform){
 const metricLabels={views:"Views",eng:"Engagements",posts:"Posts"},cutoff=D.coverage[platform];
 const weeks=D.categoryWeeks.filter(week=>week[1]<=cutoff),weekKeys=weeks.map(week=>week[0]);
 const weekSpan=week=>`${chartDate(week[1])}–${chartDate(week[2]<cutoff?week[2]:cutoff)}`;
 const categorySeries=Object.entries(D.categoryWeekly[platform]||{}).map(([category,byWeek])=>({category,isTotal:false,values:weekKeys.map(key=>byWeek[key]?.[categoryMetric]||0)}));
 const series=[{category:ALL_CATEGORIES,isTotal:true,values:weekKeys.map((_,i)=>categorySeries.reduce((sum,item)=>sum+item.values[i],0))},...categorySeries];
 const visible=series.filter(s=>!hiddenCategories[platform].has(s.category)),scale=niceScale(Math.max(1,...visible.flatMap(s=>s.values))),max=scale.max,tickCount=Math.round(max/scale.step);
 let focusState=categoryFocus[platform];
 if(!visible.some(item=>item.category===focusState?.category))focusState={category:visible[0]?.category,week:focusState?.week||weekKeys[0]};
 if(!weekKeys.includes(focusState?.week))focusState={category:focusState?.category,week:weekKeys[0]};
 categoryFocus[platform]=visible.length?focusState:null;
 const W=Math.max(920,weeks.length*27+94),H=350,L=72,R=22,T=20,B=78,innerW=W-L-R,innerH=H-T-B;
 const x=i=>L+(weeks.length===1?innerW/2:i*innerW/(weeks.length-1)),y=v=>T+innerH-(v/max)*innerH;
 const grid=Array.from({length:tickCount+1},(_,i)=>i/tickCount).map(r=>{const yy=y(max*r);return `<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" stroke="var(--grid)"/><text x="${L-10}" y="${yy+4}" text-anchor="end" fill="var(--muted)" font-size="11">${fmt(max*r)}</text>`}).join("");
 const xLabels=weeks.map((week,i)=>`<text transform="translate(${x(i)} ${H-B+18}) rotate(-55)" text-anchor="end" fill="var(--muted)" font-size="10">${esc(chartDate(week[1]))}</text>`).join("");
 const drawSeries=[...visible].sort((a,b)=>Number(a.isTotal)-Number(b.isTotal));
 const lines=drawSeries.map(s=>{const color=s.isTotal?"var(--ink)":CAT_COLOR[s.category],points=s.values.map((v,i)=>`${x(i)},${y(v)}`).join(" "),width=s.isTotal?3.5:2.25,dashes=s.isTotal?' stroke-dasharray="8 4"':"",seriesIndex=series.indexOf(s);const marks=s.values.map((v,i)=>{const selected=categorySelection[platform]?.category===s.category&&categorySelection[platform]?.week===weekKeys[i],focused=focusState?.category===s.category&&focusState?.week===weekKeys[i],postCount=pointPostCount(platform,s.category,weekKeys[i]);const valueText=categoryMetric==="posts"?`${full(v)} posts published`:`${full(v)} ${metricLabels[categoryMetric].toLowerCase()} from ${full(postCount)} ${postCount===1?"post":"posts"}`;const label=`${platform}, ${s.category}, ${weekSpan(weeks[i])}, ${weeks[i][1].slice(0,4)}: ${valueText}. Select to show top contributors.`;const marker=s.isTotal?`<rect class="point-marker" x="${x(i)-4}" y="${y(v)-4}" width="8" height="8" rx="1" fill="var(--surface)" stroke="${color}" stroke-width="2"/>`:`<circle class="point-marker" cx="${x(i)}" cy="${y(v)}" r="3" fill="${color}" stroke="var(--surface)" stroke-width="1.5"/>`;return `<g class="chart-point${selected?" selected":""}" role="button" tabindex="${focused?0:-1}" focusable="true" aria-pressed="${selected}" aria-label="${esc(label)}" data-point-platform="${esc(platform)}" data-point-category="${esc(s.category)}" data-point-week="${esc(weekKeys[i])}" data-week-index="${i}" data-series-index="${seriesIndex}" data-point-x="${x(i)}"><title>${esc(label)}</title><circle class="point-hit" cx="${x(i)}" cy="${y(v)}" r="12"/><circle class="point-focus-ring" cx="${x(i)}" cy="${y(v)}" r="8"/>${marker}</g>`}).join("");return `<g data-series="${esc(s.category)}"><polyline points="${points}" fill="none" stroke="${color}" stroke-width="${width}"${dashes} stroke-linejoin="round" stroke-linecap="round"/><title>${esc(s.category)} · ${metricLabels[categoryMetric]}</title>${marks}</g>`}).join("");
 const selectedWeekIndex=categorySelection[platform]&&visible.some(item=>item.category===categorySelection[platform].category)?weekKeys.indexOf(categorySelection[platform].week):-1;
 const selectionGuide=selectedWeekIndex>=0?`<line x1="${x(selectedWeekIndex)}" y1="${T}" x2="${x(selectedWeekIndex)}" y2="${H-B}" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="2 4" opacity=".72"/>`:"";
 const emptyState=visible.length?"":`<text x="${L+innerW/2}" y="${T+innerH/2}" text-anchor="middle" fill="var(--muted)" font-size="14">No categories selected — choose Show all</text>`;
 const legend=series.map(s=>{const color=s.isTotal?"var(--ink)":CAT_COLOR[s.category];return `<button class="category-key ${s.isTotal?"total ":""}${hiddenCategories[platform].has(s.category)?"off":""}" data-platform="${esc(platform)}" data-category="${esc(s.category)}" aria-pressed="${!hiddenCategories[platform].has(s.category)}" style="--category:${color}"><span class="swatch"></span>${esc(s.category)}</button>`}).join("");
 const showAll=hiddenCategories[platform].size?`<button type="button" class="chart-reset" data-reset-platform="${esc(platform)}">Show all</button>`:"";
 const deselectAll=visible.length?`<button type="button" class="chart-reset" data-deselect-platform="${esc(platform)}">Deselect all</button>`:"";
 return `<div class="card chart-card"><div class="chart-head"><h3><span class="dot" style="--platform:${PC[platform]}"></span>${platform}</h3><div class="chart-meta"><span class="note">${metricLabels[categoryMetric]} per week · through ${esc(chartDate(cutoff))}</span>${showAll}${deselectAll}</div></div><div class="chart-wrap" data-scroll-platform="${esc(platform)}"><svg class="line-chart" width="${W}" viewBox="0 0 ${W} ${H}" role="group" aria-label="${platform} all available 2026 weekly ${metricLabels[categoryMetric].toLowerCase()} by category, including an All categories platform-total line. Select a point to show its top posts.">${grid}<line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="var(--axis)"/><line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="var(--axis)"/>${xLabels}${selectionGuide}${lines}${emptyState}</svg></div><div class="category-legend">${legend}</div>${categoryPointPanel(platform,weeks,series)}</div>`;
}
function restoreCategoryFocus(target){
 if(!target)return;
 let element=null;
 if(target.kind==="metric")element=[...document.querySelectorAll("#categoryMetricTabs button")].find(item=>item.dataset.metric===target.metric);
 if(target.kind==="legend")element=[...document.querySelectorAll(".category-key")].find(item=>item.dataset.platform===target.platform&&item.dataset.category===target.category);
 if(target.kind==="point")element=[...document.querySelectorAll(".chart-point")].find(item=>item.dataset.pointPlatform===target.platform&&item.dataset.pointCategory===target.category&&item.dataset.pointWeek===target.week);
 element?.focus({preventScroll:true});
}
function moveCategoryPointFocus(point,key){
 const card=point.closest(".chart-card"),points=[...card.querySelectorAll(".chart-point")],weekIndex=Number(point.dataset.weekIndex),seriesIndex=Number(point.dataset.seriesIndex),seriesIndexes=[...new Set(points.map(item=>Number(item.dataset.seriesIndex)))].sort((a,b)=>a-b);
 let nextWeek=weekIndex,nextSeries=seriesIndex;
 if(key==="ArrowLeft")nextWeek=Math.max(0,weekIndex-1);
 if(key==="ArrowRight")nextWeek=Math.min(D.categoryWeeks.length-1,weekIndex+1);
 if(key==="Home")nextWeek=0;
 if(key==="End")nextWeek=Math.max(...points.filter(item=>Number(item.dataset.seriesIndex)===seriesIndex).map(item=>Number(item.dataset.weekIndex)));
 if(key==="ArrowUp")nextSeries=seriesIndexes[Math.max(0,seriesIndexes.indexOf(seriesIndex)-1)];
 if(key==="ArrowDown")nextSeries=seriesIndexes[Math.min(seriesIndexes.length-1,seriesIndexes.indexOf(seriesIndex)+1)];
 const target=points.find(item=>Number(item.dataset.weekIndex)===nextWeek&&Number(item.dataset.seriesIndex)===nextSeries);
 if(!target)return;
 point.setAttribute("tabindex","-1");target.setAttribute("tabindex","0");
 categoryFocus[target.dataset.pointPlatform]={category:target.dataset.pointCategory,week:target.dataset.pointWeek};
 target.focus({preventScroll:true});
 const wrap=card.querySelector(".chart-wrap"),x=Number(target.dataset.pointX);wrap.scrollTo({left:Math.max(0,x-wrap.clientWidth/2),behavior:"smooth"});
}
function selectCategoryPoint(point){
 const platform=point.dataset.pointPlatform,next={category:point.dataset.pointCategory,week:point.dataset.pointWeek},current=categorySelection[platform];
 categoryFocus[platform]=next;categorySelection[platform]=current?.category===next.category&&current?.week===next.week?null:next;
 renderCategoryTrends({kind:"point",platform,...next});
}
function renderCategoryTrends(focusTarget){
 const metricLabels={views:"Views",eng:"Engagements",posts:"Posts"};
 document.querySelectorAll("#categoryTrendCharts .chart-wrap").forEach(wrap=>{categoryScroll[wrap.dataset.scrollPlatform]=wrap.scrollLeft});
 document.getElementById("categoryMetricTabs").innerHTML=Object.entries(metricLabels).map(([key,label])=>`<button data-metric="${key}" class="${categoryMetric===key?"on":""}">${label}</button>`).join("");
 document.getElementById("categoryTrendCharts").innerHTML=TREND_PLATS.map(categoryChart).join("");
 document.querySelectorAll("#categoryTrendCharts .chart-wrap").forEach(wrap=>{wrap.scrollLeft=categoryScroll[wrap.dataset.scrollPlatform]||0});
 document.querySelectorAll("#categoryMetricTabs button").forEach(button=>button.addEventListener("click",()=>{categoryMetric=button.dataset.metric;renderCategoryTrends({kind:"metric",metric:categoryMetric})}));
 document.querySelectorAll(".category-key").forEach(button=>button.addEventListener("click",()=>{const platform=button.dataset.platform,hidden=hiddenCategories[platform],category=button.dataset.category,wasHidden=hidden.has(category);wasHidden?hidden.delete(category):hidden.add(category);if(!wasHidden&&categorySelection[platform]?.category===category)categorySelection[platform]=null;renderCategoryTrends({kind:"legend",platform,category})}));
 document.querySelectorAll("[data-reset-platform]").forEach(button=>button.addEventListener("click",()=>{const platform=button.dataset.resetPlatform;hiddenCategories[platform].clear();renderCategoryTrends({kind:"legend",platform,category:ALL_CATEGORIES})}));
 document.querySelectorAll("[data-deselect-platform]").forEach(button=>button.addEventListener("click",()=>{const platform=button.dataset.deselectPlatform,hidden=hiddenCategories[platform];hidden.add(ALL_CATEGORIES);Object.keys(D.categoryWeekly[platform]||{}).forEach(category=>hidden.add(category));categorySelection[platform]=null;renderCategoryTrends({kind:"legend",platform,category:ALL_CATEGORIES})}));
 document.querySelectorAll("[data-clear-point]").forEach(button=>button.addEventListener("click",()=>{const platform=button.dataset.clearPoint,current=categorySelection[platform];categorySelection[platform]=null;renderCategoryTrends(current?{kind:"point",platform,...current}:null)}));
 document.querySelectorAll(".chart-point").forEach(point=>{point.addEventListener("focus",()=>{categoryFocus[point.dataset.pointPlatform]={category:point.dataset.pointCategory,week:point.dataset.pointWeek}});point.addEventListener("pointerdown",event=>{point._pointStart={x:event.clientX,y:event.clientY};point._pointMoved=false});point.addEventListener("pointermove",event=>{if(point._pointStart&&Math.hypot(event.clientX-point._pointStart.x,event.clientY-point._pointStart.y)>8)point._pointMoved=true});point.addEventListener("pointercancel",()=>{point._pointMoved=true});point.addEventListener("click",()=>{if(point._pointMoved){point._pointMoved=false;return}selectCategoryPoint(point)});point.addEventListener("keydown",event=>{if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(event.key)){event.preventDefault();moveCategoryPointFocus(point,event.key)}else if(event.key==="Enter"||event.key===" "){event.preventDefault();selectCategoryPoint(point)}})});
 restoreCategoryFocus(focusTarget);
}

const RS=D.scope,blend=rate(RS.eng,RS.views);
const SUB=D.subscribers;
const subCutoff=new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"}).format(new Date(SUB.as_of+"T00:00:00Z"));
document.getElementById("subscribers").innerHTML=`<div><div class="label">2026 exported videos</div><div class="value">${full(SUB.gained)}</div><div class="detail">Cumulative through ${esc(subCutoff)}</div></div>
<div><div>${full(SUB.long_form)} from long-form · ${full(SUB.shorts)} from Shorts</div><div class="detail">Source-reported Subscribers across ${full(SUB.video_count)} included videos—not the current channel subscriber total or net growth.</div><div class="detail">Source: ${esc(SUB.source)}</div></div>`;
const subscriberDate=s=>new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",timeZone:"UTC"}).format(new Date(s+"T00:00:00Z"));
function renderSubscriberWeeks(){
 const all=document.getElementById("subscriberRange").value==="all";
 const rows=all?SUB.weekly:SUB.weekly.filter(row=>row.complete).slice(-8);
 const total=key=>rows.reduce((sum,row)=>sum+row[key],0);
 document.getElementById("subscriberWeekly").innerHTML=`<table><caption style="text-align:left;color:var(--ink2);font-size:12px;margin-bottom:8px">${all?"All available publish weeks":"Latest eight complete publish weeks"} · ${full(total("gained"))} source-reported subscribers from ${full(total("video_count"))} included videos</caption><thead><tr><th scope="col">Publish week</th><th scope="col" class="n">Long-form</th><th scope="col" class="n">Shorts</th><th scope="col" class="n">Total</th><th scope="col" class="n">Videos</th><th scope="col">Coverage</th></tr></thead><tbody>`+
 rows.map(row=>`<tr><th scope="row">${esc(subscriberDate(row.start))}–${esc(subscriberDate(row.end))}, ${row.end.slice(0,4)}</th><td class="n">${full(row.long_form)}</td><td class="n">${full(row.shorts)}</td><td class="n"><strong>${full(row.gained)}</strong></td><td class="n">${full(row.video_count)}</td><td>${!row.complete?"Partial week — cutoff "+esc(subCutoff):row.video_count?"Complete publish week":"No exported videos"}</td></tr>`).join("")+
 `<tr class="total"><th scope="row">Shown weeks</th><td class="n">${full(total("long_form"))}</td><td class="n">${full(total("shorts"))}</td><td class="n">${full(total("gained"))}</td><td class="n">${full(total("video_count"))}</td><td></td></tr></tbody></table>`;
}
document.getElementById("subscriberRange").addEventListener("change",renderSubscriberWeeks);
renderSubscriberWeeks();
document.getElementById("hero").innerHTML=[
 ["Views / impressions",fmt(RS.views),D.wlbl[D.reportWeek]],
 ["Engagements",fmt(RS.eng),blend+" blended interaction rate"],
 ["Posts published",full(RS.posts),PLATS.length+" platforms"],
 ["Avg. per post",fmt(Math.round(RS.views/Math.max(RS.posts,1))),"views / impressions"],
].map(x=>`<div class="card tile"><div class="label">${x[0]}</div><div class="value">${x[1]}</div><div class="detail">${x[2]}</div></div>`).join("");

document.getElementById("platforms").innerHTML=PLATS.slice().sort((a,b)=>RS.totals[b].views-RS.totals[a].views).map(p=>{
 const unit=D.definitions[p].metric_label,selected=sparkSummary(p,sparkSelection[p]);
 return `<div class="card tile platform-card" style="--platform:${PC[p]}"><div class="label"><span class="dot"></span><span class="platform-name">${p}</span></div>
 <div class="value">${selected.value}</div><div class="detail platform-week-detail">${selected.detail}</div>
 <div class="spark-help">Latest 8 available publish weeks. Select a bar for exact stats; the outlined final bar is partial.</div>${spark(p,PC[p])}<div class="spark-readout" aria-live="polite">${sparkDetail(p,sparkSelection[p])}</div><div class="detail">YTD: ${fmt(D.totals[p].views)} ${unit} across ${full(D.totals[p].posts)} posts</div></div>`}).join("");

function selectSparkBar(bar){const platform=bar.dataset.sparkPlatform,week=bar.dataset.sparkWeek,card=bar.closest(".platform-card"),summary=sparkSummary(platform,week);sparkSelection[platform]=week;card.querySelectorAll(".spark-bar").forEach(candidate=>{const selected=candidate.dataset.sparkWeek===week;candidate.classList.toggle("selected",selected);candidate.setAttribute("aria-pressed",String(selected))});card.querySelector(".value").innerHTML=summary.value;card.querySelector(".platform-week-detail").textContent=summary.detail;card.querySelector(".spark-readout").innerHTML=sparkDetail(platform,week)}
document.querySelectorAll(".spark-bar").forEach(bar=>{bar.addEventListener("click",()=>selectSparkBar(bar));bar.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectSparkBar(bar)}})});

(function(){let h=`<table><thead><tr><th>Platform</th>${D.weeks.map(w=>`<th class="n">${esc(D.wlbl[w[0]])}</th>`).join("")}</tr></thead><tbody>`;
 for(const p of PLATS){const vals=D.weeks.map(w=>D.weekly[w[0]][p].views);h+=`<tr><td><span class="dot" style="--platform:${PC[p]}"></span>${p}</td>`+
 vals.map((v,i)=>`<td class="n">${fmt(v)}${i===vals.length-1?`<span class="delta ${v>=vals[i-1]?"up":"down"}">${delta(vals[i-1],v)}</span>`:""}</td>`).join("")+`</tr>`}
 h+=`</tbody></table>`;document.getElementById("weekly").innerHTML=h})();

renderCategoryTrends();

document.getElementById("categoryTabs").innerHTML=PLATS.map((p,i)=>`<button data-p="${esc(p)}" class="${i===0?"on":""}">${p}</button>`).join("");
function renderCategories(platform){document.querySelectorAll("#categoryTabs button").forEach(b=>b.classList.toggle("on",b.dataset.p===platform));
 const rows=D.categories[platform];document.getElementById("categories").innerHTML=`<div class="scroll"><table><thead><tr><th>Category</th><th class="n">Posts</th><th class="n">${D.definitions[platform].metric_label}</th><th class="n">Avg / post</th><th class="n">Engagements</th><th class="n">Rate</th></tr></thead><tbody>`+
 rows.map(x=>`<tr><td>${esc(x.category)}</td><td class="n">${full(x.posts)}</td><td class="n">${full(x.views)}</td><td class="n">${full(x.avg_views)}</td><td class="n">${full(x.eng)}</td><td class="n">${x.er??"—"}%</td></tr>`).join("")+`</tbody></table></div>`}
document.querySelectorAll("#categoryTabs button").forEach(b=>b.addEventListener("click",()=>renderCategories(b.dataset.p)));renderCategories(PLATS[0]);

document.getElementById("weekTabs").innerHTML=D.weeks.map(w=>`<button data-w="${esc(w[0])}">${esc(D.wlbl[w[0]])}</button>`).join("");
function renderTops(week){document.querySelectorAll("#weekTabs button").forEach(b=>b.classList.toggle("on",b.dataset.w===week));
 document.getElementById("tops").innerHTML=PLATS.map(p=>{const rows=(D.top5[week][p]||[]).filter(x=>x.v>0);if(!rows.length)return "";
 return `<h3 style="margin-top:18px"><span class="dot" style="--platform:${PC[p]}"></span>${p}</h3><div class="scroll"><table><thead><tr><th class="n">#</th><th>Date</th><th>Category</th><th>Post</th><th class="n">${D.definitions[p].metric_label}</th><th class="n">Eng.</th></tr></thead><tbody>`+
 rows.map((x,i)=>`<tr><td class="n">${i+1}</td><td>${x.d.slice(5)}</td><td>${esc(x.c)}</td><td>${x.u?`<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t)||"(no text)"}</a>`:esc(x.t)}</td><td class="n">${full(x.v)}</td><td class="n">${full(x.e)}</td></tr>`).join("")+`</tbody></table></div>`}).join("")||`<div class="note">No posts in this week.</div>`}
document.querySelectorAll("#weekTabs button").forEach(b=>b.addEventListener("click",()=>renderTops(b.dataset.w)));renderTops(D.reportWeek);

document.getElementById("platformFilter").innerHTML=`<option value="">All platforms</option>`+PLATS.map(p=>`<option>${p}</option>`).join("");
function renderAll(){const q=document.getElementById("search").value.trim().toLowerCase(),p=document.getElementById("platformFilter").value;
 const rows=D.posts.filter(x=>(!p||x.p===p)&&(!q||(x.t+" "+x.c).toLowerCase().includes(q))).slice(0,500);
 document.getElementById("allPosts").innerHTML=`<table><thead><tr><th>Platform</th><th>Date</th><th>Category</th><th>Post</th><th class="n">Views / impr.</th><th class="n">Eng.</th></tr></thead><tbody>`+
 rows.map(x=>`<tr><td><span class="dot" style="--platform:${PC[x.p]}"></span>${x.p}</td><td>${x.d}</td><td>${esc(x.c)}</td><td>${x.u?`<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t)||"(no text)"}</a>`:esc(x.t)}</td><td class="n">${full(x.v)}</td><td class="n">${full(x.e)}</td></tr>`).join("")+`</tbody></table>`}
document.getElementById("search").addEventListener("input",renderAll);document.getElementById("platformFilter").addEventListener("change",renderAll);renderAll();

document.getElementById("definitions").innerHTML=PLATS.map(p=>{const d=D.definitions[p];return `<div class="card"><h3><span class="dot" style="--platform:${PC[p]}"></span>${p}</h3><div class="definition"><b>Headline metric</b><span>${esc(d.views)}</span><b>Engagements</b><span>${esc(d.engagements)}</span><b>Audience metric</b><span>${esc(d.audience)}</span>${d.subscribers?`<b>Subscribers</b><span>${esc(d.subscribers)}</span>`:""}</div></div>`}).join("");
document.getElementById("sources").innerHTML=D.sources.map(x=>`<li>${esc(x)}</li>`).join("");
</script></body></html>'''

page = (html.replace("__BRAND__", source["brand"])
            .replace("__SCOPE__", scope_label)
            .replace("__PERIOD__", period_label)
            .replace("__YEAR__", year)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
            .replace("__PC__", json.dumps(palette, separators=(",", ":"))))

output = os.path.join(ROOT, "dashboard.html")
index_output = os.path.join(ROOT, "index.html")
for path in (output, index_output):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(page)
print(output, f"{os.path.getsize(output) / 1024:.0f} KB", "+ index.html")

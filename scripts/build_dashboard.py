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


def slim(post):
    return {
        "p": post["platform"], "w": post["week"], "d": post["date"],
        "t": (post["title"] or "")[:220], "u": post["url"], "v": post["views"],
        "e": post["engagements"], "c": post["category"], "y": post["type"],
    }


data = {
    "totals": source["totals"],
    "subscribers": source["youtube_subscribers"],
    "scope": report,
    "weeks": source["weeks"],
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
.tile .label{font-size:11px;text-transform:uppercase;letter-spacing:.065em;color:var(--ink2);font-weight:700}.tile .value{font-size:30px;font-weight:720;letter-spacing:-.035em;margin-top:5px}
.tile .detail{font-size:12px;color:var(--muted);margin-top:4px}.platform-card{position:relative;overflow:hidden}.platform-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--platform)}
.subscriber-card{display:grid;grid-template-columns:minmax(180px,1fr) minmax(0,2fr);align-items:center;gap:20px}.subscriber-card .value{font-variant-numeric:tabular-nums}.subscriber-card .detail{max-width:75ch}
.subscriber-weekly-card{margin-top:14px}.subscriber-weekly-head{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:12px}.subscriber-range{display:flex;align-items:center;gap:9px;flex-wrap:wrap;max-width:100%;font-size:12px;color:var(--ink2)}.subscriber-range .select{width:auto;max-width:100%;min-width:0}.subscriber-weekly-card .note{margin-bottom:10px}
.platform-name{font-weight:730}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:var(--platform)}
.spark{display:block;width:100%;height:38px;margin-top:12px}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}
th{color:var(--ink2);font-size:11px;text-transform:uppercase;letter-spacing:.045em;font-weight:700;text-align:left;padding:9px 10px;border-bottom:1px solid var(--axis);white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--grid);vertical-align:top}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}tr.total td{font-weight:750;border-top:1px solid var(--axis)}.delta{display:block;font-size:10px;font-weight:700;margin-top:1px}
.up{color:var(--good)}.down{color:var(--bad)}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.tabs{display:flex;gap:7px;overflow-x:auto;padding-bottom:7px}.tabs button,.select,input{font:inherit;border:1px solid var(--axis);border-radius:9px;background:var(--surface);color:var(--ink)}
.tabs button{padding:7px 12px;cursor:pointer;white-space:nowrap}.tabs button.on{background:var(--ink);border-color:var(--ink);color:var(--page)}
.category-charts{display:grid;gap:14px}.chart-card{overflow:hidden}.chart-head{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:8px}
.chart-wrap{overflow-x:auto}.line-chart{display:block;width:100%;min-width:690px;height:auto}.category-legend{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.category-key{font:inherit;font-size:11px;border:1px solid var(--grid);border-radius:999px;background:var(--surface2);color:var(--ink);padding:4px 8px;cursor:pointer}
.category-key.off{opacity:.42}.category-key .swatch{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:var(--category)}
.controls{display:grid;grid-template-columns:minmax(210px,1fr) 180px;gap:10px;margin-bottom:10px}.select,input{padding:8px 10px;width:100%}
.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.definition{display:grid;grid-template-columns:110px 1fr;gap:4px 12px;font-size:12px}.definition b{color:var(--ink2)}
.sources{margin:0;padding-left:18px}.sources li{margin:5px 0;color:var(--ink2)}
.footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--axis);color:var(--muted);font-size:11px}
@media(max-width:900px){.hero,.platform-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mast{display:block}.stamp{text-align:left;margin-top:18px}}
@media(max-width:620px){body{padding-left:13px;padding-right:13px}.hero,.platform-grid,.metric-grid,.subscriber-card{grid-template-columns:1fr}.controls{grid-template-columns:1fr}.card{padding:15px}.mast{padding-top:28px}}
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
<div class="note" style="margin-top:7px">X uses impressions; the other platforms use views. Small week-over-week changes can reflect different metric maturity as posts continue accumulating activity.</div></section>

<section><div class="section-head"><div><h2>Weekly category trends</h2><div class="note">Instagram, YouTube, and TikTok categories by publish week.</div></div><div class="tabs" id="categoryMetricTabs"></div></div>
<div class="category-charts" id="categoryTrendCharts"></div>
<div class="note" style="margin-top:7px">Each chart uses its own scale. Select views, engagements, or posts; click a category label to show or hide its line.</div></section>

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
const D=__DATA__,PC=__PC__,PLATS=Object.keys(D.totals),TREND_PLATS=["Instagram","YouTube","TikTok"];
const CAT_COLORS=["#a51d2d","#2166ac","#2a9d8f","#d97706","#7c3aed","#0f766e","#c2410c","#be185d","#4d7c0f","#4338ca","#6b7280","#0891b2","#9333ea","#15803d"];
const ALL_CATS=[...new Set(TREND_PLATS.flatMap(p=>Object.keys(D.categoryWeekly[p]||{})))].sort();
const CAT_COLOR=Object.fromEntries(ALL_CATS.map((c,i)=>[c,CAT_COLORS[i%CAT_COLORS.length]]));
const full=n=>(n||0).toLocaleString();
const fmt=n=>n>=1e9?(n/1e9).toFixed(1)+"B":n>=1e6?(n/1e6).toFixed(1)+"M":n>=1e4?Math.round(n/1e3)+"K":full(n);
const esc=s=>(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
const rate=(e,v)=>v?(100*e/v).toFixed(2)+"%":"—";
const delta=(a,b)=>!a?"—":`${b>=a?"+":""}${Math.round(100*(b-a)/a)}%`;
const spark=(vals,color)=>{const max=Math.max(...vals,1);return `<svg class="spark" viewBox="0 0 160 38" preserveAspectRatio="none" aria-label="Eight-week trend">${vals.map((v,i)=>{const h=Math.max(1,32*v/max);return `<rect x="${i*20+2}" y="${36-h}" width="14" height="${h}" rx="2" fill="${color}" opacity="${i===vals.length-1?1:.48}"/>`}).join("")}</svg>`};

let categoryMetric="views";
const hiddenCategories=Object.fromEntries(TREND_PLATS.map(p=>[p,new Set()]));
const niceScale=value=>{if(value<=0)return {max:1,step:1};const raw=value/4,power=10**Math.floor(Math.log10(raw)),fraction=raw/power,step=(fraction<1.5?1:fraction<3?2:fraction<7?5:10)*power;return {max:Math.ceil(value/step)*step,step}};
function categoryChart(platform){
 const metricLabels={views:"Views",eng:"Engagements",posts:"Posts"},weeks=D.weeks.map(w=>w[0]);
 const series=Object.entries(D.categoryWeekly[platform]||{}).map(([category,byWeek])=>({category,values:weeks.map(w=>byWeek[w][categoryMetric]||0)}));
 const visible=series.filter(s=>!hiddenCategories[platform].has(s.category)),scale=niceScale(Math.max(1,...visible.flatMap(s=>s.values))),max=scale.max,tickCount=Math.round(max/scale.step);
 const W=920,H=320,L=72,R=22,T=20,B=48,innerW=W-L-R,innerH=H-T-B;
 const x=i=>L+(weeks.length===1?innerW/2:i*innerW/(weeks.length-1)),y=v=>T+innerH-(v/max)*innerH;
 const grid=Array.from({length:tickCount+1},(_,i)=>i/tickCount).map(r=>{const yy=y(max*r);return `<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" stroke="var(--grid)"/><text x="${L-10}" y="${yy+4}" text-anchor="end" fill="var(--muted)" font-size="11">${fmt(max*r)}</text>`}).join("");
 const xLabels=weeks.map((w,i)=>`<text x="${x(i)}" y="${H-17}" text-anchor="middle" fill="var(--muted)" font-size="11">${esc(w.replace("Week ","W"))}</text>`).join("");
 const lines=visible.map(s=>{const color=CAT_COLOR[s.category],points=s.values.map((v,i)=>`${x(i)},${y(v)}`).join(" ");return `<g><polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.25" stroke-linejoin="round" stroke-linecap="round"/><title>${esc(s.category)} · ${metricLabels[categoryMetric]}</title>${s.values.map((v,i)=>`<circle cx="${x(i)}" cy="${y(v)}" r="3" fill="${color}" stroke="var(--surface)" stroke-width="1.5"><title>${esc(s.category)} · ${esc(D.wlbl[weeks[i]])}: ${full(v)} ${metricLabels[categoryMetric].toLowerCase()}</title></circle>`).join("")}</g>`}).join("");
 const legend=series.map(s=>`<button class="category-key ${hiddenCategories[platform].has(s.category)?"off":""}" data-platform="${esc(platform)}" data-category="${esc(s.category)}" aria-pressed="${!hiddenCategories[platform].has(s.category)}" style="--category:${CAT_COLOR[s.category]}"><span class="swatch"></span>${esc(s.category)}</button>`).join("");
 return `<div class="card chart-card"><div class="chart-head"><h3><span class="dot" style="--platform:${PC[platform]}"></span>${platform}</h3><span class="note">${metricLabels[categoryMetric]} per week</span></div><div class="chart-wrap"><svg class="line-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${platform} weekly ${metricLabels[categoryMetric].toLowerCase()} by category">${grid}<line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="var(--axis)"/><line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="var(--axis)"/>${xLabels}${lines}</svg></div><div class="category-legend">${legend}</div></div>`;
}
function renderCategoryTrends(){
 const metricLabels={views:"Views",eng:"Engagements",posts:"Posts"};
 document.getElementById("categoryMetricTabs").innerHTML=Object.entries(metricLabels).map(([key,label])=>`<button data-metric="${key}" class="${categoryMetric===key?"on":""}">${label}</button>`).join("");
 document.getElementById("categoryTrendCharts").innerHTML=TREND_PLATS.map(categoryChart).join("");
 document.querySelectorAll("#categoryMetricTabs button").forEach(button=>button.addEventListener("click",()=>{categoryMetric=button.dataset.metric;renderCategoryTrends()}));
 document.querySelectorAll(".category-key").forEach(button=>button.addEventListener("click",()=>{const hidden=hiddenCategories[button.dataset.platform],category=button.dataset.category;hidden.has(category)?hidden.delete(category):hidden.add(category);renderCategoryTrends()}));
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

document.getElementById("platforms").innerHTML=PLATS.map(p=>({p,t:RS.totals[p]})).sort((a,b)=>b.t.views-a.t.views).map(({p,t})=>{
 const vals=D.weeks.map(w=>D.weekly[w[0]][p].views),unit=D.definitions[p].metric_label;
 return `<div class="card tile platform-card" style="--platform:${PC[p]}"><div class="label"><span class="dot"></span><span class="platform-name">${p}</span></div>
 <div class="value">${fmt(t.views)}</div><div class="detail">${unit} · ${fmt(t.eng)} engagements · ${t.posts} posts · ${t.er??"—"}% rate</div>
 ${spark(vals,PC[p])}<div class="detail">YTD: ${fmt(D.totals[p].views)} ${unit} across ${full(D.totals[p].posts)} posts</div></div>`}).join("");

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

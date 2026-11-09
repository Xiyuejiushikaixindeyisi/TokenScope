"""Fill the approved local HTML from the immutable 2026-11-09 report.

Only parses existing Markdown; no product APIs, analysis, or state writes.
Run from any directory with Python 3. Output stays inside this promotion folder.
"""
from pathlib import Path
import collections
import hashlib
import html
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REPORT = ROOT / 'docs/huawei/TOKENSCOPE_PROMOTION_READONLY_20261109.md'
MAPPING = ROOT / 'docs/huawei/appid与对应产品（未去重）.md'
OUT = HERE / 'dist/index.html'
E = html.escape
report = REPORT.read_text()
rows = []
for m in re.finditer(r'### H-(\d+): (.*?) × (.*?)\n(.*?)(?=\n### H-|\n## D\.)', report, re.S):
    num, app, model, body = m.groups()
    n = int(re.search(r'sample_count: (\d+)', body)[1])
    totals = [int(x.replace(',', '')) for x in re.search(r'totals: prompt_tokens=([\d,]+), ideal_cached=([\d,]+), ideal_compute=([\d,]+)', body).groups()]
    bins = [list(map(int, b)) for b in re.findall(r'^\| (\d+) \| (\d+) \| (\d+) \|', body, re.M)]
    mean = sum(upper * count for lower, upper, count in bins) / n
    assert sum(b[2] for b in bins) == n
    assert totals[1] + totals[2] == totals[0]
    assert abs(mean - float(re.search(r'mean_input_tokens_est \(右端点加权\): ([\d.]+)', body)[1])) < .006
    rows.append(dict(id=int(num), appid=app, model=model, n=n, mean=mean,
                     hit=totals[1] / totals[0], bins=bins))
assert len(rows) == 77 and len({r['appid'] for r in rows}) == 67
assert sum(r['n'] for r in rows) == 150698
assert {m: (sum(r['model'] == m for r in rows), sum(r['n'] for r in rows if r['model'] == m)) for m in {r['model'] for r in rows}} == {
    'DeepSeek-V4-Flash-0731': (34, 19186), 'GLM-5.2': (22, 12446), 'Qwen3.6-27B': (21, 119066)}
assert not any(r['appid'] == 'com.huawei.icsl.base' for r in rows)
assert not any(r['mean'] == 10000 for r in rows)

# Exact appid match only, except removing explicit environment annotations.
# No guessed aliases, lowercasing, or matching by similar product names.
names = {}
for line in MAPPING.read_text().splitlines():
    if re.match(r'^\| \d+ \|', line):
        cells = [x.strip() for x in line.split('|')[1:-1]]
        app = re.sub(r'（(?:生产|测试)环境）$', '', cells[1])
        if cells[2] not in ['—', '-']:
            assert app not in names or names[app] == cells[2]
            names[app] = cells[2]

# Display grouping inferred from explicit product names, not confirmed ownership.
domains = {
    '营销服': ['云计算销售助手'],
    '财经': ['财报产品', '前端组件子产品', '财经质量管理产品', '财经文档助手子产品-财经文档综合智能识别模块'],
    '研发': ['天舟人工智能平台', '存储芯片开发工具链'],
    'HR': ['任职资格认证管理'],
}
for r in rows:
    r['product'] = names.get(r['appid'])
    r['domain'] = next((k for k, v in domains.items() if r['product'] in v), '跨域 / 待确认') if r['product'] else '待关联产品'
    r['quadrant'] = ('长' if r['mean'] > 10000 else '短') + ('高' if r['hit'] >= .5 else '低')
counts = collections.Counter(r['quadrant'] for r in rows)
assert counts == {'短高': 9, '长高': 31, '短低': 23, '长低': 14}
employee = next(r for r in rows if r['id'] == 2)
longlow = sorted((r for r in rows if r['quadrant'] == '长低'), key=lambda r: -r['n'])
mapped = {r['appid']: r['product'] for r in rows if r['product']}
assert len(mapped) == len(set(mapped.values())) == 15
q = HERE / 'qa'
q.mkdir(exist_ok=True)
(q / 'report-derived.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))

def head(eyebrow, title, active):
    loc = ''.join(f'<span class="{ "on" if i == active else "" }">{v}</span>' for i, v in enumerate(['产品', '案例', '覆盖', '机会']))
    return f'<header class="slide-head"><div><div class="eyebrow">{eyebrow}</div><h1>{title}</h1></div><div class="location" aria-hidden="true">{loc}</div></header>'

def foot(text, page):
    return f'<footer class="slide-footer"><span class="wordmark">TokenScope</span><span>{text}</span><span>0{page} / 04</span></footer>'

cards = []
for i, (domain, products) in enumerate(domains.items(), 1):
    subset = [r for r in rows if r['domain'] == domain]
    product_list = ''.join(f'<div title="{E(p)}">{E(p.replace("财经文档助手子产品-财经文档综合智能识别模块", "财经文档助手（综合智能识别）"))}</div>' for p in products)
    cards.append(f'<article class="business"><div class="business-head">{domain}<span class="business-number">0{i}</span></div><div class="business-stats"><span><strong>{len(products)}</strong>产品</span><span><strong>{sum(r["n"] for r in subset):,}</strong>请求</span></div><div class="business-list">{product_list}</div><div class="business-bottom">已关联真实结果 · 按产品名初分领域</div></article>')

page3 = f'''<section class="slide" id="page-3" aria-label="第3页：业务覆盖与模型系列" hidden>
{head('业务覆盖 / 营销服 · 财经 · 研发 · HR', '已分析<em>67个业务appid</em>，覆盖三大主流模型系列', 2)}
<div class="slide-body">
 <div class="coverage-kpis">
  <div class="coverage-kpi"><div class="label">已关联业务产品<small>15个appid已关联名称；52个待关联</small></div><div class="big-placeholder verified">15<small>个</small></div></div>
  <div class="coverage-kpi"><div class="label">已分析 appid<small>形成77组 appid × 模型结果</small></div><div class="big-placeholder verified">67<small>个</small></div></div>
  <div class="coverage-kpi"><div class="label">已分析请求<small>2026-10-20真实Trace，约2小时窗口</small></div><div class="big-placeholder verified request-total">150,698<small>次</small></div></div>
 </div>
 <div class="coverage-note"><span class="section-label">业务产品矩阵</span><span class="tag">8个产品按名称初分至四领域 · 7个已知产品跨域 / 归属待确认</span></div>
 <div class="business-grid">{''.join(cards)}</div>
 <div class="models-band"><div class="models-label"><strong>三大主流</strong><br>模型系列</div><div class="model-family"><b>Qwen</b><span>21组 · 119,066次请求</span></div><div class="model-family"><b>DeepSeek</b><span>34组 · 19,186次请求</span></div><div class="model-family"><b>GLM</b><span>22组 · 12,446次请求</span></div></div>
 <div class="value-strip"><strong>推广价值</strong><span>同一套分析方法，跨业务找问题、给证据、推动协同改进</span></div>
 <div class="case-footnote">来源：11月9日只读回传 + appid产品对照表；已排除ICSL构造样本。领域按产品名称初分，非组织归属确认；未关联对象仍计入67个appid及请求总数。此为已分析范围，不代表企业全量覆盖率。</div>
</div>{foot('真实结果 → 关联产品 → 汇总领域；完整明细见讲解与数据说明', 3)}
</section>'''

# Log x-axis keeps 1K–159K loads readable without shifting points or clipping tails.
def x(mean): return 70 + math.log10(mean / 1000) / math.log10(200) * 676
def y(hit): return 415 - hit * 350
split = x(10000)
svg = [f'<svg class="quad-chart" viewBox="0 0 790 530" role="img" aria-label="77组真实appid与模型结果。横轴为平均输入Token估算的对数刻度；10K临时观察线，纵轴50%分界。短高9、长高31、短低23、长低14组。">']
for xx, yy, ww, hh, color in [(70,65,split-70,175,'#eff5f8'),(split,65,746-split,175,'#eef5f0'),(70,240,split-70,175,'#f4f5f7'),(split,240,746-split,175,'#fff0ee')]:
    svg.append(f'<rect x="{xx:.2f}" y="{yy}" width="{ww:.2f}" height="{hh}" fill="{color}"/>')
for h in [0,.25,.5,.75,1]:
    svg.append(f'<line x1="70" x2="746" y1="{y(h)}" y2="{y(h)}" stroke="{"#8996a4" if h==.5 else "#dfe5e9"}"/><text x="58" y="{y(h)+5}" text-anchor="end" class="axis-text">{int(h*100)}%</text>')
for t in [1000,2000,5000,10000,20000,50000,100000,200000]:
    svg.append(f'<line x1="{x(t):.2f}" x2="{x(t):.2f}" y1="65" y2="415" stroke="{"#8996a4" if t==10000 else "#e1e6ea"}" stroke-dasharray="{"6 5" if t==10000 else "2 3"}"/><text x="{x(t):.2f}" y="438" text-anchor="middle" class="axis-text">{t//1000}K</text>')
svg += ['<text x="70" y="28" class="chart-axis-title">理想前缀命中率</text>', '<text x="746" y="470" text-anchor="end" class="chart-axis-title">平均输入Token（估算 · 对数刻度）</text>', f'<text x="{split:.2f}" y="492" text-anchor="middle" class="axis-text">10K · 临时观察线</text>']
for tx, ty, label, col in [(82,55,'短输入 · 高命中  9组','#315c86'),(split+12,55,'长输入 · 高命中  31组','#416b5a'),(82,264,'短输入 · 低命中  23组','#626b78'),(split+12,264,'长输入 · 低命中  14组','#b40000')]:
    svg.append(f'<text x="{tx}" y="{ty}" font-size="17" font-weight="700" fill="{col}" paint-order="stroke" stroke="white" stroke-width="4" stroke-linejoin="round">{label}</text>')
colors = {'DeepSeek-V4-Flash-0731':'#315c86','GLM-5.2':'#398369','Qwen3.6-27B':'#c34639'}
for r in sorted(rows,key=lambda r:(r['id']==2,r['n'])):
    desc = f'{r["product"] or "产品待关联"}｜{r["appid"]}\n{r["model"]}｜{r["n"]:,}条请求\n平均输入 {r["mean"]:,.2f} Token｜理想命中率 {r["hit"]*100:.2f}%\n报告 H-{r["id"]}；{r["quadrant"]}（10K临时线）'
    svg.append(f'<circle class="data-point" data-record="{r["id"]}" tabindex="0" role="img" aria-label="{E(desc)}" cx="{x(r["mean"]):.2f}" cy="{y(r["hit"]):.2f}" r="5.5" fill="{colors[r["model"]]}" fill-opacity=".8" stroke="white" stroke-width="1.4"><title>{E(desc)}</title></circle>')
ex, ey = x(employee['mean']), y(employee['hit'])
svg.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="10" fill="none" stroke="#c00000" stroke-width="2" pointer-events="none"/><path d="M{ex-9:.2f} {ey+4:.2f} l-45 42 h-100" fill="none" stroke="#b00000"/><text x="{ex-152:.2f}" y="{ey+65:.2f}" fill="#b00000" font-size="15" font-weight="700">员工助手 × DeepSeek</text></svg>')

table = []
for r in longlow[:3]:
    display = r['product'] or ('S010320（产品待关联）' if r['appid']=='S010320' else '产品待关联')
    table.append(f'<tr><td><b>{E(display)}</b><small title="{E(r["appid"])}">{E(r["appid"])}</small></td><td>DeepSeek</td><td>{r["n"]:,}</td></tr>')

# Render the existing 5K view; validate against aggregation of the existing 1K bins.
d6 = report.split('### D.6')[1].split('### D.7')[0]
bins5 = [list(map(int, b)) for b in re.findall(r'^\| (\d+) \| (\d+) \| (\d+) \|', d6,re.M)]
aggregated = collections.Counter()
for lower, upper, count in employee['bins']: aggregated[(lower//5000)*5000] += count
assert {a:c for a,b,c in bins5} == dict(aggregated)
hist = ['<svg class="employee-hist" viewBox="0 0 600 155" role="img" aria-label="员工助手DeepSeek，1047条请求，已有5K分箱直方图。主峰45K至50K为112条，分布宽且多峰。">']
for n in [0,60,120]:
    yy=117-n/120*90
    hist.append(f'<line x1="37" x2="581" y1="{yy}" y2="{yy}" stroke="#e0e5ea"/><text x="30" y="{yy+4}" text-anchor="end" class="hist-tick">{n}</text>')
for lower in range(0,125000,5000):
    count=aggregated.get(lower,0);xx=37+lower/125000*544;hh=count/120*90
    hist.append(f'<rect x="{xx+1:.2f}" y="{117-hh:.2f}" width="19.5" height="{hh:.2f}" fill="{"#b90000" if lower==45000 else "#6686a2"}"><title>{lower:,}–{lower+5000:,} Token：{count}条（{count/1047*100:.2f}%）</title></rect>')
for t in range(0,125001,25000):
    hist.append(f'<text x="{37+t/125000*544:.2f}" y="136" text-anchor="middle" class="hist-tick">{t//1000}K</text>')
hist.append('<text x="37" y="16" class="hist-tick">请求数</text><text x="581" y="153" text-anchor="end" class="hist-tick">模板后输入Token · 已有5K分箱</text></svg>')
employee_url = 'http://localhost:18002/#/users?run=ur-07c8abc2e3ea49438cb018cf53bcaa97&appid=S00000000000000000000000000000773&revision=4eaa33edb665be3e709af4fa3fc2bf75c98d96e122dbb4a79bdf5788c90ded63'
page4 = f'''<section class="slide" id="page-4" aria-label="第4页：场景分类与优先优化对象" hidden>
{head('真实负载 / 场景分类与优化机会', '按场景选择优化策略，优先协同改善<em>长输入、低命中</em>业务', 3)}
<div class="slide-body"><div class="chart-layout">
 <div class="quadrants-panel"><div class="panel-heading">业务负载四象限 <span class="tag">77组真实结果 · 悬停可查看详情</span></div>
 {''.join(svg)}
 <div class="legend-row model-legend"><span><i style="background:#315c86"></i>DeepSeek</span><span><i style="background:#398369"></i>GLM</span><span><i style="background:#c34639"></i>Qwen</span><span>每点 = appid × 模型</span></div>
 <div class="scenario-guide"><div><b>长高 / 编码与工具Agent等</b><span>关注剩余计算、路由与并发</span></div><div><b>短低 / 问答、搜索、提取等</b><span>关注负载适配、SLO与排队</span></div><div><b>短高 / 固定模板等</b><span>关注高频调用与执行效率</span></div><div class="priority"><b>长低 / 业务协同重点</b><span>核查动态前缀、工具与消息问题</span></div></div>
 <div class="chart-note">命中分界50%；10K为临时长度观察线，正式分界待定。场景举例不等于任务识别；长低不代表一定可修复。重叠点不偏移，完整明细见说明。</div>
 </div>
 <div class="case-column">
  <div class="candidate-panel"><div class="candidate-title">长输入、低命中：优先核查清单 <span class="tag">14组中的请求量前3</span></div><table class="candidate-table"><thead><tr><th>产品 / appid</th><th>模型</th><th>请求量</th></tr></thead><tbody>{''.join(table)}</tbody></table><div class="minor">暂按平均输入&gt;10K、理想命中&lt;50%筛选；共{sum(r['n'] for r in longlow):,}条请求。先结合业务核查原因，再确定改进方案。</div></div>
  <div class="employee-panel"><div class="employee-head"><strong>重点核查：员工助手</strong><span class="family">DeepSeek-V4-Flash</span></div><div class="appid">S00000000000000000000000000000773 · 1,047条</div><div class="employee-metrics"><div class="employee-metric">平均输入长度（1K箱估算）<b class="verified">44.74<small>K Token</small></b></div><div class="employee-metric">理想命中率<b class="verified">34.81<small>%</small></b></div></div>{''.join(hist)}<div class="chart-note">主峰45K–50K：112条（10.70%）；分布宽且多峰。<br>model_id：DeepSeek-V4-Flash-0731 <a class="source-link" href="{E(employee_url)}" target="_blank" rel="noopener noreferrer">查看华为已有结果 ↗</a></div></div>
 </div>
</div><div class="value-strip"><strong>下一步</strong><span>从真实负载找到关键对象，让业务协同和平台优化各有重点</span></div></div>
{foot('2026-10-20约2小时真实Trace · 1K箱右端点加权均值 · 已排除构造样本',4)}
</section>'''

def detail_table(data, mapped_only=False):
    lines=['<div class="data-table-wrap"><table class="detail-table"><thead><tr><th>产品 / appid</th><th>模型</th><th>请求</th><th>均长Token</th><th>理想命中</th></tr></thead><tbody>']
    for r in data:
        if mapped_only and not r['product']: continue
        lines.append(f'<tr><td>{E(r["product"] or "待关联")}<small>{E(r["appid"])}</small></td><td>{E(r["model"])}</td><td>{r["n"]:,}</td><td>{r["mean"]:,.2f}</td><td>{r["hit"]*100:.2f}%</td></tr>')
    return ''.join(lines)+'</tbody></table></div>'

note3=f'''<div class="note-content" data-note="2" hidden><p><b>建议讲解约2分钟。</b>67个appid、77组appid×模型、150,698条请求来自11月9日只读回传，已排除ICSL构造样本。三大主流系列按本次业务汇报口径命名，非企业总体模型排行。</p><p><b>产品关联与领域初分：</b>对照表关联15个产品名称（15个appid，17组结果）；52个appid缺有效名称映射。8个产品按名称初分到四领域，7个已关联产品暂不强行归属：员工助手、WeLink直播、IOC、e+ IOC、会议管理维稳、交易经营产品、iAudit。领域是展示初分，仍需业务确认。</p><p>匹配保持appid大小写，仅去除“（生产环境）/（测试环境）”描述；cf7…的交易经营产品由此匹配。未把com.huawei.gtsdata.datalinkpro猜作对照表中com.gtsdata.huawei.com.datalinkpro；未分析的标书360、发票识别等不计入。</p><details><summary>查看已关联产品与分析结果（17组）</summary>{detail_table(rows,True)}</details><p>来源为2026-10-20约2小时Trace，报告概述为07:00–09:00 UTC；员工助手源文件观测范围到09:03:42 UTC，因此页面使用“约2小时”。没有企业完整分母，不展示覆盖率百分比。</p></div>'''
note4=f'''<div class="note-content" data-note="3" hidden><p><b>建议讲解约4分钟。</b>50%为已确认命中率分界；10K仅用于本次观察（大于为长、小于为短，本批无恰等于10K）。短高9组、长高31组、短低23组、长低14组，总77组，均为appid×model_id×common_name结果；不是77个独立appid。</p><p>横轴：Σ(区间请求数×右端点)/总请求数，模板后输入长度，统一使用已有1K分箱。右端点估算略偏高；77条均无开放尾箱。图以对数横轴覆盖1K–200K，无删点、随机抖动或尾部截断。颜色表示模型，圆大小不编码请求量；重叠点可能遮挡，完整表如下。</p><p><b>员工助手：</b>DeepSeek-V4-Flash-0731，1,047条，均长44,741.17 Token，理想命中34.81%。均长分子46,844,000；缓存16,124,832 / 输入46,326,632。右侧已有5K直方图与1K合并计数一致，补回零箱；主峰45K–50K仅占10.70%，不是窄高斯分布。</p><p>低命中原因尚未在此报告中诊断，不能认定员工助手具有CCH问题。任务语义、可修复性与SLO承诺需分别确认。员工助手链接来自华为报告，需对应现场SSH转发；本机同端口服务未必持有该run。</p><details><summary>查看长输入、低命中完整14组</summary>{detail_table(longlow)}</details><details><summary>查看全部77组真实结果</summary>{detail_table(rows)}</details></div>'''

s=OUT.read_text()
s=re.sub(r'<section class="slide" id="page-3".*?</section>',lambda _:page3,s,flags=re.S)
s=re.sub(r'<section class="slide" id="page-4".*?</section>',lambda _:page4,s,flags=re.S)
s=re.sub(r'<div class="note-content" data-note="2".*?(?=\n <div class="note-content" data-note="3")',lambda _:note3,s,flags=re.S)
s=re.sub(r'<div class="note-content" data-note="3".*?(?=\n <p class="source">)',lambda _:note4,s,flags=re.S)
s=s.replace('业务汇报（四页讨论版）','业务汇报（现场数据版）').replace('业务汇报 · 四页讨论版','业务汇报 · 现场数据版')
s=s.replace('讲解与占位说明','讲解与数据说明').replace('讲解与占位','讲解与数据')
s=s.replace('四页结构预览 · 待报告字段已留占位','11月9日回传已填入 · 长度10K暂作观察线')
s=s.replace('内容基线：2026-11-09四页方案与最新只读取证要求。该文件为独立HTML讨论稿，未连接真实数据接口，未更改产品服务或前端。','内容基线：2026-11-09四页方案 + TOKENSCOPE_PROMOTION_READONLY_20261109.md + appid产品对照表。离线静态报告，无自动接口调用。CPU/GPU耗时、历史闭环周期及线上收益仍待补证；演进功能保持标注。')
extra_css='''
/* 2026-11-09: report-backed data, within the approved four-slide layout. */
.verified{color:var(--red)!important}.request-total{font-size:40px}.business-stats strong{color:#465363}.business-list{font-size:17px;gap:13px}.model-family{flex-direction:column;gap:4px}.model-family span{font-size:13px}.business-bottom{color:#727b85;background:#f7f8fa;border-color:#e0e4e8}.axis-text{font:14px "Microsoft YaHei",Arial;fill:#697583}.chart-axis-title{font:15px "Microsoft YaHei",Arial;fill:#52606e}.data-point{cursor:help}.data-point:hover,.data-point:focus{stroke:#24262b;stroke-width:3;fill-opacity:1;outline:none}.quad-chart{min-height:270px}.model-legend{justify-content:flex-start;gap:21px;margin:0 0 9px}.model-legend span{display:flex;align-items:center;gap:5px;font-size:12px}.model-legend i{display:inline-block;width:9px;height:9px;border-radius:50%}.scenario-guide{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:8px}.scenario-guide>div{background:#f4f6f8;padding:7px 10px;font-size:12px;line-height:1.5;border-left:2px solid #a8b7c3}.scenario-guide b,.scenario-guide span{display:block}.scenario-guide b{font-size:13px;font-weight:600}.scenario-guide span{color:#76808a}.scenario-guide .priority{background:#fff2f0;border-color:#c00000;color:#aa1515}.candidate-table{table-layout:fixed}.candidate-table th:nth-child(1){width:63%}.candidate-table th:nth-child(2){width:20%}.candidate-table th:nth-child(3){width:17%}.candidate-table td{color:#4b5058;padding:8px}.candidate-table td b{font-weight:500;font-size:14px}.candidate-table td small{display:block;font:10.5px Consolas,monospace;overflow-wrap:anywhere;color:#7b8189;margin-top:2px}.employee-hist{width:100%;min-height:92px;flex:1;display:block}.hist-tick{font:11px "Microsoft YaHei",Arial;fill:#77818c}.employee-head .family{font-size:13px}.source-link{color:#315c86;text-decoration:none;margin-left:8px}.notes{width:min(960px,95vw)}.notes summary{cursor:pointer;font-weight:600;color:#315c86;margin:13px 0}.data-table-wrap{overflow:auto}.detail-table{width:100%;border-collapse:collapse;font-size:11px;line-height:1.5}.detail-table th,.detail-table td{padding:7px;border:1px solid #dbe0e5;text-align:left}.detail-table th{background:#f1f4f7}.detail-table td small{display:block;color:#7a838d;overflow-wrap:anywhere}.detail-table td:first-child{max-width:270px}.plot-tooltip{position:fixed;z-index:30;pointer-events:none;background:#263440f5;color:white;padding:10px 13px;font-size:12px;line-height:1.7;white-space:pre-line;max-width:min(440px,90vw);box-shadow:0 3px 12px #0003}.plot-tooltip[hidden]{display:none}
'''
s=re.sub(r'\n*/\* 2026-11-09: report-backed data.*?(?=</style>)','',s,flags=re.S)
s=s.replace('</style>',extra_css+'</style>')
if 'id="plot-tooltip"' not in s:
    s=s.replace('<script>','<div class="plot-tooltip" id="plot-tooltip" hidden role="status"></div>\n<script>',1)
tooltip_js='''
// Report point details are local DOM text, never an API request.
const plotTip=document.getElementById('plot-tooltip');
document.querySelectorAll('.data-point').forEach(p=>{
 const display=(event)=>{plotTip.textContent=p.getAttribute('aria-label');plotTip.hidden=false;const rect=p.getBoundingClientRect();const px=event?.clientX??rect.right,py=event?.clientY??rect.top;plotTip.style.left=Math.max(8,Math.min(px+14,innerWidth-plotTip.offsetWidth-12))+'px';plotTip.style.top=Math.max(8,Math.min(py+14,innerHeight-plotTip.offsetHeight-12))+'px';};
 p.addEventListener('pointerenter',display);p.addEventListener('pointermove',display);p.addEventListener('focus',()=>display());p.addEventListener('click',display);p.addEventListener('pointerleave',()=>plotTip.hidden=true);p.addEventListener('blur',()=>plotTip.hidden=true);
});
document.addEventListener('keydown',()=>plotTip.hidden=true);document.querySelectorAll('[data-goto],#next,#previous').forEach(b=>b.addEventListener('click',()=>plotTip.hidden=true));
'''
if 'const plotTip=' not in s:s=s.replace("window.addEventListener('resize',resize);",tooltip_js+"\nwindow.addEventListener('resize',resize);")
OUT.write_text(s)

summary={
    'report_sha256':hashlib.sha256(REPORT.read_bytes()).hexdigest(),
    'mapping_sha256':hashlib.sha256(MAPPING.read_bytes()).hexdigest(),
    'groups':77,'appids':67,'requests':150698,'mapped_products':15,
    'unknown_product_appids':52,'quadrants_at_provisional_10k':dict(counts),
    'long_low_requests':sum(r['n'] for r in longlow),
    'employee':{k:v for k,v in employee.items() if k!='bins'},
    'html_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
}
(q/'report-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))

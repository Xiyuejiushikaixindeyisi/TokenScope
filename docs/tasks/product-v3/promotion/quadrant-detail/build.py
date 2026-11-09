"""Build the offline quadrant report from already collected Markdown results."""
from pathlib import Path
import collections
import hashlib
import html
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = ROOT / 'docs/huawei/TOKENSCOPE_PROMOTION_READONLY_20261109.md'
MAPPING = ROOT / 'docs/huawei/appid与对应产品（未去重）.md'
SOURCE_SHA = '31ee6957e16c6ddcc09c61e5abde2490be8b532a7fa3801d801d197304a5b5ab'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
report = SOURCE.read_text()
esc = html.escape
models = ['DeepSeek-V4-Flash-0731', 'GLM-5.2', 'Qwen3.6-27B']
short_models = dict(zip(models, ['DeepSeek', 'GLM', 'Qwen']))
model_colors = dict(zip(models, ['#3e7197', '#3c8c78', '#99704c']))
quads = [('lh', '长输入 · 高命中', '平均输入 > 10K · 理想命中 ≥ 50%'),
         ('sl', '短输入 · 低命中', '平均输入 < 10K · 理想命中 < 50%'),
         ('sh', '短输入 · 高命中', '平均输入 < 10K · 理想命中 ≥ 50%'),
         ('ll', '长输入 · 低命中', '平均输入 > 10K · 理想命中 < 50%')]
names = {}
for line in MAPPING.read_text().splitlines():
    if re.match(r'^\| \d+ \|', line):
        cells = [x.strip() for x in line.split('|')[1:-1]]
        key = re.sub(r'（(?:生产|测试)环境）$', '', cells[1])
        if cells[2] not in ['—', '-']:
            assert key not in names or names[key] == cells[2]
            names[key] = cells[2]
rows = []
for match in re.finditer(r'### H-(\d+): (.*?) × (.*?)\n(.*?)(?=\n### H-|\n## D\.)', report, re.S):
    number, appid, model, body = match.groups()
    n = int(re.search(r'sample_count: (\d+)', body)[1])
    p, h, c = [int(v.replace(',', '')) for v in re.search(r'totals: prompt_tokens=([\d,]+), ideal_cached=([\d,]+), ideal_compute=([\d,]+)', body).groups()]
    bins = [list(map(int, v)) for v in re.findall(r'^\| (\d+) \| (\d+) \| (\d+) \|', body, re.M)]
    mean = sum(upper * count for lower, upper, count in bins) / n
    hit = h / p
    assert sum(b[2] for b in bins) == n and h + c == p
    assert abs(mean - float(re.search(r'mean_input_tokens_est \(右端点加权\): ([\d.]+)', body)[1])) < .006
    assert mean != 10000, 'Equality needs a separate boundary group; do not silently assign.'
    quadrant = ('l' if mean > 10000 else 's') + ('h' if hit >= .5 else 'l')
    rows.append(dict(id=int(number), appid=appid, model=model, n=n, mean=mean,
                     hit=hit, bins=bins, quadrant=quadrant, product=names.get(appid, '')))
assert len(rows) == 77 and len({r['appid'] for r in rows}) == 67
assert sum(r['n'] for r in rows) == 150698
assert not any(r['appid'] == 'com.huawei.icsl.base' for r in rows)
assert collections.Counter(r['quadrant'] for r in rows) == {'lh':31, 'sl':23, 'sh':9, 'll':14}

def fmt(v): return f'{v:,}'
def axis(v): return f'{v/1000:g}K' if v else '0'
def histogram(r):
    # Full finite nonzero range with intervening zero bins preserved. No fitted curve.
    xmax = max(5000, max(b[1] for b in r['bins']))
    bars = {b[0]: b[2] for b in r['bins']}
    max_count = max(bars.values())
    rough = max_count / 3
    magnitude = 10 ** math.floor(math.log10(rough))
    step = int(max(1, next(v * magnitude for v in [1, 2, 5, 10] if v * magnitude >= rough)))
    ymax = math.ceil(max_count / step) * step
    left, top, width, height = 48, 26, 530, 118
    out = [f'<svg class="histogram" viewBox="0 0 600 181" role="img" aria-label="{esc(r["appid"])}，{r["n"]}条请求，输入长度直方图，1K分箱，横轴0至{xmax} Token。"><title>已有模板后输入长度分布 · 1K分箱</title>']
    for tick in range(0, ymax+1, step):
        yy=top+height-tick/ymax*height
        out.append(f'<line x1="{left}" x2="{left+width}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#e8edf2"/><text x="{left-9}" y="{yy+4:.2f}" text-anchor="end">{fmt(tick)}</text>')
    for lower in range(0,xmax,1000):
        count=bars.get(lower,0)
        xx=left+lower/xmax*width; bar_width=width*1000/xmax
        hh=count/ymax*height
        label=f'{fmt(lower)}–{fmt(lower+1000)} Token：{fmt(count)}条（{count/r["n"]*100:.2f}%）'
        out.append(f'<rect class="bar" x="{xx+.25:.2f}" y="{top+height-hh:.2f}" width="{max(.5,bar_width-.5):.2f}" height="{hh:.2f}" fill="{model_colors[r["model"]]}" data-bin="{lower}" data-count="{count}" data-detail="{esc(label)}"><title>{esc(label)}</title></rect>')
    for tick in sorted({0, round(xmax/4), round(xmax/2), round(xmax*3/4), xmax}):
        out.append(f'<text x="{left+tick/xmax*width:.2f}" y="163" text-anchor="middle">{axis(tick)}</text>')
    out.append('<text x="48" y="13">请求数</text><text x="578" y="179" text-anchor="end">模板后输入 Token</text></svg>')
    return ''.join(out)

def card(r):
    title = r['product'] or '产品名称待关联'
    n_label = '<span class="sample-note">少于30条</span>' if r['n'] < 30 else ''
    table = ''.join(f'<tr><td>[{fmt(a)}, {fmt(b)})</td><td>{fmt(c)}</td><td>{c/r["n"]*100:.2f}%</td></tr>' for a,b,c in r['bins'])
    return f'''<article class="request-card" id="record-{r['id']}" data-id="{r['id']}" data-search="{esc(r['appid']+' '+r['product'])}" data-requests="{r['n']}" data-mean="{r['mean']}" data-hit="{r['hit']}">
 <div class="card-heading"><span class="product-name">{esc(title)}</span><span class="source-id">H-{r['id']}</span></div>
 <h3 class="appid">{esc(r['appid'])}</h3>
 <div class="metrics"><div><span>平均输入长度 <small>估算</small></span><strong>{r['mean']:,.2f}<small>Token</small></strong></div><div><span>理想命中率</span><strong>{r['hit']*100:.2f}<small>%</small></strong></div><div><span>请求量 {n_label}</span><strong>{fmt(r['n'])}<small>条</small></strong></div></div>
 <div class="hist-head"><span>请求长度分布</span><small>1K分箱 · 全部{fmt(r['n'])}条</small></div>{histogram(r)}
 <details class="bin-detail"><summary>查看分箱明细 <span>{len(r['bins'])}个非零区间</span></summary><div class="bin-table"><table><thead><tr><th>输入Token区间</th><th>请求量</th><th>占比</th></tr></thead><tbody>{table}</tbody></table></div><p>左闭右开；零计数区间仅在表中省略，图中保留空白间隔。</p></details>
</article>'''

sections=[];tab_buttons=[];summary={}
for qi,(key,title,rule) in enumerate(quads,1):
    subset=[r for r in rows if r['quadrant']==key]
    total=sum(r['n'] for r in subset)
    summary[key]={'groups':len(subset),'requests':total,'models':{m:sum(r['model']==m for r in subset) for m in models}}
    priority='<span class="priority-label">重点优化</span>' if key=='ll' else ''
    tab_buttons.append(f'<button type="button" class="quadrant-tab {"priority-tab" if key=="ll" else ""}" data-quad="{key}" aria-pressed="false"><span class="tab-top"><span>{qi:02}</span>{priority}</span><b>{title}</b><span class="tab-total"><strong>{len(subset)}</strong>组 <i>·</i> {fmt(total)}条请求</span><small>{rule}</small></button>')
    groups=[]
    for model in models:
        items=sorted((r for r in subset if r['model']==model), key=lambda r:(-r['n'],r['appid']))
        count=sum(r['n'] for r in items)
        cards=''.join(card(r) for r in items)
        groups.append(f'<section class="model-section" data-model="{esc(model)}"><header class="model-heading"><h3><i style="background:{model_colors[model]}"></i>{esc(model)}</h3><span class="model-count">{len(items)}组 · {fmt(count)}条请求</span></header><div class="card-grid">{cards}</div><div class="model-empty" {"hidden" if items else ""}>该模型在此象限暂无结果。</div></section>')
    sections.append(f'<section class="quadrant-section" id="quadrant-{key}" data-quadrant="{key}"><header class="quadrant-heading"><div><span class="eyebrow">QUADRANT {qi:02}</span><h2>{title} {priority}</h2><p>{rule}</p></div><div class="section-total">{len(subset)}组结果 · {fmt(total)}条请求</div></header>{"".join(groups)}</section>')

template = (HERE/'template.html').read_text()
result=template.replace('<!--QUADRANT_TABS-->',''.join(tab_buttons)).replace('<!--QUADRANT_SECTIONS-->','\n'.join(sections))
(HERE/'dist').mkdir(exist_ok=True)
(HERE/'dist/index.html').write_text(result)
(HERE/'qa').mkdir(exist_ok=True)
manifest={'source_sha256':SOURCE_SHA,'groups':77,'appids':67,'requests':150698,'quadrants':summary,
          'card_count':result.count('class="request-card"'),'histogram_count':result.count('class="histogram"'),
          'html_sha256':hashlib.sha256(result.encode()).hexdigest(),'html_bytes':len(result.encode())}
assert manifest['card_count']==manifest['histogram_count']==77
(HERE/'qa/validation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(manifest,ensure_ascii=False,indent=2))

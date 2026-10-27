// Backend-owned joint acceptance: real service, explicit network fault injection only.
import { test, expect } from '@playwright/test';
import { createHash } from 'node:crypto';
const fmt = (s: string) => BigInt(s).toLocaleString('en-US');
const models = ['GLM-5.2','Qwen3.6-27B','DeepSeek-V4-Flash-0731'];
test.beforeEach(() => test.skip(process.env.TOKENSCOPE_JOINT !== '1', 'Explicit isolated joint state required'));
test('J01/J04: every group metrics, all 1029 bins and quantiles equal real backend', async ({ page, request }, info) => {
  test.setTimeout(180000);
  const catalog = await (await request.get('/monitoring/catalog')).json(); expect(catalog.items).toHaveLength(15);
  const evidence = [];
  for (const item of catalog.items) {
    const s = await (await request.get(`/analysis-runs/${item.active_run_id}/view-snapshot`, { params: { appid: item.appid } })).json();
    await page.goto(`/#/overview?appid=${item.appid}&model=${encodeURIComponent(item.model_id)}`);
    await expect(page.locator('.metric-grid')).toBeVisible();
    await expect(page.getByText('当前范围：', { exact:false })).toContainText(s.identity.run_id);
    const values = [s.metrics.ideal_hit_rate === null ? '—' : (s.metrics.ideal_hit_rate*100).toFixed(2)+'%', fmt(s.metrics.request_count), ...Object.values(s.metrics.totals).map(v => v)];
    const labels = ['json_tokens','prompt_tokens','ideal_cached_input_tokens','ideal_compute_input_tokens','completion_tokens'];
    expect(await page.locator('.metric strong').allTextContents()).toEqual([values[0],values[1],...labels.map(k=>fmt(s.metrics.totals[k]))]);
    for (const width of ['1000','2000','5000']) {
      await page.getByLabel('分箱宽度').selectOption(width);
      for (const [i, key] of ['json_tokens','prompt_tokens','ideal_compute_input_tokens'].entries()) {
        const chart=page.locator('.chart').nth(i), h=s.distributions[key][width], q=s.metrics.quantiles[key];
        expect(await chart.locator('rect').count()).toBe(h.bins.length);
        expect(await chart.locator('rect[data-mode="true"]').count()).toBe(h.summary.mode_bin_indices.length);
        expect(await chart.locator('.quantiles b').allTextContents()).toEqual([fmt(q.p50),fmt(q.p80),fmt(q.p90)]);
        const texts=await chart.locator('rect').evaluateAll(es=>es.map(e=>e.getAttribute('aria-label')));
        h.bins.forEach((b: {count:string}, n:number)=>expect(texts[n]).toContain(`${fmt(b.count)} 个请求`));
      }
    }
    const time = new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'}).format(new Date(s.provenance.data_range_utc.start));
    await expect(page.locator('.identity')).toContainText(time);
    evidence.push({ run:s.identity.run_id, appid:item.appid, model:item.model_id, checkedBins:1029 });
  }
  await info.attach('all-groups', {body:JSON.stringify(evidence),contentType:'application/json'});
});
test('J02/J03/J05: real SSE publication pins edits; real CAS; immutable historical bytes', async ({ page, request }, info)=>{
  test.setTimeout(90000);
  const c=await (await request.get('/monitoring/catalog')).json(); const item=c.items.find((x:{model_id:string})=>x.model_id===models[0]);
  const url=`/analysis-runs/${item.active_run_id}/view-snapshot?appid=${item.appid}`;
  const old=await (await request.get(url)).body();
  await page.goto(`/#/settings?appid=${item.appid}&model=${models[0]}`);
  await expect(page.getByLabel('Block size',{exact:true})).toBeVisible();
  const endpoint='/monitoring/models/GLM-5.2/settings'; const settings=await (await request.get(endpoint)).json();
  await page.getByLabel('Block size',{exact:true}).fill('256');
  expect((await request.put(endpoint,{data:{expected_revision:settings.settings.revision,changes:{block_size:'64'}}})).ok()).toBeTruthy();
  await page.getByRole('button',{name:'保存下一运行设置'}).click(); await expect(page.getByText('设置已被更新，当前草稿已保留。请对照服务器新版本后决定是否重新保存。')).toBeVisible();
  await expect(page.getByLabel('Block size',{exact:true})).toHaveValue('256');
  await page.getByRole('button',{name:'确认以新版本保存当前草稿'}).click(); await expect(page.getByText('已保存，仅对下一次启动运行生效；当前结果保持原设置。')).toBeVisible();
  const run=await (await request.post('/analysis-runs',{data:{file_ref:'model-1.csv',model_id:models[0],submission_key:'joint-pin-'+Date.now()}})).json();
  await expect(page.getByText('新结果可查看。',{exact:false})).toBeVisible({timeout:60000});
  await expect(page.getByText('当前范围：',{exact:false})).toContainText(item.active_run_id);
  expect(await (await request.get(url)).body()).toEqual(old);
  await page.getByRole('button',{name:'切换到新完整结果'}).click();await expect(page.getByText('当前范围：',{exact:false})).toContainText(run.run_id);
  await page.getByRole('link',{name:'监控概览'}).click(); await expect(page.locator('.identity')).toContainText('Block size 256');
  let fetches=0;page.on('request',r=>{if(r.url().includes('/view-snapshot'))fetches++;});
  await page.getByRole('link',{name:'请求长度分布'}).click();await page.getByRole('link',{name:'监控概览'}).click();expect(fetches).toBe(0);
  await page.context().setOffline(true); await expect(page.locator('.metric-grid')).toBeVisible(); await page.context().setOffline(false);
  await expect(page.getByText('通知已连接',{exact:false})).toBeVisible({timeout:15000});
  const current=await (await request.get(endpoint)).json();await request.put(endpoint,{data:{expected_revision:current.settings.revision,changes:{block_size:settings.settings.block_size}}});
  await info.attach('publication', {body:JSON.stringify({old:item.active_run_id,new:run.run_id,oldSha:createHash('sha256').update(old).digest('hex'),extraSnapshotGets:fetches}),contentType:'application/json'});
});
test('R1/J05: accepted POST response lost, real persistent receipt recovers after reload',async({page,request},info)=>{
  test.setTimeout(60000); let key=''; let run=''; let posts=0;
  await page.route('**/analysis-runs',async route=>{
    if(route.request().method()!=='POST') return route.continue();
    posts++; key=route.request().postDataJSON().submission_key;
    const accepted=await route.fetch();run=(await accepted.json()).run_id;await route.abort('connectionfailed');
  });
  await page.goto('/#/submissions');await expect(page.getByText('通知已连接',{exact:false})).toBeVisible();
  await page.getByLabel('file_ref').fill('model-1.csv');await page.getByLabel('确认启动该文件的监控计算').check();await page.getByRole('button',{name:'提交监控任务',exact:true}).click();
  await expect.poll(()=>key).not.toBe('');
  await expect.poll(async()=> (await (await request.get('/analysis-submissions/'+key)).json()).status,{timeout:45000}).toBe('completed');
  await page.reload();await expect(page.locator('.signal').filter({hasText:key})).toContainText('completed');expect(posts).toBe(1);
  const same=await (await request.post('/analysis-runs',{data:{file_ref:'model-1.csv',model_id:models[0],submission_key:key}})).json();expect(same.run_id).toBe(run);
  await info.attach('lost-response',{body:JSON.stringify({key,run,posts,recovered:'completed'}),contentType:'application/json'});
});
test('J04/R2: actual NDJSON into OPFS; corrupted real SHA aborts; empty filtered export',async({page,request},info)=>{
  test.setTimeout(60000);
  const c=await (await request.get('/monitoring/catalog')).json(), item=c.items[0];
  await page.goto(`/#/requests?appid=${item.appid}&model=${encodeURIComponent(item.model_id)}`);await expect(page.locator('tbody tr')).toHaveCount(50);
  await page.evaluate(()=>{
    Object.assign(window,{jointWrite:{close:0,abort:0,size:0}});
    Object.defineProperty(window,'showSaveFilePicker',{configurable:true,value:async()=>{
      const root=await navigator.storage.getDirectory(), handle=await root.getFileHandle('joint-export.ndjson',{create:true});
      return {createWritable:async()=>{const writable=await handle.createWritable();return {write:(b:Uint8Array<ArrayBuffer>)=>writable.write(b),close:async()=>{await writable.close();Object.assign(window,{jointWrite:{close:1,abort:0,size:(await handle.getFile()).size}});},abort:async()=>{await writable.abort();Object.assign(window,{jointWrite:{close:0,abort:1,size:0}});}};}};
    }});
  });
  await page.getByRole('button',{name:'导出 NDJSON'}).click();await expect(page.getByRole('status')).toContainText('SHA256 与记录数一致');
  const stored=await page.evaluate(async()=>{const h=await(await navigator.storage.getDirectory()).getFileHandle('joint-export.ndjson');return(await h.getFile()).text();});
  const lines=stored.trimEnd().split('\n'), summary=JSON.parse(lines.at(-1)!);expect(summary.request_lines_sha256).toBe(createHash('sha256').update(lines.slice(1,-1).join('\n')+'\n').digest('hex'));
  await page.route('**/requests/export?**',async route=>{const response=await route.fetch();const body=(await response.text()).replace(/"request_lines_sha256":"[a-f0-9]{64}"/,'"request_lines_sha256":"'+'0'.repeat(64)+'"');await route.fulfill({response,body});});
  await page.getByRole('button',{name:'导出 NDJSON'}).click();await expect(page.getByRole('status')).toContainText('REQUEST_SHA256_MISMATCH');
  expect(await page.evaluate(()=>Reflect.get(window,'jointWrite'))).toMatchObject({close:0,abort:1});
  await page.unroute('**/requests/export?**');await page.getByLabel('hash_id',{exact:true}).fill('absent-joint-id');await expect(page.getByText('该筛选范围没有请求。')).toBeVisible();
  await page.getByRole('button',{name:'导出 NDJSON'}).click();await expect(page.getByRole('status')).toContainText('SHA256 与记录数一致');
  const empty=await page.evaluate(async()=>{const h=await(await navigator.storage.getDirectory()).getFileHandle('joint-export.ndjson');return(await h.getFile()).text();});expect(JSON.parse(empty.trimEnd().split('\n').at(-1)!)).toMatchObject({actual_rows:'0',request_lines_sha256:createHash('sha256').digest('hex')});
  await info.attach('real-file-validation',{body:JSON.stringify({normalRows:summary.actual_rows,normalBytes:Buffer.byteLength(stored),emptyBytes:Buffer.byteLength(empty),corruptAborted:true,picker:'controlled OPFS handle; real disk writes, no OS dialog'}),contentType:'application/json'});
});

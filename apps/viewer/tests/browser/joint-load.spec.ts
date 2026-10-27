import {test,expect} from '@playwright/test';
test('J01/J04 full Poisson 3-model 5-app workload including 66K and 200K tails',async({page,request},info)=>{
 test.skip(process.env.TOKENSCOPE_JOINT!=='1','explicit joint inputs only');test.setTimeout(240000);
 const evidence=[];
 await page.goto('/#/submissions');await expect(page.getByText('通知已连接',{exact:false})).toBeVisible();
 for(const [i,model] of ['GLM-5.2','Qwen3.6-27B','DeepSeek-V4-Flash-0731'].entries()){
  const start=Date.now();await page.getByLabel('file_ref').fill(`poisson-${i+1}.csv`);await page.locator('.panel label').filter({hasText:/^模型 /}).locator('select').selectOption(model);await page.getByLabel('确认启动该文件的监控计算').check();await page.getByRole('button',{name:'提交监控任务',exact:true}).click();await expect(page.locator('.signal').filter({hasText:`poisson-${i+1}.csv`})).toContainText('completed',{timeout:90000});
  const c=await(await request.get('/monitoring/catalog')).json(),groups=c.items.filter((x:{model_id:string})=>x.model_id===model);expect(groups).toHaveLength(5);let total=0;
  for(const g of groups){const s=await(await request.get(`/analysis-runs/${g.active_run_id}/view-snapshot`,{params:{appid:g.appid}})).json();const t=s.metrics.totals;expect(BigInt(t.ideal_cached_input_tokens)+BigInt(t.ideal_compute_input_tokens)).toBe(BigInt(t.prompt_tokens));expect(BigInt(s.distributions.prompt_tokens['5000'].summary.overflow_count)).toBeGreaterThan(0n);total+=Number(s.metrics.request_count);}
  expect(total).toBeGreaterThan(9000);evidence.push({model,total,elapsedMs:Date.now()-start,groups:5});
 }
 const c=await(await request.get('/monitoring/catalog')).json(),g=c.items[0];await page.goto(`/#/overview?appid=${g.appid}&model=${encodeURIComponent(g.model_id)}`);await expect(page.locator('.metric-grid')).toBeVisible();await info.attach('poisson-overview',{body:await page.screenshot({fullPage:true}),contentType:'image/png'});
 const tail=page.locator('.chart').nth(1).locator('rect').last();await tail.click();await expect(page.getByText('当前区间：',{exact:false})).toContainText('200,000');await expect(page.locator('tbody tr').first()).toBeVisible();
 const download=page.waitForEvent('download');await page.evaluate(()=>Object.defineProperty(window,'showSaveFilePicker',{value:undefined,configurable:true}));await page.getByRole('button',{name:'导出 NDJSON'}).click();const d=await download;await expect(page.getByRole('status')).toContainText('SHA256 与记录数一致');await d.saveAs(info.outputPath('tail-requests.ndjson'));
 await info.attach('poisson-workload',{body:JSON.stringify(evidence),contentType:'application/json'});
});

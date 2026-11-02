import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const fixturePath=process.env.TOKENSCOPE_SOURCE_LINK_FIXTURE;
test.beforeEach(()=>test.skip(!fixturePath,'fresh real backend required'));
const metrics=['json_tokens','prompt_tokens','ideal_compute_input_tokens'];
for(const scenario of ['user','legacy','requests','second-segment']) test('pointer uses actual circle position across viewport resize: '+scenario,async({page,request},testInfo)=>{
 test.setTimeout(120000);
 const root=path.dirname(fixturePath!),f=JSON.parse(fs.readFileSync(fixturePath!,'utf8')),base=JSON.parse(fs.readFileSync(path.join(root,'base-acceptance.json'),'utf8')),large=JSON.parse(fs.readFileSync(path.join(root,'rank-segment-fixture.json'),'utf8'));
 if(process.env.TOKENSCOPE_POINTER_C2==='1')await page.route('http://localhost:4191/**',async route=>{
  const u=new URL(route.request().url()),old=path.resolve(root,'../approved-ui-review-fixes-20261102-c2/dist'),file=path.join(old,u.pathname==='/'?'index.html':u.pathname);
  if((u.pathname==='/'||u.pathname.startsWith('/assets/'))&&fs.existsSync(file))return route.fulfill({path:file,contentType:file.endsWith('.html')?'text/html':file.endsWith('.css')?'text/css':'application/javascript'});
  await route.continue();
 });
 let run:string,appid:string,url:string;
 if(scenario==='legacy'||scenario==='requests'){
  const s=base.scopes[0];run=s.run_id;appid=s.appid;url='/#/'+(scenario==='legacy'?'distributions':'requests')+'?'+new URLSearchParams({run,appid,model:base.runs.find((r:{run_id:string})=>r.run_id===run).model_id});
 }else{
  const receipt=scenario==='user'?JSON.parse(await (await request.get('/monitoring/user-v2/runs/'+f.other.user_run_id,{headers:{'X-TokenScope-Instance-Id':f.service_instance_id}})).text()):large;
  run=receipt.base_run_id;appid='synthetic-app-1';url='/#/users?'+new URLSearchParams({run:receipt.user_run_id,appid});
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(url);
 if(scenario==='requests')await page.getByLabel('辅助排名图（每段至多1000点）').check();else await page.getByLabel('分布视图',{exact:true}).selectOption('rank');
 const offset=scenario==='second-segment'?'1000':'0',records:unknown[]=[];
 if(offset==='1000')for(const card of await page.locator('.distributions article').all()){await expect(card.getByRole('button',{name:'下一段'})).toBeEnabled();await card.getByRole('button',{name:'下一段'}).click();}
 const oracle=await Promise.all(metrics.map(async metric=>{
  const response=await request.get('/analysis-runs/'+run+'/requests?'+new URLSearchParams({appid,sort_by:metric,sort_order:'desc',offset,limit:'1000'}),{headers:{'X-TokenScope-Instance-Id':f.service_instance_id}});
  expect(response.ok()).toBeTruthy();return response.json();
 }));
 try{
  for(const width of [1440,390,1920,1440]){
   await page.setViewportSize({width,height:width===390?844:1080});
   for(let metricIndex=0;metricIndex<3;metricIndex++){
    if(scenario==='requests')await page.getByRole('combobox',{name:'排序',exact:true}).selectOption(metrics[metricIndex]!);
    const chart=page.locator('.rank-chart svg').nth(scenario==='requests'?0:metricIndex),rows=oracle[metricIndex].items;
    await expect(chart.locator('circle:has(title)')).toHaveCount(rows.length);
    await chart.scrollIntoViewIfNeeded();
    for(const i of [...new Set([0,Math.floor(rows.length/2),rows.length-1])]){
     const circle=chart.locator('circle:has(title)').nth(i);const bounds=await circle.boundingBox();expect(bounds).not.toBeNull();
     await page.mouse.move(bounds!.x+bounds!.width/2,bounds!.y+bounds!.height/2);
     const r=rows[i],expected='排名 #'+(BigInt(offset)+BigInt(i)+1n).toLocaleString('zh-CN')+' · '+r.hash_id+' · 源记录 '+BigInt(r.request_ref.source_record_index).toLocaleString('zh-CN')+'：'+BigInt(r[metrics[metricIndex]!]).toLocaleString('zh-CN')+' Token';
     const reading=chart.locator('..').locator('[aria-live]');
     try { await expect(reading).toHaveText(expected); }
     finally { records.push({width,metric:metrics[metricIndex],offset,index:i,bounds,api_row:r,expected,actual:await reading.innerText()}); }
     if(width===1920 && i===0) await chart.locator('..').screenshot({path:testInfo.outputPath(scenario+'-first-1920-'+metricIndex+'.png')});
    }
    if(width===1920||width===390)await chart.locator('..').screenshot({path:testInfo.outputPath(scenario+'-'+width+'-'+metricIndex+'.png')});
   }
   expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
  }
 }finally{fs.writeFileSync(testInfo.outputPath('pointer-records.json'),JSON.stringify(records,null,2));}
});

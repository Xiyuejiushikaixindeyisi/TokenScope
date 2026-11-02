import { test, expect } from '@playwright/test';
import fs from 'node:fs';
const fixturePath=process.env.TOKENSCOPE_SOURCE_LINK_FIXTURE;
test.beforeEach(()=>test.skip(!fixturePath,'fresh real-backend source fixture required'));
const fixture=()=>JSON.parse(fs.readFileSync(fixturePath!,'utf8'));
for(const width of [1440,390]) {
 test('UIR-02 keyboard focus preserves all fixed routes '+width,async({page})=>{
  const f=fixture(),s=f.user.scope.source,q=new URLSearchParams({run:s.base_run_id,appid:f.user.scope.appid,model:s.model_id});
  await page.setViewportSize({width,height:width===1440?1000:844});
  const routes=['users?run='+s.user_run_id+'&appid='+f.user.scope.appid,'users/ranking?run='+s.user_run_id,'ma','analysis?'+new URLSearchParams({binding:f.user.binding_id,task:f.user.task_id,direction:'low_hit',mode:'history'}),'settings?'+q,'overview?'+q,'requests?'+q];
  for(const route of routes){
   await page.goto('/#/'+route);await expect(page.locator('main')).toBeVisible();await page.waitForTimeout(600);
   if(route.startsWith('users?'))await expect(page.locator('.metric-grid')).toBeVisible();
   if(route.startsWith('analysis?'))await expect(page.locator('.solution-card').first()).toBeVisible();
   const url=page.url(),history=await page.evaluate(()=>window.history.length);
   const cards=await page.locator('.solution-card').count();
   await page.getByText('跳至内容',{exact:true}).focus();await page.keyboard.press('Enter');
   await expect(page.locator('main')).toBeFocused();expect(page.url()).toBe(url);
   expect(await page.evaluate(()=>window.history.length)).toBe(history);expect(await page.locator('.solution-card').count()).toBe(cards);
   await expect(page.getByText('页面不存在',{exact:true})).toHaveCount(0);
   await page.locator(width===1440?'.sidebar a':'.unified-mobile a').filter({hasText:'搜索与排行'}).click();await expect(page).toHaveURL(/users\/ranking(?:\?.*)?$/);await expect(page.getByRole('heading',{name:'搜索与排行',exact:true})).toBeVisible();await page.goBack();await expect(page).toHaveURL(url);await page.goForward();await expect(page).toHaveURL(/users\/ranking(?:\?.*)?$/);
  }
 });
 test('UIR-01 real curves match each exact sorted segment '+width,async({page,request})=>{
  const f=fixture(),s=f.user.scope.source;
  await page.setViewportSize({width,height:width===1440?1000:844});
  await page.goto('/#/users?run='+s.user_run_id+'&appid='+f.user.scope.appid);await expect(page.locator('.metric-grid')).toBeVisible();
  await page.getByLabel('分布纵轴').selectOption('share');await page.getByLabel('分布视图').selectOption('rank');
  const metrics=['json_tokens','prompt_tokens','ideal_compute_input_tokens'],colors=['#6c87a7','#4277e6','#098e80'];
  for(let i=0;i<3;i++){
   const card=page.locator('.distributions article').nth(i),chart=card.locator('.rank-chart svg');
   await expect(chart).toBeVisible();await expect(card).toContainText('纵轴：Token；横轴：请求排名');await expect(card).not.toContainText('纵轴：请求占比');
   expect(await chart.locator('line').count()).toBeGreaterThanOrEqual(5);await expect(chart.locator('path[stroke]')).toHaveAttribute('stroke',colors[i]!);
   const response=await request.get('/analysis-runs/'+s.base_run_id+'/requests?'+new URLSearchParams({appid:f.user.scope.appid,sort_by:metrics[i]!,sort_order:'desc',offset:'0',limit:'1000'}),{headers:{'X-TokenScope-Instance-Id':f.service_instance_id}});
   expect(response.ok()).toBeTruthy();const data=await response.json();
   await expect(card.locator('[aria-live]')).toContainText(BigInt(data.items[0][metrics[i]!]).toLocaleString('zh-CN')+' Token');
   await chart.focus();await page.keyboard.press('ArrowRight');await expect(card.locator('[aria-live]')).toContainText(data.items[1].hash_id);
   await expect(card.locator('[aria-live]')).toContainText(BigInt(data.items[1][metrics[i]!]).toLocaleString('zh-CN')+' Token');
   expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
  }
  await page.getByLabel('分布视图').selectOption('histogram');await expect(page.locator('.distributions')).toContainText('纵轴：请求占比');await expect(page.locator('.distributions svg[aria-label$="直方图"]')).toHaveCount(3);
  await page.getByLabel('辅助排名图（每段至多1000点）').check();await expect(page.locator('.rank-chart')).toHaveCount(1);
 });
}
for(const width of [1440,390]) test('UIR-01 controlled boundary: 1000 points, next segment, retry, zero and exact big integer '+width,async({page})=>{
 await page.setViewportSize({width,height:width===1440?1000:844});
 const f=fixture(),s=f.user.scope.source;let failures=0;
 await page.route('**/analysis-runs/*/requests?**',async route=>{
  const u=new URL(route.request().url());if(u.searchParams.get('limit')!=='1000')return route.continue();
  const response=await route.fetch(),data=await response.json(),offset=u.searchParams.get('offset')??'0';
  if(offset==='1000' && failures++===0)return route.fulfill({status:503,body:'retry'});
  const template=data.items[0]??(await (await page.request.get('/analysis-runs/'+s.base_run_id+'/requests?appid='+f.user.scope.appid,{headers:{'X-TokenScope-Instance-Id':f.service_instance_id}})).json()).items[0];
  data.offset=offset;data.total='1001';data.next_offset=offset==='0'?'1000':null;
  data.items=Array.from({length:offset==='0'?1000:1},(_,i)=>({...template,position:String(Number(offset)+i+1),request_ref:{...template.request_ref,source_record_index:String(Number(offset)+i+1)},hash_id:'boundary-'+(Number(offset)+i+1),json_tokens:offset==='0'?'90071992547409931':'0',prompt_tokens:offset==='0'?'90071992547409931':'0',ideal_compute_input_tokens:offset==='0'?'90071992547409931':'0'}));
  await route.fulfill({response,json:data});
 });
 await page.goto('/#/users?run='+s.user_run_id+'&appid='+f.user.scope.appid);await expect(page.locator('.metric-grid')).toBeVisible();await page.getByLabel('分布视图').selectOption('rank');
 const card=page.locator('.distributions article').first();await expect(card.locator('[aria-live]')).toContainText('90,071,992,547,409,931 Token');
 await card.getByRole('button',{name:'下一段'}).click();await expect(card.getByRole('alert')).toBeVisible();await card.getByRole('button',{name:'重读曲线'}).click();
 await expect(card.locator('[aria-live]')).toContainText('排名 #1,001');await expect(card.locator('[aria-live]')).toContainText('0 Token');
 await expect(card.getByRole('button',{name:'下一段'})).toBeDisabled();await card.getByRole('button',{name:'上一段'}).click();await expect(card.locator('[aria-live]')).toContainText('排名 #1 ·');
});



for(const width of [1440,390]) test('UIR-01 empty current segment '+width,async({page})=>{
 const f=fixture(),s=f.user.scope.source;await page.setViewportSize({width,height:width===1440?1000:844});
 await page.route('**/analysis-runs/*/requests?**',async route=>{
  if(new URL(route.request().url()).searchParams.get('limit')!=='1000')return route.continue();
  const response=await route.fetch(),data=await response.json();await route.fulfill({response,json:{...data,items:[],offset:'0',total:'0',next_offset:null}});
 });
 await page.goto('/#/users?run='+s.user_run_id+'&appid='+f.user.scope.appid);await expect(page.locator('.metric-grid')).toBeVisible();await page.getByLabel('分布视图').selectOption('rank');
 await expect(page.getByText('当前范围没有请求。',{exact:true})).toHaveCount(3);await expect(page.locator('.distributions .rank-chart svg')).toHaveCount(0);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});

for(const width of [1440,390]) test('UIR-01 real 1005 request segments '+width,async({page,request})=>{
 const f=fixture(),r=JSON.parse(fs.readFileSync(fixturePath!.replace('source-link-fixture.json','rank-segment-fixture.json'),'utf8'));
 await page.setViewportSize({width,height:width===1440?1000:844});await page.goto('/#/users?run='+r.user_run_id+'&appid=synthetic-app-1');
 await expect(page.locator('.metric-grid')).toBeVisible();await page.getByLabel('分布视图').selectOption('rank');
 for(const [i,metric] of ['json_tokens','prompt_tokens','ideal_compute_input_tokens'].entries()){
  const card=page.locator('.distributions article').nth(i);await expect(card).toContainText('当前段 1–1,000 / 共 1,005 条');
  await card.getByRole('button',{name:'下一段'}).click();await expect(card).toContainText('当前段 1,001–1,005 / 共 1,005 条');
  const response=await request.get('/analysis-runs/'+r.base_run_id+'/requests?'+new URLSearchParams({appid:'synthetic-app-1',sort_by:metric,sort_order:'desc',offset:'1000',limit:'1000'}),{headers:{'X-TokenScope-Instance-Id':f.service_instance_id}});
  expect(response.ok()).toBeTruthy();const data=await response.json();expect(data.items).toHaveLength(5);
  await expect(card.locator('[aria-live]')).toContainText('排名 #1,001');await expect(card.locator('[aria-live]')).toContainText(BigInt(data.items[0][metric]).toLocaleString('zh-CN')+' Token');
 }
 await page.locator('.distributions').screenshot({path:fixturePath!.replace('source-link-fixture.json','rank-segment-'+width+'.png')});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 for(const card of await page.locator('.distributions article').all()){await card.getByRole('button',{name:'上一段'}).click();await expect(card).toContainText('当前段 1–1,000 / 共 1,005 条');}
});

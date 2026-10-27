// Backend-owned recovery checks. No synthetic EventSource or fake server DTOs.
import { test, expect } from '@playwright/test';
import { execFileSync, spawn } from 'node:child_process';
import { readFileSync, openSync, closeSync } from 'node:fs';
const root='/home/zhangxiyue/TokenScope';
const artifact='artifacts/validation/monitoring/joint-v1';
test.beforeEach(()=>test.skip(process.env.TOKENSCOPE_JOINT!=='1','isolated joint state only'));
test('R1/J03: terminal before subscribe, expired log reset, 404 and real server crash/restart', async({page,request},info)=>{
  test.setTimeout(90000);
  const catalog=await(await request.get('/monitoring/catalog')).json();
  const keys=Array.from({length:6},(_,i)=>'joint-recovery-'+Date.now()+'-'+i);
  const records=[];
  for(const key of keys){
    const body={file_ref:'model-1.csv',model_id:'GLM-5.2',submission_key:key};
    const run=await(await request.post('/analysis-runs',{data:body})).json();
    records.push({instance:catalog.service_instance_id,request:body,submittedAt:new Date().toISOString(),runId:run.run_id,status:'queued'});
  }
  for(const key of keys) await expect.poll(async()=> (await(await request.get('/analysis-submissions/'+key)).json()).status,{timeout:60000}).toBe('completed');
  records.push({instance:catalog.service_instance_id,request:{file_ref:'model-1.csv',model_id:'GLM-5.2',submission_key:'never-accepted'},submittedAt:new Date().toISOString(),runId:'',status:'unconfirmed'});
  // Install real durable pending receipts before app starts, simulating a lost tab.
  await page.goto('/');
  await page.evaluate(async records=>new Promise<void>((resolve,reject)=>{const q=indexedDB.open('tokenscope-viewer-receipts-v1',1);q.onupgradeneeded=()=>q.result.createObjectStore('receipts');q.onsuccess=()=>{const db=q.result,tx=db.transaction('receipts','readwrite');for(const r of records)tx.objectStore('receipts').put(r,JSON.stringify([r.instance,r.request.submission_key]));tx.oncomplete=()=>{db.close();resolve();};tx.onerror=()=>reject(tx.error);};}),records);
  const trace:{url:string;status:number;at:number}[]=[];let active=0,max=0,posts=0,forced=false;
  page.on('response',r=>{if(r.url().includes('/analysis-submissions/'))trace.push({url:r.url(),status:r.status(),at:Date.now()});});
  page.on('request',r=>{if(r.method()==='POST')posts++;});
  await page.route('**/analysis-submissions/**',async route=>{active++;max=Math.max(max,active);try{const response=await route.fetch();const body=await response.body(),headers=response.headers(),status=response.status();await new Promise(r=>setTimeout(r,50));await route.fulfill({body,headers,status});}finally{active--;}});
  execFileSync('wsl.exe',['-d','Ubuntu-22.04','--',root+'/.venv/bin/python','-c',`from pathlib import Path; from tokenscope.monitoring.storage import ControlStore; from tokenscope.monitoring.events import PublicationEventReader; c=ControlStore(Path('${root}/${artifact}/state/control.sqlite3')); PublicationEventReader(c).prune(days=0)`],{windowsHide:true});
  await page.route('**/monitoring/events?**',route=>{if(!forced){forced=true;const u=new URL(route.request().url());u.searchParams.set('after',catalog.service_instance_id+':0');return route.continue({url:u.toString()});}return route.continue();});
  await page.goto('/#/submissions');await page.reload();for(const key of keys)await expect(page.locator('.signal').filter({hasText:key})).toContainText('completed');
  await expect(page.locator('.signal').filter({hasText:'never-accepted'})).toContainText('尚未确认');expect(max).toBeLessThanOrEqual(4);expect(posts).toBe(0);await expect.poll(()=>active).toBe(0);await page.unrouteAll({behavior:'wait'});
  // Stop only the exact independent process whose PID is recorded by our launcher.
  const log=readFileSync(new URL('../../../../'+artifact+'/server-fixed.log',import.meta.url),'utf8');const pid=log.match(/Started server process \[(\d+)\]/)![1]!;
  execFileSync('wsl.exe',['-d','Ubuntu-22.04','--','kill','-KILL',pid],{windowsHide:true});
  await expect(page.getByText('通知待连接',{exact:false})).toBeVisible({timeout:15000});
  const fd=openSync(new URL('../../../../'+artifact+'/server-restarted.log',import.meta.url),'w');
  const child=spawn('wsl.exe',['-d','Ubuntu-22.04','--cd',root,'--',root+'/.venv/bin/python','-m','tokenscope.cli','--input-root',artifact+'/inputs','--state-root',artifact+'/state','--asset-root',root,'serve','--host','0.0.0.0','--port','8186','--viewer-root','apps/viewer/dist'],{windowsHide:true,stdio:['ignore',fd,fd]});child.unref();closeSync(fd);
  await expect(page.getByText('通知已连接',{exact:false})).toBeVisible({timeout:25000});
  const after=await(await request.get('/monitoring/catalog')).json();expect(after.service_instance_id).toBe(catalog.service_instance_id);
  await page.reload();for(const key of keys)await expect(page.locator('.signal').filter({hasText:key})).toContainText('completed');
  const bad=await request.post('/analysis-runs',{headers:{'X-TokenScope-Instance-Id':'wrong-instance'},data:{file_ref:'model-1.csv',model_id:'GLM-5.2',submission_key:'wrong-instance-test'}});expect(bad.status()).toBe(409);
  await info.attach('recovery-trace',{body:JSON.stringify({trace,max,posts,forcedExpiredCursor:forced,instanceBefore:catalog.service_instance_id,instanceAfter:after.service_instance_id,crashedPid:pid}),contentType:'application/json'});
});
test('R1-03: real terminal SSE wins over delayed queued receipt HTTP response',async({page,request},info)=>{
  test.setTimeout(60000);let release:()=>void=()=>{};const gate=new Promise<void>(r=>release=r);let delayedStatus='';let key='';
  await page.route('**/analysis-submissions/**',async route=>{const response=await route.fetch();const body=await response.json();delayedStatus=body.status;await gate;await route.fulfill({response});});
  page.on('request',r=>{if(r.method()==='POST'&&r.url().endsWith('/analysis-runs'))key=r.postDataJSON().submission_key;});
  await page.goto('/#/submissions');await expect(page.getByText('通知已连接',{exact:false})).toBeVisible();await page.getByLabel('file_ref').fill('model-1.csv');await page.getByLabel('确认启动该文件的监控计算').check();await page.getByRole('button',{name:'提交监控任务',exact:true}).click();
  await expect.poll(()=>key).not.toBe('');await expect(page.locator('.signal').filter({hasText:key})).toContainText('completed',{timeout:45000});
  release();await page.unrouteAll({behavior:'wait'});await expect(page.locator('.signal').filter({hasText:key})).toContainText('completed');
  expect(['queued','running']).toContain(delayedStatus);expect((await(await request.get('/analysis-submissions/'+key)).json()).status).toBe('completed');
  await info.attach('late-get',{body:JSON.stringify({key,delayedStatus,final:'completed'}),contentType:'application/json'});
});

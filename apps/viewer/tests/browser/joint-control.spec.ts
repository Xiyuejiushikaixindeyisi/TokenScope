import {test,expect} from '@playwright/test';
test.beforeEach(()=>test.skip(process.env.TOKENSCOPE_JOINT!=='1','isolated joint only'));
test('J05 real rule CAS conflict retains draft and old snapshot; two tabs share current result',async({page,context,request},info)=>{
 const c=await(await request.get('/monitoring/catalog')).json(),item=c.items[0];const scope=`appid=${item.appid}&model=${encodeURIComponent(item.model_id)}`;
 const path=`/analysis-runs/${item.active_run_id}/view-snapshot?appid=${item.appid}`;const old=await(await request.get(path)).body();
 await page.goto('/#/settings?'+scope);await page.getByRole('button',{name:'新增阈值规则'}).click();await page.getByRole('combobox',{name:'指标',exact:true}).selectOption('request_count');await page.getByLabel('阈值',{exact:true}).fill('500');
 const saving=page.waitForRequest(r=>r.method()==='PUT'&&r.url().includes('/monitoring/threshold-rules'));await page.getByRole('button',{name:'保存阈值规则'}).click();const body=(await saving).postDataJSON();await expect(page.getByText('规则已保存，仅影响下一次运行。')).toBeVisible();
 const competing={...body,expected_revision:'1',threshold:'600'};expect((await request.put('/monitoring/threshold-rules',{data:competing})).status()).toBe(200);
 await page.getByLabel('阈值',{exact:true}).fill('700');await page.getByRole('button',{name:'保存阈值规则'}).click();await expect(page.getByText('规则版本冲突',{exact:false})).toBeVisible();await page.getByRole('button',{name:'重读规则列表'}).click();await expect(page.getByLabel('阈值',{exact:true})).toHaveValue('700');await page.getByRole('button',{name:'确认按新规则版本保存当前草稿'}).click();await expect(page.getByText('规则已保存，仅影响下一次运行。')).toBeVisible();
 expect(await(await request.get(path)).body()).toEqual(old);
 const second=await context.newPage();await second.goto('/#/overview?'+scope);await expect(second.locator('.metric-grid')).toBeVisible();await expect(second.getByText('当前范围：',{exact:false})).toContainText(item.active_run_id);await page.reload();await expect(page.getByText('request_count · 700 · 停用')).toBeVisible();await second.close();
 await info.attach('rule-cas',{body:JSON.stringify({rule:body.rule_id,versions:['1','2','3'],oldResultUnchanged:true,twoTabs:true}),contentType:'application/json'});
});
test('R1-04 native EventSource duplicate and conflicting terminal fault frames keep real receipt terminal',async({page,request},info)=>{
 test.setTimeout(60000);
 const key='joint-conflict-'+Date.now(),submitted={file_ref:'model-1.csv',model_id:'GLM-5.2',submission_key:key};
 const run=await(await request.post('/analysis-runs',{data:submitted})).json();await expect.poll(async()=> (await(await request.get('/analysis-submissions/'+key)).json()).status,{timeout:45000}).toBe('completed');
 const receipt=await(await request.get('/analysis-submissions/'+key)).json(), c=await(await request.get('/monitoring/catalog')).json();
 await page.goto('/');await page.evaluate(async record=>new Promise<void>(resolve=>{const q=indexedDB.open('tokenscope-viewer-receipts-v1',1);q.onsuccess=()=>{const db=q.result,tx=db.transaction('receipts','readwrite');tx.objectStore('receipts').put(record,JSON.stringify([record.instance,record.request.submission_key]));tx.oncomplete=()=>{db.close();resolve();};};}),{instance:c.service_instance_id,request:submitted,submittedAt:new Date().toISOString(),runId:run.run_id,status:'completed',receipt});
 const seq=BigInt(c.cursor.split(':').at(-1)!),event={service_instance_id:c.service_instance_id,view_schema_version:'1',run_id:run.run_id,model_id:'GLM-5.2',event_seq:String(seq+1n),status:'failed',error_code:'JOINT_INJECTED_CONFLICT',finished_at:receipt.finished_at};
 const duplicate={...event,event_seq:String(seq),status:'completed',error_code:null};
 const frame=(e:Record<string,unknown>)=>`id: ${e.service_instance_id}:${e.event_seq}\nevent: run_terminal\ndata: ${JSON.stringify(e)}\n\n`;
 await page.route('**/monitoring/events?**',r=>r.fulfill({contentType:'text/event-stream',body:frame(duplicate)+frame(duplicate)+frame(event)}));
 await page.goto('/#/submissions');await page.reload();const row=page.locator('.signal').filter({hasText:key});await expect(row).toContainText('completed');await expect(row).toContainText('终态冲突');
 await info.attach('native-sse-fault',{body:JSON.stringify({receiptStatus:receipt.status,duplicateCursor:c.cursor,injected:event,final:'completed',kind:'real_receipt_plus_controlled_native_SSE_fault_frames'}),contentType:'application/json'});
});

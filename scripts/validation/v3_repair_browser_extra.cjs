const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('../../apps/viewer/node_modules/playwright');
const input=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);fs.mkdirSync(out,{recursive:false});
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[],writes=[],cases=[];
page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(!['GET','HEAD'].includes(r.method()))writes.push(r.url());});
try {for(const name of ['synthetic-constant-clock','synthetic-l5-large-int','synthetic-cancelled']){
 const link=JSON.parse(fs.readFileSync(path.join(input,name+'-link.json'),'utf8'));
 await page.goto(link.url);await page.waitForFunction(task=>document.querySelector('[aria-label="历史报告"]')?.value===task,link.task);
 await page.getByText(/合成数据验证 · 小样本分析/).first().waitFor();
 if(name.includes('constant')) {if(await page.getByRole('heading',{name:'固定 session_clock，稳定公共前缀'}).count())throw Error('FALSE_CLOCK');}
 if(name.includes('l5')){const card=page.locator('article[data-rule="L5"]');await card.waitFor();if(await card.count()!==1)throw Error('DUPLICATE_L5');await card.getByRole('button').click();await page.locator('.example-block').first().waitFor();if(await page.locator('.example-block').count()>3)throw Error('TOO_MANY_EXAMPLES');if(!(await page.locator('.diff-grid').innerText()).includes('900719925474099312345'))throw Error('INTEGER_LOSS');}
 if(name.includes('cancelled')){const card=page.locator('article').filter({has:page.getByRole('heading',{name:'固定 session_clock，稳定公共前缀'})});await card.waitFor();if(!(await card.innerText()).includes('未评估'))throw Error('MISSING_UNEVALUATED');if((await card.innerText()).includes('0个百分点'))throw Error('FAKE_ZERO');}
 await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});cases.push(name);
}if(errors.length||writes.length)throw Error(JSON.stringify({errors,writes}));fs.writeFileSync(path.join(out,'PASS.json'),JSON.stringify({cases,errors,writes,real_http:true},null,2),{flag:'wx'});
}catch(e){fs.writeFileSync(path.join(out,'FAIL.json'),JSON.stringify({error:String(e),errors,writes,text:await page.locator('body').innerText()},null,2),{flag:'wx'});await page.screenshot({path:path.join(out,'failure.png'),fullPage:true});throw e;}finally{await browser.close();}})();

const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('../../apps/viewer/node_modules/playwright');
const root = process.cwd(), input = path.join(root, process.argv[2]), out = path.join(root, process.argv[3]);
fs.mkdirSync(out, {recursive:false});
const errors = [], writes = [], cases = [];
(async () => {
 const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page = await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror', e => errors.push(String(e)));
 page.on('request', r => { if (!['GET','HEAD'].includes(r.method())) writes.push([r.method(),r.url()]); });
 try {
  for (const group of ['BUS01','BUS02','BUS03','BUS04','BUS05']) {
   const link = JSON.parse(fs.readFileSync(path.join(input,group+'-link.json'),'utf8'));
   const report = JSON.parse(fs.readFileSync(path.join(input,group+'-report.json'),'utf8'));
   await page.goto(link.url);
   await page.waitForFunction(task => document.querySelector('[aria-label="历史报告"]')?.value === task, link.task);
   await page.getByRole('heading',{name:'固定 session_clock，稳定公共前缀'}).waitFor();
   await page.getByText('合成数据验证 · 非生产业务收益',{exact:true}).first().waitFor();
   if (await page.getByLabel('业务应用').inputValue() !== link.appid) throw Error('APPID_MISMATCH');
   if (!(await page.getByLabel('模型服务').innerText()).includes(link.model)) throw Error('MODEL_MISMATCH');
   if (await page.locator('.sample-diagnostics').count()) throw Error('PARALLEL_MODULE');
   const clock = report.recommendations.find(r=>r.finding.rule_version==='clock-3.1');
   const card = page.locator('article').filter({has:page.getByRole('heading',{name:'固定 session_clock，稳定公共前缀'})});
   const w=clock.windows[0], n=BigInt(w.improvement_pp.numerator),d=BigInt(w.improvement_pp.denominator), rounded=((n<0n?-n:n)*100n+d/2n)/d;
   const value=(n<0n?'-':n>0n?'+':'')+`${rounded/100n}.${String(rounded%100n).padStart(2,'0')}`.replace(/\.00$/,'').replace(/(\.\d)0$/,'$1');
   if (!(await card.innerText()).includes(value+'个百分点')) throw Error('RATE_MISMATCH '+value);
   await card.getByText(/请求 A：/).waitFor();
   await page.screenshot({path:path.join(out,group+'-cards.png'),fullPage:true});
   await card.getByRole('button',{name:/查看证据与改法/}).click();
   await page.locator('.before-after').waitFor();
   if (!(await page.locator('.before-after').innerText()).includes('NORMALIZED')) throw Error('MISSING_EDIT');
   if (!await page.locator('.diff-grid mark').count()) throw Error('MISSING_HIGHLIGHT');
   await page.screenshot({path:path.join(out,group+'-clock.png'),fullPage:true});
   await page.reload(); await page.locator('.before-after').waitFor();
   await page.getByRole('button',{name:/返回卡片列表/}).click();
   const diff = page.locator('article[data-rule="L4"]');
   if (await diff.count()) {
    if (await diff.count() !== 1) throw Error('L4_DUPLICATE_CARDS');
    await diff.getByRole('button').click();
    await page.locator('.example-block').first().waitFor();
    if (await page.locator('.example-block').count() > 3) throw Error('TOO_MANY_EXAMPLES');
    await page.getByRole('button',{name:/返回卡片列表/}).click();
   }
   cases.push({group,task:link.task,rate:value});
  }
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
  if (await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth)) throw Error('MOBILE_OVERFLOW');
  for (const target of ['users','users/ranking','ma']) {
   await page.goto('http://127.0.0.1:18002/#/'+target);
   await page.getByRole('heading',{name:target==='users'?'用户 Token 监控':target==='users/ranking'?'搜索与排行':'MA集群 Token 监控',exact:true}).waitFor();
  }
  if (errors.length || writes.length) throw Error(JSON.stringify({errors,writes}));
  fs.writeFileSync(path.join(out,'PASS.json'),JSON.stringify({cases,errors,writes,real_http:true},null,2),{flag:'wx'});
 } catch(e) {
  await page.screenshot({path:path.join(out,'failure.png'),fullPage:true});
  fs.writeFileSync(path.join(out,'FAIL.json'),JSON.stringify({error:String(e),errors,writes,cases,text:await page.locator('body').innerText()},null,2),{flag:'wx'});throw e;
 } finally {await browser.close();}
})();

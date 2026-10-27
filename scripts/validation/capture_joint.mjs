import {chromium} from '../../apps/viewer/node_modules/@playwright/test/index.mjs';
import {writeFileSync} from 'node:fs';
const dir='artifacts/validation/monitoring/joint-v1/';
const b=await chromium.launch({executablePath:process.env.TOKENSCOPE_BROWSER_EXECUTABLE,headless:true});
try{const page=await b.newPage({viewport:{width:1440,height:1000}});const external=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:8186/'))external.push(r.url());});await page.goto('http://127.0.0.1:8186/#/overview');await page.locator('.metric-grid').waitFor();await page.screenshot({path:dir+'desktop.png',fullPage:true});await page.setViewportSize({width:390,height:844});await page.screenshot({path:dir+'mobile.png',fullPage:true});writeFileSync(dir+'visual.json',JSON.stringify({browser:b.version(),external,width:390,scrollWidth:await page.evaluate(()=>document.documentElement.scrollWidth),secure:await page.evaluate(()=>isSecureContext)},null,2));}finally{await b.close();}

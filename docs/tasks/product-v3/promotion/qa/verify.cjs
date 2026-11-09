const { chromium } = require('C:/Users/ALIENWARE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const {pathToFileURL}=require('url');
(async()=>{
 const root=path.resolve(__dirname,'..');
 const context=await chromium.launchPersistentContext(path.join(__dirname,'browser-profile'),{executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,viewport:{width:1440,height:1000},deviceScaleFactor:1,args:['--disable-background-networking']});
 const page=await context.newPage();const errors=[],network=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 const results={};
 try{
 await page.goto(pathToFileURL(path.join(root,'TokenScope_V2_Overview.html')).href);
 await page.screenshot({path:path.join(__dirname,'desktop-hero.png')});
 results.desktopOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const ids=await page.locator('[id]').evaluateAll(els=>els.map(e=>e.id));
 results.duplicateIds=ids.filter((x,i)=>ids.indexOf(x)!==i);
 results.brokenAnchors=await page.locator('a[href^="#"]').evaluateAll(els=>els.filter(e=>!document.getElementById(e.hash.slice(1))).map(e=>e.hash));
 results.tabs=[];
 for(let i=0;i<6;i++){await page.locator('#tab-'+i).click();results.tabs.push({step:i,visible:await page.locator('#panel-'+i).isVisible(),count:await page.locator('[role=tabpanel]:visible').count()})}
 await page.locator('#tab-2').click();await page.locator('#journey').scrollIntoViewIfNeeded();
 await page.locator('.workflow').screenshot({path:path.join(__dirname,'desktop-workflow.png')});
 await page.locator('#tab-2').focus();await page.keyboard.press('ArrowRight');results.keyboardTab=await page.locator('#tab-3').getAttribute('aria-selected');
 await page.locator('#cases').screenshot({path:path.join(__dirname,'desktop-cases.png')});
 await page.locator('#cpu').screenshot({path:path.join(__dirname,'desktop-cpu.png')});
 await page.locator('#slo').screenshot({path:path.join(__dirname,'desktop-slo.png')});
 await page.locator('#ma').screenshot({path:path.join(__dirname,'desktop-ma.png')});
 await page.emulateMedia({media:'print'});results.printPanels=await page.locator('[role=tabpanel]:visible').count();await page.emulateMedia({media:'screen'});
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(__dirname,'mobile-hero.png')});
 results.mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 await page.locator('#tab-2').click();await page.locator('.workflow').screenshot({path:path.join(__dirname,'mobile-workflow.png')});
 const links=await page.locator('a[href]').evaluateAll(els=>els.map(e=>e.getAttribute('href')).filter(h=>!h.startsWith('#')&&!/^https?:/.test(h)));
 results.missingLocalLinks=links.filter(h=>!fs.existsSync(path.resolve(root,h)));
 results.networkRequests=network;results.pageErrors=errors;
 fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));
 if(results.desktopOverflow||results.mobileOverflow||errors.length||network.length||results.brokenAnchors.length||results.duplicateIds.length||results.missingLocalLinks.length||results.printPanels!==6||results.keyboardTab!=='true'||results.tabs.some(t=>!t.visible||t.count!==1))throw Error('Verification failed');
 }finally{await context.close()}
})();

import {test,expect} from '@playwright/test';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
test('R2-10 real streaming gzip proxy preserves decoded NDJSON digest',async({page},info)=>{
 test.skip(process.env.TOKENSCOPE_JOINT_GZIP!=='1','explicit real gzip proxy only');
 await page.goto('/#/overview');await expect(page.locator('.metric-grid')).toBeVisible();
 await page.evaluate(()=>Object.defineProperty(window,'showSaveFilePicker',{value:undefined,configurable:true}));
 const response=page.waitForResponse(r=>r.url().includes('/requests/export?'));
 const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'导出 NDJSON'}).click();
 const r=await response;expect(r.headers()['content-encoding']).toBe('gzip');expect(r.headers()['content-length']).toBeUndefined();
 const d=await downloaded;await expect(page.getByRole('status')).toContainText('SHA256 与记录数一致');const path=info.outputPath('gzip-export.ndjson');await d.saveAs(path);
 const bytes=readFileSync(path),lines=bytes.toString('utf8').trimEnd().split('\n');const summary=JSON.parse(lines.at(-1)!);
 expect(summary.request_lines_sha256).toBe(createHash('sha256').update(lines.slice(1,-1).join('\n')+'\n').digest('hex'));
 await info.attach('gzip',{body:JSON.stringify({headers:r.headers(),decodedBytes:bytes.length,rows:summary.actual_rows,sha:summary.request_lines_sha256}),contentType:'application/json'});
});

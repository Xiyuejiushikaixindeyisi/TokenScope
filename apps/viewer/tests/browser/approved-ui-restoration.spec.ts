import { test, expect } from '@playwright/test';
const names=['用户监控','搜索与排行','异常分析','MA集群监控'];
test.beforeEach(()=>test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1','isolated real backend required'));
for(const width of [1440,390]) test(`approved four-entry shell, legacy functionality and history ${width}`,async({page})=>{
 await page.setViewportSize({width,height:width===1440?1000:844});
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const route of ['users','users/ranking','analysis','ma','settings','overview','requests','distributions','signals','submissions','unknown']) {
  await page.goto('/#/'+route);
  const nav=page.locator(width===1440?'.sidebar':'.unified-mobile');
  await expect(nav.locator('a')).toHaveText(names);
  if(width===390) expect((await nav.boundingBox())!.height).toBeLessThan(100);
  await expect(nav.locator('a[aria-current=page]')).toHaveCount(1);
  await expect(page.locator('.sidebar-bottom')).not.toContainText('V1');
  await expect(page.locator('main')).toBeVisible();
  if(route==='settings') await expect(page.getByRole('heading',{name:'运行设置',exact:true})).toBeVisible();
  await page.reload();await expect(nav.locator('a')).toHaveText(names);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 }
 await page.goto('/#/users');await page.goto('/#/ma');await page.goBack();await expect(page).toHaveURL(/#\/users$/);await page.goForward();await expect(page).toHaveURL(/#\/ma$/);
 expect(errors).toEqual([]);
});

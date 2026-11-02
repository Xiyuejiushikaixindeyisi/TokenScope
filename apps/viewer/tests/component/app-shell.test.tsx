import { render, screen, cleanup } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import { AppShell } from '../../src/components/AppShell';
afterEach(cleanup);
it.each(['users','users/ranking','analysis','ma','settings','overview','requests','distributions','signals','submissions','unknown'])('keeps approved four entries for %s without replacing the child function', page => {
 const {container}=render(<AppShell page={page}><main><h1>功能内容</h1></main></AppShell>);
 const expected=['用户监控','搜索与排行','异常分析','MA集群监控'];
 for(const scope of ['.sidebar','.unified-mobile']) {
  const links=Array.from(container.querySelectorAll(`${scope} a`));
  expect(links.map(a=>a.textContent)).toEqual(expected);
  expect(links.filter(a=>a.getAttribute('aria-current')==='page')).toHaveLength(1);
  expect(links.every(a=>a.querySelector('svg'))).toBe(true);
 }
 expect(screen.getByRole('heading',{name:'功能内容'})).toBeVisible();
 expect(container.textContent).not.toContain('V1监控');
});

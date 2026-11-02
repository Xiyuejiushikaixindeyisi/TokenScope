import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { AppShell } from '../../src/components/AppShell';
import { RankChart } from '../../src/features/requests/Requests';
import type { Dto } from '../../src/api/types';
afterEach(cleanup);
it('skip focuses main without changing fixed route or history', () => {
 window.history.replaceState(null,'','#/users?run=fixed&appid=orders');
 const scroll=vi.fn(); HTMLElement.prototype.scrollIntoView=scroll;
 render(<AppShell page="users"><main id="main">固定报告</main></AppShell>);
 const before=window.location.href, length=window.history.length;
 fireEvent.click(screen.getByText('跳至内容'));
 expect(document.activeElement).toBe(screen.getByRole('main'));
 expect(window.location.href).toBe(before);expect(window.history.length).toBe(length);expect(scroll).toHaveBeenCalled();
});
const page=(values:string[],offset='0')=>({offset,total:(BigInt(offset)+BigInt(values.length)).toString(),items:values.map((n,i)=>({position:(BigInt(offset)+BigInt(i)+1n).toString(),hash_id:'request-'+i,request_ref:{source_record_index:String(i+1)},json_tokens:n,prompt_tokens:n,ideal_compute_input_tokens:n}))} as Dto<'RequestsPage'>);
it.each(['json_tokens','prompt_tokens','ideal_compute_input_tokens'] as const)('rank has Token/rank axes, grid and exact current segment values: %s', metric=>{
 const {container}=render(<RankChart page={page(['90071992547409931','0'],'1000')} metric={metric}/>);
 expect(screen.getByRole('img').textContent).toContain('Token');expect(screen.getByRole('img').textContent).toContain('请求排名');
 expect(container.querySelectorAll('line').length).toBeGreaterThanOrEqual(5);
 expect(container.textContent).toContain('1,001');expect(container.textContent).toContain('90,071,992,547,409,931');
 fireEvent.keyDown(screen.getByRole('img'),{key:'ArrowRight'});
 expect(container.querySelector('[aria-live]')).toHaveTextContent('排名 #1,002'); expect(container.querySelector('[aria-live]')).toHaveTextContent('0 Token');
 expect(container.textContent).not.toContain('精确值见下表');
});
it.each([{values:[]},{values:['0']},{values:['5']}])('rank handles empty or single point ',({values})=>{
 const {container}=render(<RankChart page={page(values)} metric="json_tokens"/>);
 expect(container.innerHTML).not.toMatch(/NaN|Infinity/);
 if(!values.length) expect(container.textContent).toContain('没有请求');
 else expect(container.querySelector('circle')).not.toBeNull();
});

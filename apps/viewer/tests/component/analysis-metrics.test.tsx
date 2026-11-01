import { render, screen } from '@testing-library/react';
import { it, expect } from 'vitest';
import { Metrics } from '../../src/features/analysis/Reports';
import { loadReport } from '../../src/features/analysis/model';
import { allTasks, low, token, entry, client } from '../unit/analysis/recommendation-fixtures';

it('low-hit benefits focus on affected requests and hit rate only', async () => {
    const data = await loadReport(client(low).api, entry(low), 'low_hit');
    const { container } = render(<Metrics card={data.cards.find(x => x.kind === 'recommendation')!}/>);
    expect(screen.getByText('影响请求')).toBeInTheDocument(); expect(screen.getByText('预期命中率提升')).toBeInTheDocument(); expect(container).not.toHaveTextContent('Token');
});
it('Token P decrease and C increase remain distinct and use opposite visual signals', async () => {
    const t = allTasks.find(x => String((x.report.scope as Record<string, unknown>).appid).startsWith('boundary-'))!;
    const card = (await loadReport(client(t).api, entry(t), 'token_content')).cards[0]!;
    const { container } = render(<Metrics card={card}/>);
    expect(screen.getByText('预期输入 Token减少')).toBeInTheDocument(); expect(screen.getByText('预期计算 Token增加')).toBeInTheDocument();
    expect(container.querySelector('.good')).toHaveTextContent('−4'); expect(container.querySelector('.caution')).toHaveTextContent('+124');
});
it('zero impact stays zero and missing evaluation never becomes zero', async () => {
    const data = await loadReport(client(token).api, entry(token), 'token_content');
    const zero = data.cards.find(x => x.affected === '0')!, missing = data.cards.find(x => x.affected === null)!;
    const { container, rerender } = render(<Metrics card={zero}/>); expect(container).toHaveTextContent('0条'); expect(container).not.toHaveTextContent('尚未评估');
    rerender(<Metrics card={missing}/>); expect(container).toHaveTextContent('待评估'); expect(container).toHaveTextContent('业务依据'); expect(container.querySelectorAll('.good')).toHaveLength(0);
});

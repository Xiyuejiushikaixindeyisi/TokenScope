"""Isolated catalogue gate only; no production requests or running service writes."""
import hashlib
import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from fastapi.testclient import TestClient
from tokenscope.monitoring.service import MonitoringService
from tokenscope.errors import TokenScopeError

HERE = Path(__file__).resolve().parent
WORK = HERE / 'isolation-fixture'
WORK.mkdir(exist_ok=False)
(WORK / 'inputs').mkdir()
service = MonitoringService(WORK / 'inputs', WORK / 'state')
fixture = runpy.run_path(str(ROOT / 'tests/integration/monitoring/test_user_discovery_defaults.py'))
app, headers, publish = fixture['context'].__wrapped__(service)
model = fixture['MODELS'][1]
old = publish(model, {'existing.fixture.glm': [50000, 50000]})
old_folder = service.state_root / 'runs' / old[2]
def hashes():
    return {str(p.relative_to(old_folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in old_folder.rglob('*') if p.is_file()}
baseline_hashes = hashes()
with TestClient(app) as client:
    def catalog():
        response = client.get('/monitoring/user-v2/runs', headers=headers)
        response.raise_for_status()
        return response.json()['entries']
    before = catalog()
    new = publish(model, {'demo.synthetic.icsl.glm52.cch.v1': [50000, 50000]})
    after = catalog()
    # Exact selection semantics of UserMonitor.refreshDirectory for no run/appid.
    def first_default(entries):
        return next(e for e in entries if e['appid'] is not None and e['is_default'])
    old_after = next(e for e in after if e['source']['user_run_id'] == old[0])
    custom_name_error = None
    try:
        app.state.user.validate_name('ICSL-SYNTHETIC-GLM52', 'GLM-5.2')
    except TokenScopeError as exc:
        custom_name_error = str(exc)
    result = {
        'scope': 'two small pre-sealed synthetic catalogue fixtures; not 80-request data or browser E2E',
        'state_root': str(service.state_root),
        'before': before, 'after': after,
        'bare_entry_before': first_default(before)['appid'],
        'bare_entry_after': first_default(after)['appid'],
        'bare_entry_unchanged': first_default(before)['appid'] == first_default(after)['appid'],
        'existing_group_default_preserved': old_after['is_default'],
        'existing_sealed_files_unchanged': baseline_hashes == hashes(),
        'custom_common_name_error': custom_name_error,
        'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [
            'src/tokenscope/user_monitoring/discovery.py',
            'src/tokenscope/user_monitoring/service.py',
            'apps/viewer/src/features/v2/UserMonitor.tsx']},
    }
(HERE / 'isolation-gate-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ('before','after','source_sha256')}, ensure_ascii=False, indent=2))
assert result['existing_group_default_preserved'] and result['existing_sealed_files_unchanged']
assert not result['bare_entry_unchanged'], 'Unexpected behavior requires review'
assert custom_name_error is not None

"""Append the demo using existing HTTP endpoints, preserve pre-existing reports."""
import hashlib,json,shutil,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'src'))
from tokenscope.analysis_common.execution_v2 import RequestV2,RuntimeV2,SelectionV2,SubmissionV2
from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.plugins import BudgetSpec,PluginSelection
from tokenscope.analysis_common.wire import to_wire
HERE=Path(__file__).resolve().parent/'revision3';OUT=HERE/'delivery';BASE='http://127.0.0.1:18002'
def call(path,body=None,headers=None):
    req=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json',**(headers or {})})
    with urllib.request.urlopen(req,timeout=120) as r:return json.load(r)
cap=call('/diagnostics/v2/capabilities');instance=cap['service_instance_id']
UH={'X-TokenScope-Instance-Id':instance};DH={'X-TokenScope-Service-Instance':instance}
def save(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
def catalogue():return call('/monitoring/user-v2/runs?limit=1000',headers=UH)
before=catalogue();save('existing-user-catalog-before.json',before)
before_diag=call('/diagnostics/v2/catalog?limit=100',headers=DH);save('existing-diagnostic-catalog-before.json',before_diag)
assert all(e.get('appid')!='com.huawei.icsl.base' for e in before['entries'])
manifest=json.loads((OUT/'manifest.json').read_text());assert hashlib.sha256((OUT/'icsl_glm52_cch_102.csv').read_bytes()).hexdigest()==manifest['csv_sha256']
dest=HERE.parent/'local/inputs/icsl-cch-v3';dest.mkdir(exist_ok=False);shutil.copy2(OUT/'icsl_glm52_cch_102.csv',dest)
started=time.perf_counter()
receipt=call('/monitoring/user-v2/runs',{'submission_key':'icsl-glm52-v3-monitor','file_ref':'icsl-cch-v3/icsl_glm52_cch_102.csv','common_name':'GLM-V5.2','model_id':'GLM-5.2'},UH)
save('monitor-submit.json',receipt);print('MONITOR',receipt,flush=True)
def wait(path,header,key,terminal):
    for _ in range(1800):
        result=call(path,headers=header)
        if result[key] in terminal:return result
        time.sleep(1)
    raise RuntimeError('bounded wait exhausted')
receipt=wait('/monitoring/user-v2/runs/'+receipt['user_run_id'],UH,'state',{'ready','empty','failed','interrupted'})
save('monitor-result.json',receipt);assert receipt['state']=='ready',receipt
opts=RuntimeV2(token_selection=PluginSelection(rule_ids=('T2','T3','T4'),budget=BudgetSpec(max_request_bytes=1048576,max_units=10000,max_comparison_bytes=2097152,max_depth=64,max_candidates=1000,max_encoding_calls=100)),candidate_limit=2,pilot_limit=8,max_source_requests=102,max_source_bytes=64*1024*1024,max_findings=400,max_retained_bytes=96*1024*1024,max_comparisons=1000,max_experiments=1,max_combinations=0,max_encoding_calls=400,max_plan_bytes=64*1024*1024)
request=RequestV2(source=SourceSelection(source_kind='user_v2',user_run_id=receipt['user_run_id'],appid=manifest['appid'],expected_index_revision=receipt['index_revision']),selection=SelectionV2(reason_codes=('low_hit',),enable_low_hit=True,enable_token_content=False),reason_note='ICSL编码Agent前缀复用分析',submission_key='icsl-glm52-v3-analysis')
payload=to_wire(SubmissionV2(request=request,options=opts));save('delivery/diagnostic-submission-local.json',payload)
task=call('/diagnostics/v2/tasks',payload,DH);save('diagnostic-submit.json',task);print('DIAGNOSTIC',task,flush=True)
task=wait('/diagnostics/tasks/'+task['task_id'],DH,'status',{'ready','partial','failed','empty','interrupted'});save('diagnostic-result.json',task)
assert task['status'] in ('ready','partial'),task
tid=task['task_id'];report=call('/diagnostics/tasks/'+tid+'/report',headers=DH);save('diagnostic-report.json',report)
def items(kind):
    out=[]
    for offset in range(0,10000,100):
        rows=call(f'/diagnostics/tasks/{tid}/items/{kind}?offset={offset}&limit=100',headers=DH)['items'];out+=rows
        if len(rows)<100:return out
    raise RuntimeError('pagination bound')
ev=items('evaluation');findings=items('finding');optim=items('optimization');save('evaluations.json',ev);save('findings.json',findings);save('optimizations.json',optim)
after=catalogue();save('existing-user-catalog-after.json',after)
old_map={(e['source']['user_run_id'],e['appid']):e for e in before['entries']};after_map={(e['source']['user_run_id'],e['appid']):e for e in after['entries']}
assert all(after_map.get(k)==v for k,v in old_map.items()),'existing catalogue entry changed'
old_diag_after=call('/diagnostics/v2/catalog?limit=100',headers=DH);save('existing-diagnostic-catalog-after.json',old_diag_after)
old_ids={x['task_id'] for x in before_diag['items']};assert old_ids<={x['task_id'] for x in old_diag_after['items']}
oldroot=ROOT/'artifacts/reviews/hv2-repair-20261103/final-default/state';baseline=json.loads((HERE.parent/'existing-original-sha256.json').read_text());assert all(hashlib.sha256((oldroot/p).read_bytes()).hexdigest()==sha for p,sha in baseline.items())
summary={'service_instance_id':instance,'monitor':receipt,'task':task,'seconds':time.perf_counter()-started,'old_user_entries_preserved':len(old_map),'old_diagnostic_entries_preserved':len(old_ids),'original_state_files_preserved':len(baseline),'finding_rules':{r:sum(x['data'].get('rule_id')==r for x in findings) for r in ('L1','L2','L3','L4','L5')},'evaluations':ev,'optimizations':optim}
save('acceptance-backend.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('evaluations','optimizations')},ensure_ascii=False),flush=True)

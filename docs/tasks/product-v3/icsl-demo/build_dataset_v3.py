"""Deterministic fictitious coding workload; measured using pinned GLM encoding."""
import csv, hashlib, json, random, resource, statistics, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'src'))
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.models import ModelEncoder
from tokenscope.encoding.batch import EncodingBatchService
from tokenscope.monitoring.simulation import PrefixLedger, FullBlockStrategy

HERE=Path(__file__).resolve().parent/'revision3'; OUT=HERE/'delivery';OUT.mkdir(parents=True,exist_ok=True)
APPID='com.huawei.icsl.base'
settings=DEFAULT_SETTINGS['GLM-5.2']; assets=AssetRegistry(ROOT).load('GLM-5.2')
enc=ModelEncoder(assets,settings);batch=EncodingBatchService(enc)
def raw(body):return json.dumps(body,ensure_ascii=False,separators=(',',':'))
tools=[{'type':'function','function':{'name':n,'description':d,'parameters':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}}} for n,d in [('inspect_module','Inspect the named module and its test contract.'),('propose_patch','Propose a reviewable patch without changing production data.'),('review_tests','Review unit tests and explain missing edge cases.')]]
def module(n):
    domains=['invoice','shipment','inventory','refund','reservation','catalog','pricing','account']
    domain=domains[n%len(domains)]; lim=11+n%79
    return f'''\nModule {n}: {domain} consistency contract\nThe component {domain}_service_{n} validates a command before publishing an event. All amounts use integer minor units. Replaying a committed command must return the existing result. Validation errors must not mutate the journal. The caller supplies a stable command identity.\n```python\nclass {domain.title()}Policy{n}:\n    limit = {lim}\n    def validate(self, command, snapshot):\n        if command.quantity <= 0:\n            raise ValueError("positive quantity required")\n        if command.quantity > self.limit:\n            return {{"accepted": False, "reason": "quota"}}\n        previous = snapshot.find(command.identity)\n        if previous is not None:\n            return previous\n        return {{"accepted": True, "quantity": command.quantity}}\n\ndef test_{domain}_policy_{n}(fixture):\n    policy = {domain.title()}Policy{n}()\n    outcome = policy.validate(fixture.command, fixture.snapshot)\n    assert outcome["accepted"] is True\n    assert fixture.snapshot.write_count == 0\n```\nReview requirements: verify boundary quantities, duplicate identities, empty snapshots, concurrent submissions and rejected commands. Preserve existing public return fields. Introduce new assertions before changing behavior. Document the smallest safe patch and rollback conditions. Module {n} belongs to the repository reference index.\n'''
pool=''.join(module(n) for n in range(500))
intro='You are a Claude agent working on the ICSL codebase. Preserve business correctness and propose reviewable patches.\n'
def ids(v):return batch.encode_batch([raw(v)])[0].prompt_ids
def lcp(x,y):
    for i,(a,b) in enumerate(zip(x,y)):
        if a!=b:return i
    return min(len(x),len(y))
def fit(text,target,measure):
    lo,hi=0,len(text)
    while lo<hi:
        mid=(lo+hi)//2
        if measure(text[:mid])<target:lo=mid+1
        else:hi=mid
    return text[:lo]

import uuid
started=time.perf_counter();rng=random.Random(20261105)
sizes=[2]*40+[1]*22;rng.shuffle(sizes)
conversations=[c for c,n in enumerate(sizes) for _ in range(n)]
codes=rng.sample(range(16**5),62)
def body(shared,i,tail,header=True):
    line=f'x-anthropic-billing-header: cc_entrypoint=sdk-py; cch={codes[conversations[i]]:05x};\n' if header else ''
    return {'model':'GLM-5.2','messages':[{'role':'system','content':line+intro+shared},{'role':'user','content':f'Review request {i+1}: inspect the code changes and propose regression tests.\n'+tail}], 'tools':tools,'enable_thinking':False}
shared=fit(pool,25620,lambda s:lcp(ids(body(s,0,'',False)),ids(body(s,1,'',False))))
targets=[round(rng.gauss(28000,520)) for _ in range(102)]
targets=[v-round(statistics.mean(targets)-28000) for v in targets]
records=[];before_ids=[];after_ids=[];details=[]
for i,target in enumerate(targets):
    tail_pool=''.join(module(1000+i*9+j) for j in range(20))
    empty_len=len(ids(body(shared,i,'')))
    tail=fit(tail_pool,target-empty_len,lambda t:len(enc.full.encode(t,add_special_tokens=False).ids))
    v=body(shared,i,tail);before=ids(v);after=ids(body(shared,i,tail,False))
    records.append(v);before_ids.append(before);after_ids.append(after)
    details.append({'index':i,'conversation':conversations[i],'cch':f'{codes[conversations[i]]:05x}','prompt_before':len(before),'prompt_after':len(after),'target':target})
    if i%20==0:print('generated',i,'tokens',len(before),flush=True)
def replay(rows,label):
    ledger=PrefixLedger(HERE/f'calibration-{label}-{time.time_ns()}.sqlite3');strategy=FullBlockStrategy(settings,assets.identity,ledger)
    hits=[strategy.process(APPID,row).hit_tokens for row in rows];ledger.close();total=sum(map(len,rows))
    return {'p':total,'h':sum(hits),'c':total-sum(hits),'rate':sum(hits)/total,'per_request_hits':hits}
before=replay(before_ids,'before');after=replay(after_ids,'after');print('RATES',before['rate'],after['rate'],flush=True)
assert .355<=before['rate']<=.365,before
assert .895<=after['rate']<=.905,after
path=OUT/'icsl_glm52_cch_102.csv';clock=datetime(2026,11,5,1,12,17,tzinfo=timezone.utc)
with path.open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['hash_id','appid','model_handle_start_time','completion_tokens','request_input'])
    for i,v in enumerate(records):
        clock+=timedelta(seconds=rng.randint(7,71),milliseconds=rng.randint(0,999))
        w.writerow([str(uuid.UUID(int=rng.getrandbits(128))),APPID,clock.isoformat(),0,raw(v)])
manifest={'description':'ICSL场景构造样本','dataset_kind':'constructed_scenario','appid':APPID,'count':102,'conversations':62,'conversation_sizes':sizes,'model_id':'GLM-5.2','common_name':'GLM-V5.2','seed':20261105,'completion_tokens':'placeholder 0, not measured output','settings':settings.model_dump(),'asset_identity':assets.identity,'encoder_identity':enc.identity,'model_asset_spec':assets.spec.model_dump(),'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'csv_bytes':path.stat().st_size,'before':before,'after_reference':after,'lengths':details,'seconds':time.perf_counter()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:manifest[k] for k in ('csv_bytes','seconds','peak_rss_kib')}),flush=True)

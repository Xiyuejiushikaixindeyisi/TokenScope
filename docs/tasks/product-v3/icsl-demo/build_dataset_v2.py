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

HERE=Path(__file__).resolve().parent/'revision2'; OUT=HERE/'delivery';OUT.mkdir(parents=True,exist_ok=True)
APPID='demo.synthetic.icsl.glm52.cch.v2'
settings=DEFAULT_SETTINGS['GLM-5.2']; assets=AssetRegistry(ROOT).load('GLM-5.2')
enc=ModelEncoder(assets,settings);batch=EncodingBatchService(enc)
def raw(body):return json.dumps(body,ensure_ascii=False,separators=(',',':'))
tools=[{'type':'function','function':{'name':n,'description':d,'parameters':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}}} for n,d in [('inspect_module','Inspect the named module and its test contract.'),('propose_patch','Propose a reviewable patch without changing production data.'),('review_tests','Review unit tests and explain missing edge cases.')]]
def module(n):
    domains=['invoice','shipment','inventory','refund','reservation','catalog','pricing','account']
    domain=domains[n%len(domains)]; lim=11+n%79
    return f'''\nModule {n}: {domain} consistency contract\nThe component {domain}_service_{n} validates a command before publishing an event. All amounts use integer minor units. Replaying a committed command must return the existing result. Validation errors must not mutate the journal. The caller supplies a stable command identity.\n```python\nclass {domain.title()}Policy{n}:\n    limit = {lim}\n    def validate(self, command, snapshot):\n        if command.quantity <= 0:\n            raise ValueError("positive quantity required")\n        if command.quantity > self.limit:\n            return {{"accepted": False, "reason": "quota"}}\n        previous = snapshot.find(command.identity)\n        if previous is not None:\n            return previous\n        return {{"accepted": True, "quantity": command.quantity}}\n\ndef test_{domain}_policy_{n}(fixture):\n    policy = {domain.title()}Policy{n}()\n    outcome = policy.validate(fixture.command, fixture.snapshot)\n    assert outcome["accepted"] is True\n    assert fixture.snapshot.write_count == 0\n```\nReview requirements: verify boundary quantities, duplicate identities, empty snapshots, concurrent submissions and rejected commands. Preserve existing public return fields. Introduce new assertions before changing behavior. Document the smallest safe patch and rollback conditions. Module {n} is synthetic project documentation, not customer source code.\n'''
pool=''.join(module(n) for n in range(500))
intro='You are the coding assistant for the fictional ICSL demo project. This is synthetic material for TokenScope demonstrations. Preserve business correctness and propose reviewable patches.\n'
def body(a,b,i,tail,header=True):
    line=f'x-anthropic-billing-header: cc_version=demo.v1; cc_entrypoint=synthetic-cli; cch={i:05x};\n' if header else ''
    return {'model':'GLM-5.2','messages':[{'role':'system','content':intro+a+'\n'},{'role':'system','content':line},{'role':'system','content':b},{'role':'user','content':f'Coding task {i:03d}: review module {i}, explain the defect and propose tests.\n'+tail}], 'tools':tools,'enable_thinking':False}
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
started=time.perf_counter()
a=fit(pool,18400,lambda s:lcp(ids(body(s,'',0,'')),ids(body(s,'',1,''))))
bpool='\nAdditional repository reference:\n'+pool[len(a):]
b=fit(bpool,45720,lambda s:lcp(ids(body(a,s,0,'',False)),ids(body(a,s,1,'',False))))
rng=random.Random(20261105); targets=[max(48000,min(52500,round(rng.gauss(50000,800)))) for _ in range(80)]
targets=[v-round(statistics.mean(targets)-50000) for v in targets]
records=[];before_ids=[];after_ids=[];details=[]
for i,target in enumerate(targets):
    tail_pool=''.join(module(1000+i*9+j) for j in range(35))
    empty_len=len(ids(body(a,b,i,'')))
    tail=fit(tail_pool,target-empty_len,lambda t:len(enc.full.encode(t,add_special_tokens=False).ids))
    v=body(a,b,i,tail); before=ids(v); after=ids(body(a,b,i,tail,False))
    records.append(v);before_ids.append(before);after_ids.append(after)
    details.append({'index':i,'prompt_before':len(before),'prompt_after':len(after),'target':target})
    if i%10==0:print('generated',i,'tokens',len(before),flush=True)
def replay(rows,label):
    p=HERE/f'calibration-{label}-{time.time_ns()}.sqlite3'
    ledger=PrefixLedger(p); strategy=FullBlockStrategy(settings,assets.identity,ledger)
    hits=[]
    for row in rows:hits.append(strategy.process(APPID,row).hit_tokens)
    ledger.close();total=sum(map(len,rows));return {'p':total,'h':sum(hits),'c':total-sum(hits),'rate':sum(hits)/total,'per_request_hits':hits}
before=replay(before_ids,'before');after=replay(after_ids,'after')
assert .355<=before['rate']<=.365,before
assert .895<=after['rate']<=.905,after
path=OUT/'icsl_glm52_cch_80.csv'
with path.open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['hash_id','appid','model_handle_start_time','completion_tokens','request_input'])
    for i,v in enumerate(records):w.writerow([f'synthetic-icsl-glm52-{i:03d}',APPID,(datetime(2026,11,5,tzinfo=timezone.utc)+timedelta(seconds=i)).isoformat(),0,raw(v)])
manifest={'dataset_kind':'synthetic_demonstration','appid':APPID,'count':80,'model_id':'GLM-5.2','common_name':'GLM-V5.2','seed':20261105,'completion_tokens':'synthetic placeholder 0; no output-performance claim','settings':settings.model_dump(),'asset_identity':assets.identity,'encoder_identity':enc.identity,'model_asset_spec':assets.spec.model_dump(),'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'csv_bytes':path.stat().st_size,'before':before,'after_reference':after,'lengths':details,'seconds':time.perf_counter()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:manifest[k] for k in ('csv_bytes','seconds','peak_rss_kib')}),flush=True)
print('RATES',before['rate'],after['rate'],flush=True)

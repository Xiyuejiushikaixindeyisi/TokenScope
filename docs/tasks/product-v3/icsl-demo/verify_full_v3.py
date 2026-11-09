import csv,json,urllib.request,re,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent/'revision3';a=json.loads((p/'acceptance-backend.json').read_text());m=json.loads((p/'delivery/manifest.json').read_text());tid=a['task']['task_id'];h={'X-TokenScope-Service-Instance':a['service_instance_id']}
def get(path):
 with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:18002/diagnostics/tasks/'+tid+'/'+path,headers=h),timeout=120) as r:return json.load(r)
def save(n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2))
ev=next(x['data'] for x in a['evaluations'] if x['data']['stage']=='full')
assert ev['coverage']['checked']=='102' and ev['coverage']['complete'] and ev['display_eligible']
for k in ('p','h','c'):
 assert int(ev['before'][k])==m['before'][k] and int(ev['after'][k])==m['after_reference'][k]
rows=[]
for offset in (0,100):rows+=get('evaluations/'+ev['evaluation_id']+'/rows?limit=100&offset='+str(offset))['items']
assert len(rows)==102
csv.field_size_limit(16*1024*1024)
with (p/'delivery/icsl_glm52_cch_102.csv').open() as f:raw=list(csv.DictReader(f))
for r in rows:
 e=r['evidence'];before=json.loads(raw[int(r['source_record_index'])-1]['request_input']);content=before['messages'][0]['content'];before['messages'][0]['content']=content.split('\n',1)[1]
 assert json.loads(e['after_raw'])==before
 assert len(e['changes'])==1 and e['changes'][0]['source_pointer']=='/messages/0/content'
summary=get('recommendation-summary');save('recommendation-summary.json',summary);assert summary['recommendation_count']=='1'
save('recommendations.json',get('recommendations?direction=low_hit'))
save('final-validation.json',{'passed':True,'full_rows':102,'only_top_billing_line_removed':True,'full_matches_reference':True,'before_percent':m['before']['rate']*100,'after_percent':m['after_reference']['rate']*100,'csv_sha256':m['csv_sha256'],'old_user_entries_preserved':a['old_user_entries_preserved'],'old_diagnostic_entries_preserved':a['old_diagnostic_entries_preserved']})
v=json.loads((p/'delivery/diagnostic-submission-local.json').read_text());v['request']['source']['user_run_id']='REPLACE_WITH_HUAWEI_USER_RUN_ID';v['request']['source']['expected_index_revision']='REPLACE_WITH_HUAWEI_INDEX_REVISION';save('delivery/diagnostic-submission-template.json',v)
print(json.dumps({'passed':True,'rows':len(rows),'before':ev['before'],'after':ev['after'],'sha256':m['csv_sha256']}))

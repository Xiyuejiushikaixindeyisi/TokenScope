import csv,hashlib,json,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'src'))
from tokenscope.prefix_analysis.detection import pair_dynamics
from tokenscope.prefix_analysis.dynamic import apply_recipe,dynamic_recipes
HERE=Path(__file__).resolve().parent/'revision3'
csv.field_size_limit(16*1024*1024)
with (HERE/'delivery/icsl_glm52_cch_102.csv').open() as f:
    rows=list(csv.DictReader(f))
left,right=[json.loads(x['request_input']) for x in [rows[0],next(r for r in rows if json.loads(r['request_input'])['messages'][0]['content']!=json.loads(rows[0]['request_input'])['messages'][0]['content'])]]
found=[x for x in pair_dynamics(left,right) if x[0]=='L1']
assert len(found)==1
recipe=json.loads(found[0][2]);assert recipe['pattern']=='billing_header'
modified=[]
for row in rows:
    v=json.loads(row['request_input']);old=v['messages'][0]['content'];new=apply_recipe(old,recipe)
    assert new is not None and new!=old
    removed=[line for line in old.splitlines(keepends=True) if line.startswith('x-anthropic-billing-header:')]
    assert len(removed)==1 and old.replace(removed[0],'',1)==new
    v['messages'][0]['content']=new;modified.append(v)
assert not [x for x in pair_dynamics(modified[0],modified[1]) if x[0]=='L1']
constant=json.loads(json.dumps(right));constant['messages'][0]['content']=left['messages'][0]['content']
assert not [x for x in pair_dynamics(left,constant) if x[0]=='L1']
assert len({r['hash_id'] for r in rows})==102
result={'positive_l1':True,'constant_cch_no_l1':True,'removed_cch_no_l1':True,'only_one_billing_line_removed_all_102':True,'other_fields_preserved_by_reference':True,'request_count':len(rows),'unique_hash_ids':102,'max_raw_bytes':max(len(r['request_input'].encode()) for r in rows),'fixture_only':True}
(HERE/'negative-controls.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

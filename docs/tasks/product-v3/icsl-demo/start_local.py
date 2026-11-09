"""Start local acceptance on a copy of retained HV2 state. Never replace originals."""
import hashlib,json,os,shutil,socket,subprocess,time
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OLD=ROOT/'artifacts/reviews/hv2-repair-20261103/final-default';WORK=HERE/'local'
assert not WORK.exists(),'Existing work state must be preserved; do not silently reset'
for port in (18002,4191):
 with socket.socket() as s:assert s.connect_ex(('127.0.0.1',port))!=0,('port occupied',port)
def hashes(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
baseline=hashes(OLD/'state');WORK.mkdir()
(HERE/'existing-original-sha256.json').write_text(json.dumps(baseline,indent=2))
shutil.copytree(OLD/'state',WORK/'state');shutil.copytree(OLD/'inputs',WORK/'inputs',symlinks=True)
assert baseline==hashes(WORK/'state')
env=os.environ.copy();env.pop('TOKENSCOPE_RECOMMENDATION_BUNDLE',None)
cmd=[str(ROOT/'.venv/bin/python'),'-m','tokenscope.cli','--input-root',str(WORK/'inputs'),'--state-root',str(WORK/'state'),'--asset-root',str(ROOT),'--cpu-budget','8','serve','--host','127.0.0.1','--port','18002','--viewer-root',str(OLD/'dist')]
with (WORK/'server.log').open('x') as log:p=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
record={'pid':p.pid,'argv':cmd,'original_state':str(OLD/'state'),'working_state':str(WORK/'state'),'base_url':'http://localhost:18002','original_files':len(baseline),'ui':str(OLD/'dist')}
(WORK/'server.json').write_text(json.dumps(record,indent=2))
for _ in range(100):
 if p.poll() is not None:raise RuntimeError((WORK/'server.log').read_text())
 try:
  with urlopen('http://127.0.0.1:18002/healthz',timeout=1) as response:print(response.read().decode());break
 except OSError:time.sleep(.2)
else:raise RuntimeError('Server readiness timeout')
print(json.dumps(record,indent=2))

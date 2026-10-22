#!/usr/bin/env python3
"""Run bounded release acceptance checks without rewriting release data."""
import subprocess,sys,tempfile,json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args):
 print('+ '+' '.join(args),flush=True)
 subprocess.run(args,cwd=ROOT,check=True)
def main():
 lock=json.loads((ROOT/'data/current-release.json').read_text())
 for group in ['files','authoring','reviewFiles']:
  for name,sha in lock[group].items():
   path=ROOT/'data'/name if group=='files' else ROOT/name
   if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('Release lock mismatch: '+name)
 for path,label,key in [('diagnose/app.js','DATA_VERSION','version'),('diagnose/engine.js','ENGINE_VERSION','engineVersion')]:
  match=re.search(label+r" = '([^']+)'",(ROOT/path).read_text())
  if not match or match.group(1)!=lock[key]:raise ValueError('Application version mismatch: '+path)
 run([sys.executable,'scripts/validate.py'])
 for name in ['statistics','algebra','algebra_d2','algebra_d3','algebra_d4','algebra_d5']:
  run([sys.executable,'scripts/build_'+name+'.py','--check'])
 for p in sorted((ROOT/'scripts').glob('build_rc_*.py')):
  if p.name!='build_rc_review.py':run([sys.executable,str(p.relative_to(ROOT)),'--check'])
 run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*build.py'])
 run(['node','tests/test_engine.js'])
 run([sys.executable,'scripts/check_figures.py'])
 with tempfile.TemporaryDirectory(prefix='cnm-release-') as tmp:
  run([sys.executable,'scripts/verify_questions.py','--file','data/questions.json','--report',str(Path(tmp)/'verification.json')])
 print('RELEASE ACCEPTANCE CHECKS PASSED')
if __name__=='__main__':main()

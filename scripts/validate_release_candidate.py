#!/usr/bin/env python3
"""Run bounded release acceptance checks without rewriting release data."""
import subprocess,sys,tempfile,json,hashlib,re,shutil
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
 if lock['version'].startswith('primary-'):
  run([sys.executable,'scripts/build_primary_review.py','--check'])
  run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_primary_review.py'])
  # Previous patches assert their historical outputs. Reconstruct the exact
  # frozen release, verify its byte hashes, and run the unchanged old checks.
  # Never weaken historical assertions to accommodate newer question edits.
  with tempfile.TemporaryDirectory(prefix='cnm-history-') as tmp:
   r=Path(tmp)
   for name in ['data','authoring','reviews','scripts','tests','diagnose']:
    shutil.copytree(ROOT/name,r/name,ignore=shutil.ignore_patterns('__pycache__'))
   subprocess.run([sys.executable,str(r/'scripts/build_primary_review.py'),'--reverse'],cwd=r,check=True)
   shutil.copyfile(r/'reviews/math-primary/base-release.json',r/'data/current-release.json')
   shutil.copyfile(r/'reviews/math-primary/base-validator.py',r/'scripts/validate_release_candidate.py')
   shutil.copyfile(r/'reviews/math-primary/base-test-engine.js',r/'tests/test_engine.js')
   app=r/'diagnose/app.js';app.write_text(app.read_text().replace("const DATA_VERSION = '"+lock['version']+"'","const DATA_VERSION = 'junior-2026-10.1'"))
   subprocess.run([sys.executable,str(r/'scripts/validate_release_candidate.py')],cwd=r,check=True)
  run(['node','tests/test_engine.js'])
  run([sys.executable,'scripts/check_figures.py'])
  with tempfile.TemporaryDirectory(prefix='cnm-primary-') as tmp:
   run([sys.executable,'scripts/verify_questions.py','--file','data/questions.json','--report',str(Path(tmp)/'verification.json')])
  print('PRIMARY RELEASE ACCEPTANCE CHECKS PASSED');return
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

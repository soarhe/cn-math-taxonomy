#!/usr/bin/env python3
"""Apply/reverse the primary review patch; check every object before any write."""
import argparse,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def build(root=ROOT,check=False,reverse=False):
 patch=json.loads((root/'authoring/primary-2026-10/patch.json').read_text());result={}
 for kind in ['topics','questions','dependencies']:
  data=json.loads((root/'data'/f'{kind}.json').read_text())
  for c in patch[kind]:
   if c['beforeHash']!=(digest(c['before']) if c['before'] is not None else None):raise ValueError('Invalid preimage '+c['id'])
   field='topicId' if kind=='dependencies' else 'id';found=[x for x in data if x[field]==c['id']]
   old=found if kind=='dependencies' else found[0] if found else None
   src,dst=(c['after'],c['before']) if reverse else (c['before'],c['after'])
   if old==dst:continue
   if old!=src:raise ValueError('Upstream drift '+c['id'])
   if check:raise ValueError('Patch not applied '+c['id'])
   if kind=='dependencies':data=[x for x in data if x[field]!=c['id']]+copy.deepcopy(dst)
   elif dst is None:data=[x for x in data if x[field]!=c['id']]
   elif found:data[data.index(found[0])]=copy.deepcopy(dst)
   else:data.append(copy.deepcopy(dst))
  if reverse and kind=='dependencies':
   order={tuple(x):i for i,x in enumerate(patch['baseDependencyOrder'])}
   data.sort(key=lambda x:order[(x['topicId'],x['prerequisiteId'])])
  result[kind]=data
 # Standards are a separately reviewed document, not an upstream regeneration.
 sp=root/'authoring/primary-2026-10/standards-patch.json'
 if sp.exists():
  c=json.loads(sp.read_text());actual=json.loads((root/'data/cn-curriculum-standards.json').read_text())
  if digest(c['before'])!=c['beforeHash']:raise ValueError('Invalid standards preimage')
  src,dst=(c['after'],c['before']) if reverse else (c['before'],c['after'])
  if actual not in [src,dst]:raise ValueError('Upstream standards drift')
  if check and actual!=dst:raise ValueError('Standards patch not applied')
  result['cn-curriculum-standards']=dst
 if not check:
  for k,data in result.items():(root/'data'/f'{k}.json').write_text(json.dumps(data,ensure_ascii=False,indent=1 if k=='questions' else 2)+'\n')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--reverse',action='store_true');a=p.parse_args();build(check=a.check,reverse=a.reverse);print('Primary review patch OK')

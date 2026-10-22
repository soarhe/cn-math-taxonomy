#!/usr/bin/env python3
"""Apply the algebra review patch, guarding every changed object against drift.
Run after upstream staged builders. Unrelated records are preserved. --check checks output.
"""
import argparse,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def build(root=ROOT,check=False):
    patch=json.loads((root/'authoring/release-candidate/algebra-graphs.json').read_text())
    result={}
    for kind in ['topics','questions','dependencies']:
        path=root/'data'/f'{kind}.json'; data=json.loads(path.read_text()); changes=patch[kind]
        for change in changes:
            id=change['id']; field='topicId' if kind=='dependencies' else 'id'
            matches=[x for x in data if x[field]==id]
            old=matches if kind=='dependencies' else matches[0] if matches else None
            new=change['after']
            if old==new:continue
            actual=digest(old) if old is not None else None
            if actual!=change['beforeHash']:
                raise ValueError(f'{kind}/{id}: upstream drift; review before applying')
            if check:raise ValueError(f'{kind}/{id}: patch not applied')
            if kind=='dependencies':
                data=[x for x in data if x[field]!=id]+copy.deepcopy(new)
            elif matches:data[data.index(matches[0])]=copy.deepcopy(new)
            else:data.append(copy.deepcopy(new))
        result[kind]=data
    # All drift checks complete before writing any file.
    if not check:
        for kind,data in result.items():
            (root/'data'/f'{kind}.json').write_text(json.dumps(data,ensure_ascii=False,indent=1 if kind=='questions' else 2)+'\n')
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    r=build(check=args.check);print('Release candidate algebra graphs patch OK:',{k:len(v) for k,v in r.items()})

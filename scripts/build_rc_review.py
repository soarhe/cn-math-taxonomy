#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consolidate first-pass provenance; never promote it to teacher certification."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def write(p,x):(ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def build():
    topics=read('data/topics.json');questions=read('data/questions.json');edges=read('data/dependencies.json')
    junior={t['id']:t for t in topics if t['id'].startswith('cnm_') and t.get('grade') in [7,8,9]}
    records={}
    paths=sorted((ROOT/'reviews/release-candidate/notes').glob('*.json'))+sorted((ROOT/'reviews/math-junior').glob('batch-*/node-review.json'))
    for p in paths:
        for r in json.loads(p.read_text()):
            tid=r['topicId']
            if tid not in junior:continue
            assert tid not in records,tid
            qs=[q for q in questions if q['topicId']==tid];ds=[d for d in edges if d['topicId']==tid]
            records[tid]={'topicId':tid,'name':junior[tid]['name'],'domain':junior[tid]['domain'],'reviewRecord':str(p.relative_to(ROOT)),'firstPassFinding':r.get('finding',r.get('assessment',r.get('changeSummary','见原审阅记录'))),'questionIds':[q['id'] for q in qs],'currentSnapshotSha256':digest({'topic':junior[tid],'questions':qs,'dependencies':ds}),'status':'first-pass-reviewed','expertReviewed':False}
    assert set(records)==set(junior)
    write('reviews/release-candidate/node-review.json',{'scope':'317个初中节点首轮；不是教师认证或能力全覆盖结论','count':len(records),'rows':[records[k] for k in sorted(records)]})
    return records
if __name__=='__main__':print('Consolidated:',len(build()))

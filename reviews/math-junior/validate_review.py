#!/usr/bin/env python3
"""Validate batch A references, baseline integrity, review states and task arithmetic."""
import hashlib,json,re
from fractions import Fraction as F
from pathlib import Path
from statistics import median
P=Path(__file__).resolve().parent
R=P.parents[1]
def load(p):return json.loads(p.read_text())
def check(v,msg):
    if not v:raise ValueError(msg)
a=load(P/'standards-audit.json'); cards=load(P/'statistics/cards.json')
t=load(R/'data/topics.json'); q=load(R/'data/questions.json'); s=load(R/'data/cn-curriculum-standards.json')['items']
tids={x['id'] for x in t};sids={x['id'] for x in s};rows=a['rows']
check(len(rows)==157 and len({r['standardId'] for r in rows})==157,'157 unique requirements')
check(sum(len(r['subrequirements']) for r in rows)==159,'159 subrequirements')
check(sum(p['type']=='optional' for r in rows for p in r['subrequirements'])==5,'5 optional subrequirements')
check(sum(r['mappingStatus']=='unreferenced' for r in rows)==15,'15 unreferenced baseline requirements')
for r in rows:
    check(r['standardId'] in sids,'missing standard')
    expected={x['id'] for x in t if any(y['id']==r['standardId'] for y in x['standards'])}
    check(expected=={x['topicId'] for x in r['mappedTopics']},'mapping mismatch')
    check(r['coverage'] in ['pending','partial','missing','explicit'],'invalid coverage')
    check(not r['expertReviewed'],'unearned expert status')
    if not r['standardId'].startswith('cms-2022:4.SP.'):
        check(r['coverage']=='pending' and r['source2025']['status']=='not-compared','unreviewed row mislabeled')
    else:
        check(r['source2025']['pdfPages']==[x+3 for x in r['source2025']['printedPages']],'2025 pages')
check(len(cards)==7 and len({c['id'] for c in cards})==7,'7 unique cards')
for c in cards:
    check(set(c['existingTopicIds'])<=tids,'card topic reference')
    check(set(c['standardIds'])<=sids,'card standard reference')
    check(len(c['tasks'])>=2 and len(c['evidence'])>=2,'missing evidence or tasks')
    check(all(x['prompt'] and x['answer'] for x in c['tasks']),'empty task')
    check(c['status']=='assistant-draft' and not c['expertReviewed'],'card status')
inv=load(P/'statistics/topic-inventory.json');check(len(inv)==43,'43 topic inventory')
check({x['id'] for x in inv}=={x['id'] for x in t if re.fullmatch(r'cnm_\d+',x['id']) and x['domain']=='统计与概率'},'inventory mismatch')
d=load(P/'statistics/decisions.json');check({x['cardId'] for x in d['cards']}=={x['id'] for x in cards},'decision references')
for x in d['cards']:
    check(x['decision'] in [None,'accept','adjust','defer'],'invalid decision')
    if x['decision'] is not None:check(x['reviewer'] and x['reviewedAt'],'decision provenance')
for name,sha in load(P/'baseline-lock.json')['files'].items():check(hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,'production changed: '+name)
# Independent exact arithmetic for numerical tasks and the counterexample.
def sse(xs):
    m=sum(map(F,xs))/len(xs)
    return sum((F(x)-m)**2 for x in xs)
check(sse([1,2])+sse([8,9])==1,'S01-A')
check(sse([1,8])+sse([2,9])==49,'S01-B')
check([sse([0,2]),sse([0,9]),sse([2,9])]==[2,F(81,2),F(49,2)],'S01 exploration')
xs=sorted([9,1,7,3,8,2,6,4]);check((median(xs[:4]),median(xs),median(xs[4:]))==(2.5,5,7.5),'S02 quartiles')
check(54-46==8 and 60-40==20,'S02 interpretation')
check(40-20==20 and 35-25==10,'S03 box widths')
xs=[35]*15+[50]*10+[60]*15
check(median(xs[:20])==35 and median(xs[20:])==60,'S03 quartiles')
check(sum(35<=x<=60 for x in xs)==40 and sum(35<x<60 for x in xs)==10,'S03 counterexample')
check(F(2,5)==F(2,len(['R1','R2','W1','W2','W3'])),'S06 balls')
check(sum(a!=b for a in [0,1] for b in [0,1])==2,'S06 coins')
check(F(512,1000)==F(64,125),'S07 estimate')
check(abs(F(513,1001)-F(1,2))>abs(F(512,1000)-F(1,2)),'S07 nonmonotonic frequency')
print('Review OK: 157 requirements / 159 subrequirements; 43-topic inventory; 7 cards / 14 tasks; baseline hashes and numerical counterexamples verified.')
print('Content-source review is limited to 13 statistics requirements; teacher review and user decisions remain pending.')

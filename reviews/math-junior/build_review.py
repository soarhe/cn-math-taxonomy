#!/usr/bin/env python3
"""Build review artifacts only. Does not modify production data or reviewer decisions."""
import json, hashlib, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = '97b7b8c684fc82fb4d3037d4074555174a9a79f1'
def read(p): return json.loads((ROOT / p).read_text())
def write(p, obj): (OUT / p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
lock = OUT / 'baseline-lock.json'
if lock.exists():
    for name, expected in json.loads(lock.read_text())['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise SystemExit('Batch A is a frozen historical review. Data changed; use scripts/build_statistics_review.py for batch B.')

topics=read('data/topics.json'); edges=read('data/dependencies.json'); questions=read('data/questions.json')
standards=[x for x in read('data/cn-curriculum-standards.json')['items'] if x['id'].startswith('cms-2022:4.')]
notes=read('reviews/math-junior/statistics/requirement-findings.json')
rows=[]
verbs=['体会','理解','了解','认识','掌握','探索','证明','经历','知道','感悟','会计算','能计算','能用','能画','能解释','能制作','会制作']
for s in standards:
    sid=s['id']; mapped=[{'topicId':t['id'],'confidence':r['confidence']} for t in topics for r in t['standards'] if r['id']==sid]
    elective='optional' if s.get('elective') else 'mixed' if '*' in s['text'] else 'required'
    parts=[]
    if elective=='mixed':
        a,b=s['text'].split('*',1)
        parts=[{'id':sid+'/required','type':'required','text':a},{'id':sid+'/optional','type':'optional','text':b}]
    else: parts=[{'id':sid+'/'+elective,'type':elective,'text':s['text']}]
    pages=[int(n) for n in re.findall(r'\d+',s['page_or_ref'])]
    finding=notes.get(sid)
    r={'standardId':sid,'domain':s['domain'],'section':s['section'],'clause':s['clause'],
       'requirementTextFromBaseline':s['text'],'requirementType':elective,'subrequirements':parts,
       'verbCandidates':[v for v in verbs if v in s['text']],
       'source2022':{'sourceId':'math-2022-moe','printedPages':pages,'pdfPages':[p+7 for p in pages],
          'status':'visually-checked' if finding else 'baseline-locator-not-rechecked'},
       'mappedTopics':mapped,'mappingStatus':'referenced' if mapped else 'unreferenced',
       'coverage':finding['coverage'] if finding else 'pending',
       'finding':finding['finding'] if finding else '本批仅提取原有引用和定位；未完成能力、任务及原页核查。无引用不自动等于无覆盖。',
       'reviewStatus':'assistant-draft' if finding else 'not-reviewed','expertReviewed':False}
    if finding:
        n=int(sid.rsplit('.',1)[1]); pp=[73] if n<=3 else [73,74] if n==4 else [74]
        r['source2025']={'sourceId':'math-2025-school-copy','printedPages':pp,'pdfPages':[p+3 for p in pp], 'status':'visually-checked-content-requirement','comparison':'这13条内容要求与2022版语义一致；不推断全科或全部章节无变化。'}
    else:r['source2025']={'sourceId':'math-2025-school-copy','status':'not-compared','printedPages':[],'pdfPages':[]}
    rows.append(r)
stat=[t for t in topics if re.fullmatch(r'cnm_\d+',t['id']) and t['domain']=='统计与概率']
counts={'standards':len(rows),'referenced':sum(bool(x['mappedTopics']) for x in rows),'unreferenced':sum(not x['mappedTopics'] for x in rows),'subrequirements':sum(len(x['subrequirements']) for x in rows),'requiredSubrequirements':sum(p['type']=='required' for x in rows for p in x['subrequirements']),'optionalSubrequirements':sum(p['type']=='optional' for x in rows for p in x['subrequirements']),'contentRequirementsReviewed':len(notes),'remainingContentRequirements':len(rows)-len(notes),'statisticsTopics':len(stat)}
write('standards-audit.json',{'version':'batch-a.1','baselineCommit':BASE,'date':'2026-10-22','scope':'初中内容要求。统计13条已作首轮内容审阅，其余为审计骨架。','verbExtraction':'仅用于检索的字符串候选，不代表已完成要求层次标注。','counts':counts,'rows':rows})
cards=read('reviews/math-junior/statistics/cards.json')
selected={i for c in cards for i in c['existingTopicIds']}
write('statistics/baseline-evidence.json',{'baselineCommit':BASE,'topics':[t for t in topics if t['id'] in selected],'dependencies':[e for e in edges if e['topicId'] in selected],'questions':[q for q in questions if q['topicId'] in selected]})
write('statistics/topic-inventory.json',[{'id':t['id'],'name':t['name'],'questionIds':[q['id'] for q in questions if q['topicId']==t['id']],'cardIds':[c['id'] for c in cards if t['id'] in c['existingTopicIds']],'reviewStatus':'representative-card-drafted' if t['id'] in selected else 'not-reviewed'} for t in stat])
write('baseline-lock.json',{'commit':BASE,'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/topics.json','data/dependencies.json','data/questions.json','data/cn-curriculum-standards.json','diagnose/engine.js']}})
lines=['# 初中内容要求审计表','','这是批次A审计骨架：157条中统计与概率13条完成助手首轮审阅，其余144条待核。引用不等于充分覆盖，所有结论均未经教师审核。','','| 条款 | 类别 | 引用节点数 | 覆盖初判 | 定位（2022印刷页） | 审核意见 |','|---|---|---:|---|---|---|']
for r in rows:lines.append('| '+ ' | '.join([r['standardId'],r['requirementType'],str(len(r['mappedTopics'])),r['coverage'],','.join(map(str,r['source2022']['printedPages'])),r['finding'].replace('|','/').replace('\n',' ')])+' |')
(OUT/'AUDIT.md').write_text('\n'.join(lines)+'\n')
lines=['# 第一批代表节点审核卡','','共7张卡、14道自编审核任务。均为提案，未应用到正式图谱或题库。每张卡的任务用于审核能力边界，不是单凭两题认证掌握。','','review意见请写入独立的 `decisions.json` 或在聊天按卡号反馈；生成器不会覆盖该文件。']
for c in cards:
    lines+=['',f"## {c['id']} · {c['title']}",'',f"**动作：**{c['action']}。**旧ID：**{', '.join(c['existingTopicIds']) or '无，新增候选'}。",'',f"**课标：**{', '.join(c['standardIds'])}",'',f"**现状证据：**{c['finding']}",'',f"**能力边界：**{c['scope']}",'','**可观察证据：**']
    lines += ['- '+s for s in c['evidence']]
    lines+=['','**先修处理：**'+c['dependencyProposal'],'','**典型误区：**'+c['misconception'],'','**审核任务与判据：**']
    for i,t in enumerate(c['tasks'],1):lines+=['',f"{i}. {t['prompt']}",f"   - 答案／判据：{t['answer']}"]
    lines+=['','**尚待核对：**'+c['pending'],'','**需要你确认：**'+c['reviewQuestion']]
(OUT/'statistics/REVIEW.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(counts,ensure_ascii=False))

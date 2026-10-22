#!/usr/bin/env python3
"""Build the D1 review inventory and current release lock from authored findings.
Source checks are explicitly scoped to content-requirement pages, not examples or all teaching notes.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def dump(p,x):
 path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def build():
 patch=load('authoring/algebra-2026-10/patch.json');findings=load('authoring/algebra-2026-10/findings.json')
 topics=load('data/topics.json');qs=load('data/questions.json');edges=load('data/dependencies.json');byid={x['id']:x for x in topics}
 changed={x['id'] for x in patch['questions']};rows=[]
 for id,note in findings['notes'].items():
  t=byid[id];rows.append({'topicId':id,'name':t['name'],'action':'revise-retain-id','finding':note,'reviewScope':'目标能力边界和本批修改题目；不声称全题库已审完','changedQuestionIds':[q['id'] for q in qs if q['topicId']==id and q['id'] in changed],'evidenceQuestionIds':findings['evidence'].get(id,[]),'reviewer':'assistant','expertReviewed':False,'userContentDecision':'not-yet-recorded','textbookLocationStatus':'inherited-not-rechecked'})
 dump('reviews/math-junior/batch-d1/node-review.json',rows)
 inventory=[]
 for t in topics:
  if t['id'].startswith('cnm_') and t['domain']=='数与代数' and t['grade'] in (7,8,9):
   inventory.append({'topicId':t['id'],'name':t['name'],'status':'targeted-revision' if t['id'] in findings['notes'] else 'pending-content-review','expertReviewed':False})
 dump('reviews/math-junior/batch-d1/topic-inventory.json',inventory)
 req=[]
 for old in load('reviews/math-junior/standards-audit.json')['rows']:
  if old['domain']!='数与代数':continue
  sid=old['standardId'];n=int(sid.rsplit('.',1)[1]);pg=[57] if n<=11 else [57,58] if n==12 else [58] if n<=24 else [59] if n<=38 else [59,60] if n==39 else [60]
  mapped=[t for t in topics if any(x['id']==sid for x in t['standards'])]
  evidence=[qid for t in mapped for qid in findings['evidence'].get(t['id'],[])]
  targeted=any(t['id'] in findings['notes'] for t in mapped)
  req.append({'standardId':sid,'section':old['section'],'requirementType':old['requirementType'],'requirementText':old['requirementTextFromBaseline'],
   'source2022':{'sourceId':'math-2022-moe','pdfPages':old['source2022']['pdfPages'],'printedPages':old['source2022']['printedPages'],'status':'content-clause-visually-rechecked'},
   'source2025':{'sourceId':'math-2025-school-copy','pdfPages':pg,'printedPages':[p-3 for p in pg],'status':'content-clause-compared-in-school-copy','finding':'本条内容要求未见实质差异；不代表原始发布文件认证或全部课标对齐。'},
   'topicIds':[t['id'] for t in mapped],'mappingStatus':'referenced' if mapped else 'unreferenced',
   'coverage':'partial' if targeted else 'pending','evidenceQuestionIds':evidence,
   'finding':'; '.join(findings['notes'][t['id']] for t in mapped if t['id'] in findings['notes']) if targeted else '本批核查了条文及来源定位，尚未逐节点、逐题判断能力覆盖。',
   'remaining':'真实任务、其他子能力、全部题型与教师审核待完成。' if targeted else '需逐节点审阅能力边界、题目及先修；有引用不等于充分覆盖。','expertReviewed':False})
 dump('reviews/math-junior/batch-d1/requirements.json',req)
 dump('reviews/math-junior/batch-d1/question-review.json',[{'questionId':q['id'],'topicId':q['topicId'],'action':'add' if next(c for c in patch['questions'] if c['id']==q['id'])['before'] is None else 'replace-or-reclassify','contentSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'checking':'assistant-semantic-check; numeric invariants in tests/test_algebra_build.py; verify expressions are not independent blind solving','scope':q.get('curriculum_scope','required-task-candidate'),'rubric':q.get('rubric',[]),'expertReviewed':False} for q in qs if q['id'] in changed])
 er=[]
 for c in patch['dependencies']:
  for e in c['after']:
   er.append({**e,'action':'retain' if e in c['before'] else 'revise-or-add','reviewStatus':'assistant-provisional','counterexampleCheck':e['reason'],'expertReviewed':False})
 dump('reviews/math-junior/batch-d1/edge-review.json',er)
 sources=load('reviews/math-junior/sources.json')['sources']
 for src in sources:
  src['visuallyCheckedPdfPagesThisBatch']=[61,62,63,64,65] if src['id']=='math-2022-moe' else [57,58,59,60,61]
  src['scope']='初中数与代数49条内容要求。案例64–72全文、全部学业要求/教学提示未在本批完整复核。小学衔接条款映射未重新认证。'
 dump('reviews/math-junior/batch-d1/sources.json',{'date':'2026-10-22','sources':sources})
 counts={'topics':len(topics),'questions':len(qs),'dependencies':len(edges),'algebraInventory':len(inventory),'targetedJuniorTopics':sum(r['status']=='targeted-revision' for r in inventory),'primaryBridgeTopics':sum(byid[r['topicId']]['grade']<7 for r in rows),'changedQuestionObjects':len(changed),'netAddedQuestions':sum(c['before'] is None for c in patch['questions']),'contentRequirementsSourceChecked':len(req),'partiallyReviewedRequirements':sum(r['coverage']=='partial' for r in req),'pendingCoverageRequirements':sum(r['coverage']=='pending' for r in req)}
 release={'version':'algebra-2026-10.1','engineVersion':'evidence-1.1','date':'2026-10-22','baseCommit':patch['baseCommit'],'previousRelease':'statistics-2026-10.1','expertReviewed':False,'counts':counts,'files':{n:sha('data/'+n) for n in ['topics.json','questions.json','dependencies.json']},'authoring':{n:sha(n) for n in ['authoring/statistics-2026-10/patch.json','authoring/algebra-2026-10/patch.json']},'review':'reviews/math-junior/batch-d1/README.md','migration':'旧statistics及evidence-1会话保留原样导出；修改题面不继承历史作答或盲解标记。'}
 dump('data/current-release.json',release)
 print(json.dumps(counts,ensure_ascii=False))
if __name__=='__main__':build()

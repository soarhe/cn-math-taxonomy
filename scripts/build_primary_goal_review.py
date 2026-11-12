#!/usr/bin/env python3
"""Publish bounded authoring gates; structural coverage is not teaching certification."""
import argparse,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text())
def build(check=False):
 catalog=load('data/primary-curriculum-supplement.json'); base=[t for t in load('data/topics.json') if t['id'].startswith(('cnm_p','cne_p'))]
 topics=[dict(t,**catalog['overrides'].get(t['id'],{})) for t in base]+catalog['nodes']
 math=load('data/primary-activities.json')['tasks'];english=load('data/english-primary-activities.json')['tasks'];tasks=math+english
 rows=[]
 for t in topics:
  links=[a for a in tasks if t['id'] in a['topicIds']]
  # Prefer a focused task over the older broad standard-level task as the review entry.
  links.sort(key=lambda a:(not ('-node-' in a['id'] or '-source-' in a['id']),len(a['topicIds'])))
  rows.append({'topicId':t['id'],'name':t['name'],'subject':t.get('subject','math'),'knowledgeReview':'agent-first-pass-not-expert-certified','reviewScope':'数学沿用216项首轮知识/题库审查并复核活动关联；英语本轮逐项读取名称、描述及能力要求、修正活动材料与关联，未认证788原题全部内容。','description':t['description'],'masteryCriteria':t['mastery_criteria'],'correctedForCurriculumView':t['id'] in catalog['overrides'],'newFromOfficialRequirement':t['id'].startswith('cne_ps'),'taskIds':[a['id'] for a in links],'reviewEntryTaskId':links[0]['id'] if links else None,'reviewEntryEvidence':(links[0].get('prompt') or ' '.join(links[0]['instructions'])) if links else None,'status':'has-reviewed-task-sample' if links else 'gap','expertReviewed':False})
 def counts(ts,prefix):
  ids={t['id'] for t in topics if t['id'].startswith(prefix)};linked={x for a in ts for x in a['topicIds']}&ids
  anchors=sum(bool(a.get('scoringExample')) if prefix=='cnm_p' else len(a.get('scoringExamples',[]))==3 for a in ts)
  return {'knowledgePoints':len(ids),'taskCount':len(ts),'nodesWithTask':len(linked),'unlinkedNodeIds':sorted(ids-linked),'tasksWithCustomScoringExamples':anchors,'observationItems':sum(len(a['rubric']) for a in ts),'authoringGatesPassed':len(linked)==len(ids) and anchors==len(ts)}
 report={'version':'primary-goal-review-2026-11.1','acceptanceScope':'编写与首轮语义审查门槛：既有413节点及本轮新补25节点全部有可执行任务；所有任务有定制0/1/2示例。数量达标不是国家课标全文、词表或教学有效性认证。','math':counts(math,'cnm_p'),'english':counts(english,'cne_p'),'rows':rows,'remainingValidation':['教师独立审核、真实学生试做及评分一致性校准','英语原788题与236条先修逐项独立复核','2025版原件认证与完整差异核验','官方词汇附录逐词审计及500词实际运用样本','新增页面交互验收；不能用纯状态逻辑测试替代浏览器验证']}
 p=R/'reviews/primary-supplement/completion.json';s=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
 if check:assert p.read_text()==s,'Goal review artifact drift'
 else:p.write_text(s)
 print(json.dumps({'math':report['math'],'english':report['english']},ensure_ascii=False))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');build(p.parse_args().check)

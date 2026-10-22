#!/usr/bin/env python3
"""Compile individually authored performance tasks; preserve the frozen question audit."""
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='primary-activities-2026-10.1'
def load(p): return json.loads((ROOT/p).read_text())
def dump(x): return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def build(check=False):
 old=load('reviews/math-primary/coverage.json'); original={r['standardId'].split(':')[1]:r for r in old['rows']}
 topics={t['id']:t for t in load('data/topics.json')}
 sources=[
  {'id':'solar-terms','title':'中国非物质文化遗产网：农历二十四节气','url':'https://www.ihchina.cn/project_details/15059.html','locator':'项目介绍','checkedOn':'2026-10-22','note':'中国传统时间文化；节气名称与当地实际气候不必完全同步。'},
  {'id':'media-2024','title':'人民日报：2024年国民经济和社会发展统计公报（2025-03-01）','url':'https://paper.people.com.cn/rmrb/pc/content/202503/01/content_30059609.html','locator':'表1：2024年年末人口数及其构成','checkedOn':'2026-10-22','note':'历史版真实媒体材料，链接阅读，不复制全文；不作为当前人口数据。'},
  {'id':'nbs-2024','title':'国家统计局：2024年国民经济和社会发展统计公报（2025-02-28）','url':'https://www.stats.gov.cn/sj/zxfb/202502/t20250228_1958817.html','locator':'表1','checkedOn':'2026-10-22','note':'核对男性71909、女性68919、合计140828，单位万人；原表比例保留一位小数，本任务重算到两位小数。'},
  {'id':'measure-history','title':'中国财税博物馆：青铜量具一组','url':'https://www.fmuseum.cn/collection/article/clqakplqp001mwoi5fih1goy9','locator':'内容介绍','checkedOn':'2026-10-22','note':'统一量器与公平比较的史料；不把古代升直接等同现代升。'},
  {'id':'seasons','title':'中科院地理资源所：四季变化与地球公转','url':'https://www.igsnrr.cas.cn/cbkx/kpyd/dlzs/climate/202009/t20200910_5692635.html','locator':'四季变化解释','checkedOn':'2026-10-22','note':'供教师带读，不把天文术语作为小学数学评分要求。'},
  {'id':'standard-2022','title':'教育部：义务教育数学课程标准（2022年版）','url':'http://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220510531636118932.pdf','locator':'小学内容要求及综合实践示例（印刷页42–51）','checkedOn':'2026-10-22','note':'沿用首轮来源审核。主题活动名称为参考示例，四个增补示例不是新增强制知识点。'}]
 source_map={'2.SP.04':['media-2024','nbs-2024'],'3.SP.03':['media-2024','nbs-2024'],'2.IP.04':['measure-history'],'2.IP.01':['seasons','solar-terms']}
 tasks=[]; matrix=[]; edges=[]
 for line in (ROOT/'authoring/primary-completion/tasks.txt').read_text().splitlines():
  key,title,ids,materials,steps,expected,criteria=line.split('|')
  tid='pact-'+key.replace('.','-'); topic_ids=['cnm_p'+x for x in ids.split(',')]
  assert all(t in topics for t in topic_ids),key
  example=key.startswith('example.'); stage=3 if example else int(key[0])
  record=original.get(key); target='example-2022:'+key.split('.')[1] if example else 'cms-2022:'+key
  rubric=[{'id':tid+'-r'+str(i+1),'criterion':s,'levels':{'0':'提交证据显示未满足本项要求；请指出具体错误。','1':'部分满足本项，仍需提示、修正或补充证据。','2':'独立完成本项，并提交可核查的过程或作品。'}} for i,s in enumerate(criteria.split('§'))]
  task={'id':tid,'kind':'performance-task','title':title,'stage':stage,'gradeRange':[stage*2-1,stage*2], 'topicIds':topic_ids,'targetId':target,'targetKind':'reference-example' if example else 'standard-record','materials':materials,'instructions':steps.split('§'),'submission':['逐步记录实际操作、原始数据或推理过程；注明日期、单位和条件。','提交作图、作品或实物记录的文字说明及本地附件文件名；页面不上传附件。','逐项填写评分依据和反馈；未观察的项目保持未观察。'],'reference':expected,'rubric':rubric,'assessmentMode':'human-observation','autoMastery':False,'expertReviewed':False,'studentTrialCompleted':False,'sourceIds':source_map.get(key,[])+(['standard-2022'] if example else []),'repeatPolicy':'按任务要求重复；综合素养任务须跨次观察。未提交、未观察、答错三者分开记录。'}
  tasks.append(task)
  for topic in topic_ids: edges.append({'from':tid,'to':topic,'type':'practises','diagnosticPropagation':False})
  edges.append({'from':tid,'to':target,'type':'addresses','diagnosticPropagation':False})
  matrix.append({'targetId':target,'kind':task['targetKind'],'previousStatus':record['coverage'] if record else 'unindexed-example','previousFinding':record['finding'] if record else next(x['needed'] for x in load('reviews/math-primary/source-review.json')['additionalUnindexedExamples'] if x['name']=={'campus':'校园平面图','sport':'体育中的数学','lunch':'营养午餐','water':'水是生命之源'}[key.split('.')[1]]),'taskIds':[tid],'rubricIds':[r['id'] for r in rubric],'contentStatus':'authored-awaiting-review','validationStatus':'teacher-review-and-student-trial-pending'})
 assert len(tasks)==len({t['id'] for t in tasks})==81
 assert {m['targetId'] for m in matrix if m['kind']=='standard-record'}=={r['standardId'] for r in old['rows']}
 data={'schemaVersion':1,'version':VERSION,'baseline':'primary-2026-10.1','scope':'77条既有记录的已知不足及4个参考活动示例的任务补充，不宣称穷尽国家课标或完成2025全文认证。','sources':sources,'tasks':tasks,'relations':edges}
 report={'version':VERSION,'counts':{'previousGapsAddressed':10,'previousPartialsAddressed':67,'referenceExamplesAdded':4,'tasksAuthored':81,'rubricCriteria':sum(len(t['rubric']) for t in tasks),'unassignedKnownFindings':0,'expertValidated':0},'statusMeaning':'authored-awaiting-review 只表示逐条补充了可执行任务及量规，不表示学生已掌握或专家验证充分覆盖。','rows':matrix,'remainingExternalValidation':['教师独立内容复核、作图和测量评分校准。','真实学生试做与跨次素养观察。','2025版官方原件认证及完整版本对照；2022全文逐字转写核验。','教材年级标签与课标学段的逐项教学安排校准；活动页按课标学段提供入口。']}
 outputs={'data/primary-activities.json':dump(data),'reviews/primary-completion/coverage.json':dump(report)}
 for name,content in outputs.items():
  if check:
   assert (ROOT/name).read_text()==content,'Generated file drift: '+name
  else:(ROOT/name).write_text(content)
 print(('Checked' if check else 'Built')+f' {len(tasks)} activities, {len(edges)} typed relations, {report["counts"]["rubricCriteria"]} rubric criteria')
 return data,report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');build(p.parse_args().check)

#!/usr/bin/env python3
"""Compile authored tasks and auditable evidence mappings, without fabricating mastery."""
import argparse,hashlib,json,subprocess,tempfile,wave
from pathlib import Path
R=Path(__file__).resolve().parents[1]
VERSION='english-primary-2026-11.2'
def read(p):return json.loads((R/p).read_text())
def serial(d):return json.dumps(d,ensure_ascii=False,indent=2)+'\n'
def build(check=False,audio=False):
 tasks=read('authoring/english-primary/batch1.json')['tasks']
 for t in tasks:
  if t['skill']=='listening':t['standardIds']=[];t['mappingNote']='补充听力能力；不使用口语或阅读条目冒充直接听力覆盖。'
  if t['id']=='ep-picture-colours':t['prompt']='看图并阅读三句：Number one is red. Number two is green. Number three is green. 判断各句与图是否一致并改错；再口头回答What colour is number two?';t['reference']='对、错、对。第二句改为Number two is blue. 口头回答It is blue. 阅读与口头表达分别记录。';t['skill']='reading-speaking'
  if t['id']=='ep-write-letters':t['prompt']=t['prompt'].replace('A到F','A到Z');t['reference']=t['reference'].replace('Aa Bb Cc Dd Ee Ff；','Aa至Zz全部26组；')
 for line in (R/'authoring/english-primary/batch2.txt').read_text().splitlines():
  sid,title,skill,ids,prompt,transcript,ref,criteria=line.split('|')
  level=int(sid[0]);grades=[3,4] if level==1 or sid=='2.GR.02' else [5,6]
  tasks.append(dict(id='ep-'+sid.replace('.','-'),title=title,skill=skill,gradeRange=grades,topicIds=['cne_p'+x for x in ids.split(',')],standardIds=['ces-2022:'+sid],prompt=prompt,transcript=transcript,reference=ref,rubric=criteria.split('；'),audio=None,figure=None,expertReviewed=False,autoMastery=False))
 for t in tasks:
  if t['transcript'] and t['audio'] is None:
   path=R/'activities/english-primary/audio'/f'{t["id"]}.wav'
   if audio:
    with tempfile.TemporaryDirectory() as tmp:
     aiff=Path(tmp)/'speech.aiff'
     subprocess.run(['say','-v','Samantha','-r','135','-o',str(aiff),t['transcript']],check=True)
     subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(aiff),'-ar','22050','-ac','1',str(path)],check=True)
   if not path.exists():raise ValueError('Missing audio; run --audio on macOS: '+str(path))
   with wave.open(str(path)) as w:
    if w.getnframes()/w.getframerate()<1:raise ValueError('Empty/short audio: '+str(path))
   t['audio']={'path':'audio/'+path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'provider':'macOS Samantha synthetic speech','humanListeningReviewed':False}
  t['observationItems']=[{'id':t['id']+'-o'+str(i+1),'criterion':criterion,'evidenceRequired':'提交能支持本项判断的原句、实际录音片段说明、作品或观察记录；只填分数不算证据。','levels':{'unobserved':'未观察或未提交：保持未观察，不记0分。','0':'已有作答但未体现：'+criterion,'1':'部分体现，仍依赖提示或含影响意义的错误：'+criterion,'2':'独立体现且有可核对证据：'+criterion}} for i,criterion in enumerate(t['rubric'])]
  t['referenceIsExample']=True
  t['repeatTask']='间隔至少一天，教师替换人物、物品或数量后再做同类任务；保存两次证据，不由一次得分推断稳定掌握。'
 examples={
 'ep-listen-intro':['0：听后把年龄记成颜色，无法提取目标信息。','1：独立听出Lucy和blue，但年龄需第三次提示。','2：两遍内独立记录Lucy、nine、blue，且未打开文字稿。'],
 'ep-write-note':['0：便条未表达邀请目的。','1：邀请可理解，但漏地点或需照抄关键句。','2：独立写明时间地点活动与回复请求，并有自主修订。'],
 'ep-2-GR-02':['0：把正在读书说成She read yesterday，时间意义不符。','1：She reading可理解但缺is，提示后修正。','2：根据现场独立说She is reading，再正确描述多人动作。'],
 'ep-1-RW-02':['0：把red理解成书包颜色且找不到原文依据。','1：能找出姓名年龄，但漏数量或混淆颜色所属。','2：五项信息正确，划出依据，并指出书包颜色未知。']}
 for t in tasks:t['scoringExamples']=examples.get(t['id'],['判分时逐项对应观察要求，参考结果允许等价表达；未提供证据保留未观察。'])
 standards=[s for s in read('data/cn-curriculum-standards.json')['items'] if s['id'].startswith(('ces-2022:1.','ces-2022:2.'))]
 topics={t['id']:t for t in read('data/topics.json') if t['id'].startswith('cne_p')}
 for t in tasks:
  assert set(t['topicIds'])<=set(topics)
  assert set(t['standardIds'])<={s['id'] for s in standards}
  assert not (t['skill']=='listening' and t['standardIds'])
 rows=[{'standardId':s['id'],'sourceStatus':s.get('text_status'),'taskIds':[t['id'] for t in tasks if s['id'] in t['standardIds']],'status':'sample-authored' if any(s['id'] in t['standardIds'] for t in tasks) else 'not-yet-supplemented','expertValidated':False,'scope':'内部条目有任务，不代表官方课标充分覆盖'} for s in standards]
 observations=[{'taskId':t['id'],'id':o['id'],'capability':o['criterion'],'modality':t['skill'],'status':'authored-not-observed'} for t in tasks for o in t['observationItems']]
 out={
 'data/english-primary-activities.json':{'version':VERSION,'tasks':tasks,'audioNote':'合成语音，尚未人工听审。文字稿打开后须记录答案暴露。'},
 'reviews/english-primary/coverage.json':{'version':VERSION,'scope':'35条仓库内部转述记录，不是官方完整条目清单。','rows':rows,'observations':observations,'remaining':['官方要求逐项建底表，35条不能代表全部课标','词表与教材版本逐项核验','197节点、788题、236条关系完整复核','音频人工听审和教师、学生验证']},
 'reviews/english-primary/node-coverage.json':{'version':VERSION,'rows':[{'topicId':tid,'name':t['name'],'taskIds':[a['id'] for a in tasks if tid in a['topicIds']],'status':'has-supplement-sample' if any(tid in a['topicIds'] for a in tasks) else 'legacy-questions-only'} for tid,t in topics.items()]}}
 for p,d in out.items():
  if check:assert (R/p).read_text()==serial(d),'Generated drift: '+p
  else:(R/p).write_text(serial(d))
 print(VERSION,len(tasks),'tasks;',len(observations),'observation items;',sum(bool(x['taskIds']) for x in rows),'/35 internal records')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--audio',action='store_true');a=p.parse_args();build(a.check,a.audio)

(async function(){'use strict';
const el=(tag,text)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=text;return x;};
const VERSION='english-primary-2026-11.2',KEY='cnm.'+VERSION,OLD='cnm.english-primary-2026-11.1';
let records={},history={};const status=document.getElementById('status');
function parse(key){const x=JSON.parse(localStorage.getItem(key)||'{}');return x&&typeof x==='object'&&!Array.isArray(x)?x:{};}
try{records=parse(KEY);history=parse(OLD);}catch(e){status.textContent='本机记录读取失败；原记录未覆盖，请先导出备份。';}
function save(){try{localStorage.setItem(KEY,JSON.stringify(records));status.textContent='已保存本机。本次记录不自动更新诊断掌握状态。';}catch(e){status.textContent='无法保存，请导出备份。';}}
function textarea(parent,label,value,handler){const l=el('label',label),a=el('textarea');a.value=typeof value==='string'?value:'';a.addEventListener('input',()=>handler(a.value));l.append(a);parent.append(l);}
try{
const res=await fetch('../../data/english-primary-activities.json');if(!res.ok)throw Error(res.status);const data=await res.json();
if(data.version!==VERSION)throw Error('页面与数据版本不一致，请刷新');
function render(){
const root=document.getElementById('tasks');root.replaceChildren();const query=document.getElementById('q').value.toLowerCase(),grade=document.getElementById('grade').value;
const topic=new URLSearchParams(location.search).get('topic');
const list=data.tasks.filter(t=>(!topic||t.topicIds.includes(topic))&&(!grade||t.gradeRange.includes(Number(grade)))&&(t.title+' '+t.skill+' '+t.standardIds.join(' ')).toLowerCase().includes(query));
if(topic){const a=el('a','查看全部任务');a.href='./';root.append(a);}root.append(el('p','显示 '+list.length+' / '+data.tasks.length+' 个任务'));
if(!list.length)root.append(el('p','尚无匹配的补充任务；不表示该知识点没有原题。请调整筛选或查看全部任务。'));
for(const t of list){
 const box=el('article');box.id=t.id;const r=records[t.id]||(records[t.id]={});
 const details=el('details');details.open=location.hash==='#'+t.id||list.length===1;
 details.append(el('summary',t.title+' · '+t.gradeRange.join('–')+'年级'),el('p',t.skill+' · '+(t.standardIds.join('、')||'补充能力：未套用阅读或口语条目')),el('p',t.prompt));
 if(t.id==='ep-2-GR-02')details.append(el('p','学段校正：2022课标一级已要求理解现在进行时；关联的旧教材节点年级不作为学段要求。','note'));
 if(t.audio){const a=el('audio');a.controls=true;a.preload='none';a.src=t.audio.path;details.append(a);}
 if(t.figure){const img=el('img');img.src=t.figure;img.alt='三支编号蜡笔，请根据可见颜色作答';details.append(img);}
 const answer=el('details');answer.append(el('summary','查看文字稿和参考（会记录已查看）'),el('p',t.transcript),el('p',t.reference));
 answer.addEventListener('toggle',()=>{if(answer.open){r.answerExposed=true;r.updatedAt=new Date().toISOString();save();}});details.append(answer);
 textarea(details,'作答、操作过程或本地录音/作品文件名',r.response,v=>{r.response=v;r.updatedAt=new Date().toISOString();save();});
 const guide=el('details');guide.append(el('summary','评分边界与示例'));t.scoringExamples.forEach(x=>guide.append(el('p',x)));guide.append(el('p',t.repeatTask));guide.addEventListener('toggle',()=>{if(guide.open){r.answerExposed=true;r.scoringGuideExposed=true;save();}});details.append(guide);
 (t.observationItems||[]).forEach((o,i)=>{
  const l=el('label',o.criterion+'：'),s=el('select');
  [['','未观察'],['0','未满足'],['1','部分满足'],['2','独立完成且有证据']].forEach(([v,n])=>{const opt=el('option',n);opt.value=v;s.append(opt);});s.value=r['score'+i]||'';
  s.addEventListener('change',()=>{r['score'+i]=s.value;r.updatedAt=new Date().toISOString();save();});l.append(s);details.append(l);
  textarea(details,'本项依据：'+o.criterion,(r.observationEvidence||{})[o.id],v=>{r.observationEvidence=r.observationEvidence||{};r.observationEvidence[o.id]=v;r.updatedAt=new Date().toISOString();save();});
 });
 textarea(details,'观察者、日期和后续反馈',r.feedback,v=>{r.feedback=v;save();});box.append(details);root.append(box);
}}
document.getElementById('q').addEventListener('input',render);document.getElementById('grade').addEventListener('change',render);
document.getElementById('export').addEventListener('click',()=>{
 const warnings=[];data.tasks.forEach(t=>{const r=records[t.id]||{};(t.observationItems||[]).forEach((o,i)=>{if(r['score'+i]&&!((r.observationEvidence||{})[o.id]||'').trim())warnings.push({taskId:t.id,observationId:o.id,issue:'score-without-evidence'});});});
 const b=new Blob([JSON.stringify({version:data.version,autoMastery:false,records,warnings,historicalRecords:{'english-primary-2026-11.1':history}},null,2)],{type:'application/json'}),url=URL.createObjectURL(b),a=el('a');a.href=url;a.download='english-primary-records.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='已导出；无依据的评分标注待核，旧版记录单独保留。';
});render();document.getElementById(location.hash.slice(1))?.scrollIntoView();
}catch(e){status.textContent='加载失败：'+e.message+'；请使用本地HTTP服务器打开。';}
})();

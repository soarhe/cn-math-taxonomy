/* Human-observed portfolio; never feeds scores into the diagnosis engine. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const el = (tag, text, cls) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const KEY='cnm.primary.activities.primary-activities-2026-10.1';
  let data, topics, records={}, filtered=[];
  function notify(text){$('notice').textContent=text;}
  try {const saved=JSON.parse(localStorage.getItem(KEY)||'{}');if(saved&&typeof saved==='object'&&!Array.isArray(saved))records=saved;}
  catch(e){notify('未能读取本机记录；可继续填写并导出，请勿清理浏览器。');}
  function persist(){try{localStorage.setItem(KEY,JSON.stringify(records));notify('已保存到当前浏览器。请导出备份；尚未上传或认证。');}catch(e){notify('浏览器无法保存，请立即导出记录备份。');}}
  function record(task){let r=records[task.id];if(!r||typeof r!=='object'||Array.isArray(r))r=records[task.id]={};r.scores=r.scores&&typeof r.scores==='object'?r.scores:{};r.feedback=r.feedback&&typeof r.feedback==='object'?r.feedback:{};return r;}
  function saveField(task,key,value){const r=record(task);r[key]=value;r.updatedAt=new Date().toISOString();persist();}
  function addTextArea(host,label,value,onchange){const l=el('label',label);const input=el('textarea');input.value=typeof value==='string'?value:'';l.append(input);input.addEventListener('input',()=>onchange(input.value));host.append(l);}
  function link(text,url){const a=el('a',text);a.href=url;return a;}
  function render(){
    const stage=$('stage').value,term=$('query').value.trim().toLowerCase(),topic=new URLSearchParams(location.search).get('topic');
    filtered=data.tasks.filter(t=>(!stage||String(t.stage)===stage)&&(!topic||t.topicIds.includes(topic))&&(!term||(t.title+' '+t.targetId+' '+t.id+' '+t.topicIds.map(id=>topics.get(id)?.name||id).join(' ')).toLowerCase().includes(term)));
    $('count').textContent='显示 '+filtered.length+' / '+data.tasks.length+' 个任务'+(topic?' · 当前知识点 '+(topics.get(topic)?.name||topic):'');
    const root=$('tasks');root.replaceChildren();
    if(topic)root.append(link('取消知识点筛选，查看全部任务','./'));
    if(!filtered.length)root.append(el('p','没有匹配任务，请调整筛选。','empty'));
    for(const task of filtered){
      const card=el('article');card.id=task.id;const details=el('details');details.open=location.hash==='#'+task.id;
      const summary=el('summary',task.title);summary.append(el('span',task.gradeRange.join('–')+' 年级 · '+task.targetId+(task.targetKind==='reference-example'?' · 参考示例':'')));details.append(summary);
      const links=el('p');task.topicIds.forEach(id=>{const a=link(topics.get(id)?.name||id,'../../explore/#'+id);a.className='tag';links.append(a);});details.append(links);
      details.append(el('h3','准备材料'),el('p',task.materials),el('h3','执行步骤'));const steps=el('ol');task.instructions.forEach(s=>steps.append(el('li',s)));details.append(steps);
      if(task.sourceIds.length){details.append(el('h3','来源材料'));task.sourceIds.forEach(id=>{const s=data.sources.find(x=>x.id===id);const p=el('p');const a=link(s.title,s.url);a.target='_blank';a.rel='noopener noreferrer';p.append(a,el('small',' · '+s.locator+'。'+s.note));details.append(p);});}
      details.append(el('h3','提交要求'));const submissions=el('ol');task.submission.forEach(s=>submissions.append(el('li',s)));details.append(submissions);
      const reference=el('details',undefined,'reference');reference.append(el('summary','查看参考结果与评价边界'),el('p',task.reference),el('p',task.repeatPolicy));details.append(reference);
      const r=record(task);details.append(el('h3','过程记录与作品索引'));
      addTextArea(details,'日期、原始数据、操作过程、作品说明和本地附件文件名',r.evidence,v=>saveField(task,'evidence',v));
      addTextArea(details,'学生解释、同伴反馈与修订记录',r.reflection,v=>saveField(task,'reflection',v));
      details.append(el('h3','人工评价'),el('p','每项独立评价：未观察 / 0 未满足 / 1 部分满足 / 2 独立完成且有证据。分数不是自动认证。','muted'));
      for(const criterion of task.rubric){
        const div=el('div',undefined,'rubric'),label=el('label',criterion.criterion+' '),select=el('select');
        [['','未观察'],['0','0 · 未满足'],['1','1 · 部分满足'],['2','2 · 独立完成且有证据']].forEach(([v,t])=>{const o=el('option',t);o.value=v;select.append(o);});
        select.value=['0','1','2'].includes(r.scores[criterion.id])?r.scores[criterion.id]:'';
        select.addEventListener('change',()=>{r.scores[criterion.id]=select.value;r.updatedAt=new Date().toISOString();persist();});label.append(select);div.append(label);
        addTextArea(div,'本项评分依据与下一步反馈',r.feedback[criterion.id],v=>{r.feedback[criterion.id]=v;r.updatedAt=new Date().toISOString();persist();});details.append(div);
      }
      addTextArea(details,'观察者代号、观察日期及需要复做的内容',r.observer,v=>saveField(task,'observer',v));
      card.append(details);root.append(card);
    }
  }
  $('export').addEventListener('click',()=>{if(!data)return;const body={schemaVersion:1,activityVersion:data.version,exportedAt:new Date().toISOString(),assessmentMode:'human-observation',autoMastery:false,records};const blob=new Blob([JSON.stringify(body,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=link('',url);a.download='primary-activity-records.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notify('已导出本机人工记录；不包含附件，也不改变诊断结果。');});
  $('print').addEventListener('click',()=>{document.querySelectorAll('#tasks article > details').forEach(d=>d.open=true);window.print();});
  $('stage').addEventListener('change',render);$('query').addEventListener('input',render);
  window.addEventListener('hashchange',()=>{render();document.getElementById(location.hash.slice(1))?.scrollIntoView();});
  Promise.all(['../../data/primary-activities.json','../../data/topics.json'].map(async path=>{const res=await fetch(path);if(!res.ok)throw new Error('HTTP '+res.status);return res.json();})).then(([d,t])=>{data=d;topics=new Map(t.map(x=>[x.id,x]));render();document.getElementById(location.hash.slice(1))?.scrollIntoView();}).catch(e=>{notify('加载失败：'+e.message+'。请通过本地静态服务器访问。');});
})();

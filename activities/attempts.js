/* Attempt history shared by human-observed activities. No mastery propagation. */
(function(root){'use strict';
function archive(record,version,now=new Date().toISOString()) {
 const {attemptHistory=[],...current}=record;
 const snapshot=JSON.parse(JSON.stringify(current));
 snapshot.contentVersion=version;snapshot.archivedAt=now;
 if(snapshot.answerExposed===undefined)snapshot.answerExposureStatus='unknown';
 const priorExposure=current.answerExposed===true||current.priorAnswerExposure===true;
 return {attemptHistory:[...attemptHistory,snapshot],startedAt:now,contentVersion:version,priorAnswerExposure:priorExposure,priorExposureStatus:priorExposure?'known-exposed':'unknown',answerExposed:false};
}
function warnings(records,tasks,kind){
 const result=[];
 for(const task of tasks){const active=records[task.id];if(!active)continue;
 const attempts=[...(active.attemptHistory||[]),active];
 attempts.forEach((r,index)=>{
 const criteria=kind==='math'?task.rubric:task.observationItems;
 criteria.forEach((o,i)=>{const score=kind==='math'?(r.scores||{})[o.id]:r['score'+i];const evidence=kind==='math'?(r.feedback||{})[o.id]:(r.observationEvidence||{})[o.id];
 if(['0','1','2'].includes(String(score))&&!String(evidence||'').trim())result.push({taskId:task.id,attempt:index+1,observationId:o.id,issue:'score-without-evidence'});
 });
 });}
 return result;
}
const api={archive,warnings};if(typeof module!=='undefined')module.exports=api;else root.ActivityAttempts=api;
})(typeof window==='undefined'?this:window);

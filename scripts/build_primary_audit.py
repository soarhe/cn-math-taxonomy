#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the current primary evidence index from explicit review decisions."""
import json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text())
def write(p,x):(ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
# Each line is an explicit evidence decision, not a count of standards references.
# Empty evidence means a gap; broad competencies remain partial at best.
COVERAGE='''
1.NA.01|017_3,055_4|数位与数的组成有题；算盘表示、读写多位数和真实情境数感未充分取样。
1.NA.02|002_1,029_2,054_4|覆盖大小比较和排序；相等关系的解释仍需口头或书面证据。
1.NA.03|038_2,043_2,047_2|四则意义与相互关系有局部任务；不能用少量选择题认证全部理解。
1.NA.04|019_2,031_1,032_1,033_2|算理、算法和运算有局部证据；真实竖式过程与解释未自动采集。
1.NA.05|039_1,043_3,050_2,052_3|乘除运算和情境解释有题；算法探索过程未采集。
1.NA.06|006_3,052_3|可作为应用和推理的局部观察；数感、符号意识等综合素养不能由答对几题判定。
1.NA.07|035_1,048_1,052_1|撤去了代列算式并检查余数情境；仍需学生说明结果意义。
1.NA.08|060_1,060_2|已给出恒定增减的假设；尚未涵盖学生自己发现并表达多种规律。
1.GG.01|014_1,023_1,024_2|含实图辨形和分割示意；实际动手拼图、分类过程仍缺。
1.GG.02|040_3,041_2,045_2|尺子读数、单位换算和估测有题；统一单位必要性与真实测量未完成。
1.GG.03|024_2,040_3|空间与量感只取得局部观察；需要连续活动表现。
1.SP.01|022_1,037_3|直接测分类标准；实际收集和分类活动仍需补充。
1.IP.01||分类答题不能替代分享学前数学游戏经历的活动。
1.IP.02|036_1,036_4|人民币与简单购物有题；节约意识、交易活动和金融素养没有充分证据。
1.IP.03|061_1,062_2,063_2|时间认识和经过时间有题；感受时长、守时活动没有充分证据，且教材年级安排跨越学段。
1.IP.04|015_2,049_3|位置和方向有纸面题；真实教室定位活动仍缺。
1.IP.05|045_1,045_2|需要校准身体尺的概念和估测计算有题；实际测量记录未采集。
1.IP.06||没有学生叙述或制作数学连环画的活动任务。
2.NA.01|096_2,097_1,102_4,106_3|多位数和乘除运算有题；数级读法和算法迁移证据不足。
2.NA.02|079_2,080_1,093_1,094_1|分数、小数意义和简单运算有题；计数单位解释需要更多表现任务。
2.NA.03|084_2,112_3|情境除法与混合运算有题；综合情境与运算意义解释有限。
2.NA.04|114_4,115_4,116_4|已补运算律及字母表达；探索和证明过程不由选择题替代。
2.NA.05|076_2,076_3|编码是局部应用；生活特征描述和数感发展需持续观察。
2.NA.06|066_2,126_1|估算与实际问题有题；自主选择估算精度及单位的任务不足。
2.NA.07||无操作计算器并探索规律的任务；普通计算题不算此条证据。
2.NA.08|111_1,111_2,111_4|总价、路程等关系有直接情境；解释关系和迁移仍需补充。
2.NA.09||未见直接测量“等量的等量相等”的具体情境任务。
2.NA.10|109_2,131_2|优化与模型问题有局部证据；模型建立和结果说明未充分采集。
2.GG.01|099_2,103_4,104_3|线与位置关系有题；尺规作等长线段、两点最短路径的操作缺。
2.GG.02|100_1,100_2|量角器对齐和读圈有题；实际画角与量角缺。
2.GG.03|067_1,068_1,090_4|单位换算有题；真实估测、测量与选择单位不足。2022原页确认平方单位。
2.GG.04|105_3,122_1,122_3|分类依据有题；多样图形、旋转形态辨认不足。
2.GG.05|078_2,088_3,089_1|周长面积概念和计算有题；公式探索过程不足。
2.GG.06|113_3,113_4|文字描述物体的视向有题；照片、复杂遮挡和直接视图匹配不足。
2.GG.07|088_3,113_4|局部空间与量感观察，不等于综合素养认证。
2.GG.08|127_2,128_2,171_4|点的位置变换与性质有题；实物变换和完整图形操作不足。
2.GG.09|127_4,128_4|局部位置推断；几何直观需更多真实操作证据。
2.SP.01|085_4,037_3|读表整理位置和分类标准有题；实际采集数据和制作表格缺。
2.SP.02|085_1,085_2|表内比较和信息解释有题；学生自主交流分析不足。
2.SP.03|108_2,130_3|实际条形图读数与比较已补；独立绘图仍缺。
2.SP.04||无真实媒体统计图来源和相应阅读任务，不能把自编图冒充媒体图表。
2.SP.05|129_2,129_4|计算平均数和概念有题；移多补少、异常值与适用性不足。
2.SP.06|130_2,129_4|情境图表与平均数局部应用；自主选择表达方式不足。
2.IP.01|091_4,092_1|日历和24时记时有题；古代四季文化与主题探究缺。
2.IP.02|056_2,070_2|质量单位换算有题；曹冲称象中的等量替代推理缺。
2.IP.03|082_2,082_3|斜方向有题；几点钟方向、寻找宝藏实际活动缺。
2.IP.04||无查阅度量衡史料和理解统一单位的主题活动任务。
3.NA.01|153_1,155_1,156_4,157_3,158_1,159_1|基本术语和公因数公倍数有题；穷举过程与概念关联解释不足。
3.NA.02|118_1,165_3,166_3,170_3|小数分数意义与互化有题；计数单位与多情境迁移不足。
3.NA.03||现有平均分、分数除法题未直接测a÷b＝a/b及其具体情境解释。
3.NA.04|133_1,173_1,178_2,183_2|四则运算有题；跨运算一致性的解释不足。
3.NA.05|144_2,144_4|等式性质直接判断有题；天平等具体情境操作不足。方程题型不等于原文独立要求。
3.NA.06|135_1,135_2|积的近似数提供局部取近似证据；实际情境自主选择估算方法不足。
3.NA.07|142_4,200_4|字母表示数量关系和规律有题；自主建式与一般性解释不足。
3.NA.08|185_4,186_1,187_3,210_2|比、比例、按比分配有题；情境范围和解释证据有限。
3.NA.09|213_1,213_4|正比例有局部证据；变化趋势表和自主探规律不足，反比例不充作此条直接证据。
3.NA.10|179_3,184_1,187_3,205_3|数量关系应用有题；说明模型与结果合理性不足。
3.GG.01|123_3,124_2|三边关系和内角和有直接问题；操作验证和推理表达不足。
3.GG.02|188_2,189_2,190_3,192_3,193_2|圆概念与计算有题；圆规作图及公式探索缺。
3.GG.03|147_1,148_1,149_1,150_2|面积公式应用有题；不规则图形估面积与公式推导不足。2022原页确认平方千米。
3.GG.04|162_2,164_4|体积容积概念和换算有题；不规则物体排水测量缺。
3.GG.05|160_3,161_1,206_4,208_1,209_2|形体性质、侧面展开和公式有题；完整展开图匹配与公式探索不足。
3.GG.06|152_2,152_4|简单方块与遮挡推理有题；三视图实图互配仍缺。
3.GG.07|161_1,164_4|局部量感和空间证据；综合素养需实际活动观察。
3.GG.08|180_1,180_4,181_1|方向距离、反向路线有题；绘制与阅读实际路线图不足。
3.GG.09|136_2,136_3|数对顺序有题；方格纸落点的实际图形任务不足。
3.GG.10|212_2,212_4|比例尺与单位换算有题；方格图放大缩小操作缺。
3.GG.11|127_2,128_2,171_4|点的对应、平移和方向旋转有题；补全或变换整个图形缺。
3.GG.12||无欣赏和设计图案的学生作品任务。
3.SP.01||没有完整的实际问题驱动的数据采集、整理、分析和学生陈述过程。
3.SP.02|175_2,175_3,199_2,199_4|真实可见的自编折线图与扇形图阅读有题；自主画图和呈现数据缺。
3.SP.03||无实际媒体来源及数据获取任务。
3.SP.04|194_3,197_1,199_4|百分数统计意义、部分总体和基数限制有题；开放探究不足。
3.SP.05|197_2,199_2,205_3|百分率与图表的局部实际应用；自主收集数据和判断情境合理性不足。
3.SP.06|140_3,140_4|随机现象的不确定性有题；真实实验过程未采集。
3.SP.07|141_2,141_3,141_4|可能性大小与必然性的区分有题；随机实验验证不足。
3.IP.01|201_4,202_1,202_4|相反意义的量直接表示有题；完整主题活动与学生说明不足。
'''

def build():
 ts=load('data/topics.json');qs=load('data/questions.json');ds=load('data/dependencies.json');patch=load('authoring/primary-2026-10/patch.json')
 changed={k:{c['id'] for c in patch[k]} for k in ['topics','questions','dependencies']}
 rows=[]
 for t in ts:
  if not t['id'].startswith('cnm_p'):continue
  tid=t['id'];questions=[q for q in qs if q['topicId']==tid];deps=[d for d in ds if d['topicId']==tid]
  limits='题目只提供局部答题证据；未完成教师独立盲审、学生试测或全能力逐项认证。'
  if t['domain']=='图形与几何':limits+='纸面识别或数值计算不能替代实际作图、测量、拼摆与公式探索。'
  if t['domain']=='综合与实践':limits+='当前短题不能替代主题活动、观察记录和学生作品。'
  rows.append({'topicId':tid,'name':t['name'],'grade':t['grade'],'status':'first-pass-reviewed','expertReviewed':False,'masteryCriteria':t['mastery_criteria'],'evidenceQuestionIds':[q['id'] for q in questions],'changedQuestionIds':[q['id'] for q in questions if q['id'] in changed['questions']],'dependencyDecision':'revised' if tid in changed['dependencies'] else 'retained-for-first-pass','incomingDependencies':deps,'finding':'已按节点能力检查题干、答案和先修关系。'+('有修订，详见带前后文的补丁。' if any(q['id'] in changed['questions'] for q in questions) else '本轮保留现有题目。'),'limitations':limits,'currentSnapshotSha256':digest({'topic':t,'questions':questions,'dependencies':deps})})
 standards={s['id']:s for s in load('data/cn-curriculum-standards.json')['items']};coverage=[]
 for line in COVERAGE.strip().splitlines():
  sid,ids,finding=line.split('|');sid='cms-2022:'+sid
  qids=['cnm_p'+i.replace('_','_q') for i in ids.split(',')] if ids else []
  assert sid in standards
  for qid in qids:assert any(q['id']==qid for q in qs),qid
  coverage.append({'standardId':sid,'coverage':'partial' if qids else 'gap','evidenceQuestionIds':qids,'finding':finding,'expertReviewed':False,'sourceTextStatus':standards[sid]['text_status'],'pageOrRef':standards[sid]['page_or_ref']})
 expected={s for s in standards if s.startswith(('cms-2022:1.','cms-2022:2.','cms-2022:3.'))}
 assert len(coverage)==len(expected)==77 and {r['standardId'] for r in coverage}==expected
 write('reviews/math-primary/node-review.json',{'version':'primary-2026-10.1','method':'agent first pass; not independent blind solving or teacher certification','rows':rows})
 write('reviews/math-primary/coverage.json',{'scope':'77 existing primary content-requirement records; not proof of completeness for 2025 revision or all practice activities','counts':dict(Counter(r['coverage'] for r in coverage)),'rows':coverage})
 write('reviews/math-primary/progress.json',{'version':'primary-2026-10.1','primaryTopics':len(rows),'primaryQuestions':sum(len(r['evidenceQuestionIds']) for r in rows),'changedTopics':len(patch['topics']),'changedQuestions':len(patch['questions']),'changedIncomingDependencyGroups':len(patch['dependencies']),'primaryDependencies':sum(d['topicId'].startswith('cnm_p') for d in ds),'byGrade':dict(Counter(r['grade'] for r in rows)),'coverage':dict(Counter(r['coverage'] for r in coverage))})
 print(load('reviews/math-primary/progress.json'))
if __name__=='__main__':build()

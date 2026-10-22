import json,re,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'reviews/math-junior/batch-b'
def load(p):return json.loads((r/p).read_text())
def dump(n,x):(out/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
t=load('data/topics.json');q=load('data/questions.json');e=load('data/dependencies.json');patch=load('authoring/statistics-2026-10/patch.json');base=load('reviews/math-junior/statistics/topic-inventory.json')
notes='''102|保留调查方式选择；适用条件和准确性由既有题辨析，待教师审核。
103|保留；样本指观测值与样本容量的区分已有题，先修调查类型暂保留。
104|修正代表性保证；补随机波动解释，完整抽样框与便利抽样分开。
105|保留图表选择，已有小学条形/折线背景；真实读图证据由305等具体图题补充，本点仍待扩图。
106|明确组端点，98/41分组题指定起点；避免未给分组起点时机械套组数。
107|注明等距且纵轴频数；补实际绘图任务与评分判据。
108|保留经济/气温趋势情境；补事实、延续假设与预测限制，不把趋势预测当保证。
211|移除整套有理数混合运算hard门槛，保留小学均值背景；原均值题可独立核验。
212|权可以是频数或人数，不只重要程度；保留数值与权重解释题。
213|保留中位数/众数；明确其复合范围使216仅需中位数子能力，节点级依赖仍为近似。
214|工资题限定为一般员工典型水平，不能脱离目标一律选择中位数。
215|显式加入离差平方和，标准差退出本节点首轮核心任务；保留ID并记录含义调整。
216|补未排序数据和解释任务；保留题中算法约定，奇数规则不冒充全国唯一算法。
217|保留组中值加权估计并保留误差辨析；不是SP.06分类优化的替代。
284|保留三类事件，当前为初中有限模型；不扩展连续概率的零概率事件。
285|改为等可能基本结果计数；补列举和解释任务，同步fallback。
286|保留有限等可能列举；原四题数值可通过表达式核验。
287|补实际列表/树图任务，修正三步试验不能列表的绝对说法；明确独立投掷。
288|限定相同条件，补波动和非单调收敛反例；与285整体硬关系降soft。
289|公平比较限定相同收益损失规则，防止把胜率相等泛化为所有游戏公平。
292|修正种子数据必须亲自实验的表述，已有资料可作背景；问卷设计偏差题保留。
293|保留划记和合计核对；不凭合计错误就改合计。现整数题分组无歧义。
294|补真实折线绘制及坐标单位评分，数值题不能代替绘图过程。
295|补真实扇形绘制及角度合计判据，保留量角器操作要求。
296|保留截断纵轴辨析；截断轴不是所有图形一律禁止，具体解释针对条形高度比较。
297|频率改为本批观测占比，声明分类互斥穷尽，不把样本比例当总体真实比例。
298|补实施任务、无放回和不保证每班入样；代表性辨析降soft，样本概念为hard。
299|标志重捕题补封闭等条件；比较抽样方法统一完整名单，保留估计措辞。
300|补工具计算、缺失值处理、报告和反馈任务；追加SP.10映射，不以背步骤为实施证据。
301|保留同区间频数读图和比例；实际图形形式仍需扩充，现题主要给文字频数。
302|保留样本均值估计，明确估计不等于总体确定值；题库比较抽样方式。
303|中位数较稳健但并非删除极端值后不变，修正描述边界。
304|比较同变量同单位，稳定不自动等于决策最优；保留数值计算。
305|修复重复值人数题，补SVG读图和绘图任务，明确须端约定及离群点画法。
306|修改两处从样本直断总体的解析，保留估计与小样本限制。
307|补基本结果等可能条件及球的同质随机抽取条件。
308|保留概率范围辨析；范围限本课程有限正概率基本结果模型。
309|不均匀骰子不能直接套1/6，但也不能断言某面概率绝不为1/6；不增加反向hard环。
310|明确球的同质和随机抽取；放回/不放回分别计数，原数值可核验。
311|明确独立条件，保留三步树图应用；不因标题“以上”无限扩展题目复杂度。
312|保留频率估计发芽/合格率；模型假设相同条件，外推数量仍为估计。
313|保留图表到概率的综合应用；目前多为文字给数，后续补真实图表变式。
314|保留赌徒谬误辨析，明确独立；概率意义不仅是会算比值。
316|新增固定组数的组内平方和比较，3题含数值与约束解释；不引入聚类算法。
317|新增百分位意义，3题区分位置/阈值/原始分数；高中算法不作为先修。'''
nd={f'cnm_{a}':b for a,b in (line.split('|',1) for line in notes.splitlines())};ids=set(nd)
changedt={x['id'] for x in patch['topics']};changedq={x['id'] for x in patch['questions']}
rows=[]
for x in t:
 if x['id'] not in ids:continue
 rows.append({'topicId':x['id'],'name':x['name'],'action':'add' if x['id'] in ['cnm_316','cnm_317'] else 'revise' if x['id'] in changedt or any(z['topicId']==x['id'] and z['id'] in changedq for z in q) else 'retain','assessment':nd[x['id']],'questionIds':[z['id'] for z in q if z['topicId']==x['id']],'status':'assistant-reviewed-user-approved-rules','expertReviewed':False})
dump('node-review.json',rows)
dump('edge-review.json',[{'topicId':x['topicId'],'prerequisiteId':x['prerequisiteId'],'strength':x['strength'],'rationale':x['reason'],'decision':'retain-provisional' if x in load('reviews/math-junior/statistics/baseline-evidence.json')['dependencies'] else 'current-provisional','reviewNote':nd[x['topicId']]+' hard表示设计上的能力基础，不表示答对目标即可逻辑推出该先修已掌握。复合节点的子能力拆分留待后续。','expertReviewed':False} for x in e if x['topicId'] in ids])
dump('question-review.json',[{'questionId':x['id'],'topicId':x['topicId'],'contentSha256':hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'action':'changed-or-added' if x['id'] in changedq else 'retained','checking':'expression-check-plus-assistant-semantic-review' if 'verify' in x else 'assistant-semantic-review-not-independent-blind-solve','scoring':'manual-rubric' if x['type']=='self' else 'existing-answer-matcher','expertReviewed':False} for x in q if x['topicId'] in ids])
# Coverage is evidence-linked, not a claim that all skills have enough assessment.
old=load('reviews/math-junior/standards-audit.json')['rows'];sr=[]
for i in range(1,14):
 sid=f'cms-2022:4.SP.{i:02}';matched=[x for x in t if any(s['id']==sid for s in x['standards'])]
 sr.append({'standardId':sid,'topicIds':[x['id'] for x in matched],'status':'mapped-evidence-expanded-not-expert-certified','remaining':'需教师审核及真实任务表现；图表变式、调查活动与复测充分性尚未完成实证验证。','questionIds':[x['id'] for x in q if x['topicId'] in {a['id'] for a in matched}],'expertReviewed':False})
dump('requirements.json',sr)
release={'version':'statistics-2026-10.1','date':'2026-10-22','baseCommit':'831f8127e1f6d6729ccc099c3bea4fb627496cbd','acceptedCards':['S01','S02','S03','S04','S05','S06','S07'],'userDecision':'全部接受','expertReviewed':False,'counts':{'topics':len(t),'dependencies':len(e),'questions':len(q),'statisticsTopics':len(rows)},'changedQuestionIds':sorted(changedq),'historicalVerification':'原second_pass_log及_second_pass属于历史题面；本版本修改题目不继承独立盲解通过标记。新verification_report只报告当前表达式核验。','files':{n:hashlib.sha256((r/'data'/n).read_bytes()).hexdigest() for n in ['topics.json','dependencies.json','questions.json']}}
(r/'data/statistics-release.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
lines=['# 批次B：统计与概率修订结果','','7张卡已由用户于2026-10-22全部接受。此接受不代表教师审核；本批按已接受规则执行助手首轮内容审校。','','原43节点逐项检查，新增316（分组平方和）和317（百分位意义），统计共45节点。核心引擎的掌握推断规则尚未改动，仍须批次C处理。','','| 节点 | 动作 | 审校结论 |','|---|---|---|']
for x in rows:lines.append(f"| {x['topicId']} {x['name']} | {x['action']} | {x['assessment']} |")
lines+=['','## 运行与边界','','运行 `python3 scripts/build_statistics.py` 应用规范化修订；`--check`检查当前数据。补丁包含修改前后对象及前置hash，遇到上游漂移拒绝覆盖。所有未修改记录保持不变。旧脚本是分阶段生成器，不是全库重建入口；不要直接用build_primary.py覆盖当前全库（它带旧315节点断言并会丢其他阶段）。本批提供独立统计生成入口，不声称已修复全库历史构建链。','','当前所有13条统计内容要求均有引用与任务链接，仍不表示学业要求、全部教学提示、过程任务或实际掌握已经充分验证。绘图和报告题使用自评/教师判据，不强行自动判分。','','22个节点对象、61个题目对象及6个节点的出边组发生变化（以patch.json为准）；2节点新增，净增26题。修改过的题目不沿用历史盲解证明。两新节点暂放八下数据分析，并明确标注教材位置待核。','','数学旧会话留在原localStorage键，可在首页导出；新数据使用新会话键，避免用新题面解释旧答案。英语键不变。此措施只处理本次数据切换；通用迁移与证据模型留待批次C。','','批次A审计表是旧基线历史快照，不重写成新覆盖率。当前结果见本目录结构化node/edge/question审核与requirements.json。用户决定原文见statistics/decisions.json。']
(out/'README.md').write_text('\n'.join(lines)+'\n')
print('reviewed nodes',len(rows),'edges',sum(x['topicId'] in ids for x in e),'questions',sum(x['topicId'] in ids for x in q))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Author primary first-pass corrections against the frozen junior release.

This is an authoring entry point, not an upstream regeneration command.
The resulting guarded patch is the reproducible release input.
"""
import copy,json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
base={k:json.loads((ROOT/'data'/f'{k}.json').read_text()) for k in ['topics','questions','dependencies']}
patchpath=ROOT/'authoring/primary-2026-10/patch.json'
# Re-author from the original objects if an earlier draft has been applied.
if patchpath.exists():
 for k,changes in ((k,json.loads(patchpath.read_text())[k]) for k in base):
  for c in changes:
   field='topicId' if k=='dependencies' else 'id'
   found=[x for x in base[k] if x[field]==c['id']]
   actual=found if k=='dependencies' else found[0] if found else None
   if actual not in [c['before'],c['after']]:raise ValueError('Authoring drift: '+c['id'])
   if k=='dependencies':base[k]=[x for x in base[k] if x[field]!=c['id']]+copy.deepcopy(c['before'])
   elif c['before'] is None:base[k]=[x for x in base[k] if x[field]!=c['id']]
   else:base[k][base[k].index(found[0])]=copy.deepcopy(c['before'])
 order={tuple(x):i for i,x in enumerate(json.loads(patchpath.read_text())['baseDependencyOrder'])}
 base['dependencies'].sort(key=lambda x:order[(x['topicId'],x['prerequisiteId'])])
data=copy.deepcopy(base);ts={t['id']:t for t in data['topics']};qs={q['id']:q for q in data['questions']}
notes={}
def put(n,slot,prompt,answer,explanation,options=None,verify=None,figure=None):
 tid=f'cnm_p{n:03}';qid=f'{tid}_q{slot}'
 q={'id':qid,'topicId':tid,'difficulty':'basic' if slot<3 else 'standard','type':'choice' if options else 'numeric','prompt':prompt,'answer':str(answer),'explanation':explanation,'fixed_from_source':'小学首轮复核：直接测量本节点能力，撤去代列算式和答案提示。'}
 if options:
  if len(options)==2:options=options+['题目信息不足，无法判断']
  q['choices']=[{'key':chr(65+i),'text':s} for i,s in enumerate(options)]
 if verify is not None:q['verify']=verify
 if figure:q['figure']=figure
 qs[qid]=q
 if slot==1:ts[tid]['diagnostic_question']={'question':prompt,'answer':str(answer)}
 notes.setdefault(tid,[]).append(qid)
def num(n,s,p,a,e,v=None):put(n,s,p,a,e,verify=v)
def choice(n,s,p,opts,a,e):put(n,s,p,a,e,options=opts)

# Remove the worked expression only when a complete preceding context asks a question.
# Pure calculation exercises retain their expression.
for q in qs.values():
 if not q['topicId'].startswith('cnm_p'):continue
 p=q['prompt'];i=p.find('计算：')
 if i>0 and ('？' in p[:i] or '?' in p[:i]):
  q['prompt']=p[:i].strip()
  if '用小数作答' in p[i:]:q['prompt']+='（用小数作答）'
  q['fixed_from_source']='小学首轮复核：撤去题干中已经代列的算式，保留情境问题。'
  if q['id'].endswith('_q1'):ts[q['topicId']]['diagnostic_question']={'question':q['prompt'],'answer':q['answer']}

# Grade 1: cardinality, comparison, position, composition and modeling.
num(1,3,'数一数：● ● ● ● ●。一共有几个圆点？',5,'每个圆点数一次，共5个。')
num(1,4,'桌上有3支笔。要摆成5支，还需要添几支？',2,'3支再添2支成为5支。','5-3')
for s,a,b,key in [(1,4,2,'A'),(2,1,5,'B'),(4,3,3,'C')]:
 choice(2,s,f'{a}和{b}比较，正确的是哪一句？',[f'{a}大于{b}',f'{a}小于{b}',f'{a}等于{b}'],key,'可以用数数顺序或一一对应比较。')
choice(2,3,'一盘3个苹果，另一盘5个苹果。哪一盘多？',['3个的盘子','5个的盘子','两盘一样多'],'B','5比3大。')
num(3,1,'从左到右依次站着小兰、小明、小红、小军。小红从左数是第几个？',3,'从左数小兰第1，小明第2，小红第3。')
num(3,2,'从左到右依次站着小兰、小明、小红、小军。一共有几个小朋友？',4,'人数是4，区别于某个人的位置。')
num(3,3,'从左到右依次摆着：球、书、杯子。从右数，书是第几个？',2,'从右数杯子第1，书第2。')
choice(3,4,'“拿3支笔”和“拿第3支笔”一样吗？',['一样，都是拿3支','不一样，前者拿3支，后者拿1支','不一样，前者拿1支，后者拿3支'],'B','几个表示数量，第几个表示位置。')
num(4,1,'5个圆片分成两堆，一堆2个，另一堆几个？',3,'5可以分成2和3。','5-2')
num(4,2,'把4分成两部分，一部分是1，另一部分是几？',3,'4可以分成1和3。','4-1')
num(5,1,'盘子里一个苹果也没有，用哪个数表示苹果的个数？',0,'一个也没有用0表示。')
choice(5,2,'0和1比较，正确的是？',['0大于1','0小于1','0等于1'],'B','0比1小。')
num(8,4,'数一数：● ● ● ● ● ●。一共有几个圆点？',6,'逐个数，共6个。')
choice(9,1,'在9和6之间填什么符号？',['>','<','='],'A','9大于6。')
choice(9,2,'下面从小到大排列正确的是？',['10、7、8','7、8、10','8、7、10'],'B','先比较数的大小，再排序。')
choice(15,2,'小红面对黑板，书包放在她的背后。书包在小红的哪一边？',['前面','后面','上面'],'B','背后是后面。')
choice(15,3,'杯子在桌面上，球在桌子下面。球在杯子的哪一边？',['上方','下方','无法判断上下'],'B','球的位置低于杯子。')
choice(15,4,'小明和小红面对面站着，两人各举起右手。从小明身后看，他们的右手在同一侧吗？',['是','不是'],'B','面对面时，两人的左右方向相反。')
num(16,3,'1捆小棒有10根，再放6根，一共有多少根？',16,'1个十和6个一合成16。','10+6')
num(16,4,'20根小棒，每10根捆一捆，可以捆成几捆？',2,'20是2个十。','20/10')
choice(19,2,'用凑十法算8＋5，把5分成哪两个数，先让8凑成10？',['1和4','2和3','5和0'],'B','8先加2成为10，再加3。')
num(19,4,'用凑十法算7＋6，先从6中拿出几与7合成10？',3,'7差3成为10。','10-7')
choice(20,4,'用凑十法算9＋6，正确的一步是哪一个？',['10＋5','10＋6','9＋10'],'A','从6中拿1给9，剩下5。')
choice(22,1,'有红圆片、蓝圆片、红三角片。按颜色分，红圆片和哪一个放一组？',['蓝圆片','红三角片'],'B','分类标准是颜色。')
choice(22,2,'把红圆片和蓝圆片放在一起，把三角片另放一组，用的标准是什么？',['颜色','形状','摆放顺序'],'B','圆片与三角片按形状分组。')
num(22,3,'桌上有红圆片2个、蓝圆片3个、红三角片1个。按颜色分类，红色有几个？',3,'红圆片和红三角片同属红色。','2+1')
choice(22,4,'小明说“我家有4个人”。这里4表示什么？',['人数','一个人的位置','颜色'],'A','用数表示身边事物的数量。')
choice(24,1,'两个同样大的正方形，沿一条完整的边拼在一起，拼成什么图形？',['长方形','三角形','圆'],'A','两个正方形相邻拼接成一个长方形。')
choice(24,2,'把一个正方形沿对角线剪开，得到哪两个图形？',['两个三角形','两个圆','两个正方形'],'A','对角线把正方形分成两个三角形。')
choice(24,4,'把两个同样的三角形重新摆放拼图，所用小图形的个数会变吗？',['会，拼得长就更多','不会，仍是2个'],'B','位置变化不改变使用的块数。')
choice(29,1,'比较40和20，正确的是？',['40<20','40>20','40=20'],'B','十位上的4大于2。')
choice(29,2,'比较35和38，正确的是？',['35>38','35=38','35<38'],'C','十位相同，比较个位5和8。')
choice(29,4,'小丽有30颗珠子，小华比她多一些。小华最可能有多少颗？',['31颗','80颗','20颗'],'A','31比30只多1，符合多一些。')
choice(31,1,'计算27＋5时，个位7＋5＝12，十位应怎样处理？',['保持2不变','增加1','减少1'],'B','个位满十，向十位进1。')
choice(32,1,'用退位的方法算32－7，个位2不够减，应怎样做？',['向十位借1个十，个位变为12','向十位借1个一，个位变为3','直接用7－2'],'A','借1个十相当于10个一。')
choice(33,2,'竖式计算32＋5，5应和32中的哪个数字对齐？',['3','2','随便对齐'],'B','相同数位对齐，5与个位2对齐。')
choice(34,2,'验算52－18＝34，可以用哪道加法？',['34＋18＝52','52＋18＝70','34＋52＝86'],'A','差加减数应等于被减数。')
num(35,1,'一盒有35支笔，其中红笔15支，其余是蓝笔。蓝笔有多少支？',20,'总数减去红笔数得到蓝笔数。','35-15')
choice(35,2,'红球和蓝球共35个，红球15个。求蓝球个数，列式正确的是？',['35＋15','35－15','15－35'],'B','总数减去其中一部分。')

from primary_review_items import author
author(num,choice)

# Follow-through checks: full results instead of intermediate arithmetic.
choice(122,3,'一个三角形三条边分别为4厘米、4厘米、6厘米，按边分类属于哪一种？',['等腰三角形','等边三角形','三条边都不相等的三角形'],'A','两条边相等，是等腰三角形。')
for s,lengths,ans in [(2,'3、4、5','A'),(3,'2、3、5','B'),(4,'2、3、6','B')]:
 choice(123,s,f'三根小棒长度分别为{lengths}厘米，能围成三角形吗？',['能','不能'],ans,'最短两边之和必须严格大于最长边；等于也不能围成。')
num(124,2,'三角形两个角分别为60°和40°，第三个角多少度？',80,'180－60－40＝80。','180-60-40')
num(124,4,'一个直角三角形的一个锐角为30°，另一个锐角多少度？',60,'两个锐角之和90°。','90-30')
num(126,1,'买一本3.6元的本子，付10元，应找回多少元？',6.4,'付出的钱减去价格。','10-3.6')
num(126,2,'一根绳长2.5米，接上1.5米后总长多少米？',4,'两段长度相加。','2.5+1.5')
num(126,3,'两根绳子分别长1.8米和1.2米，合计多少米？',3,'把两段长度相加。','1.8+1.2')
num(126,4,'5米长的绳子剪去2.4米，还剩多少米？',2.6,'原长减剪去长度。','5-2.4')
num(129,4,'三次成绩是80、90、100分，平均成绩是多少分？',90,'总和270除以次数3。','(80+90+100)/3')
num(131,2,'鸡兔共8只，共26条腿。兔有几只？',5,'假设全是鸡16条腿，多10条，每只兔多2条，兔5只。','(26-8*2)/2')
num(131,3,'鸡兔共8只，共26条腿。鸡有几只？',3,'兔5只，鸡8－5＝3只。','8-(26-8*2)/2')
num(131,4,'鸡兔共10只，共28条腿。兔有几只？',4,'假设全是鸡20条腿，多8条，兔4只。','(28-10*2)/2')
choice(120,1,'1.2的小数点向右移动一位，得到哪个数？',['0.12','12','120'],'B','向右移动一位，扩大到10倍。')
choice(120,4,'把6.4缩小到原来的1/10，小数点怎样移动？',['向右一位','向左一位','向左两位'],'B','除以10，小数点向左一位。')
num(134,1,'每本练习本1.2元，买3本需多少元？',3.6,'单价乘数量。','1.2*3')
num(134,2,'每千克苹果8.5元，买0.4千克需多少元？',3.4,'8.5乘0.4。','8.5*0.4')
num(134,4,'每支笔1.25元，买8支共多少元？',10,'单价乘数量。','1.25*8')
num(135,3,'0.8×0.8的积保留一位小数是多少？',0.6,'积0.64，百分位4舍去。')
num(135,4,'2.5×1.25的积保留两位小数是多少？',3.13,'积3.125，千分位5，向百分位进1。')
num(147,4,'平行四边形底8厘米，对应的高3厘米，面积是多少平方厘米？',24,'底乘对应的高。','8*3')
num(148,4,'三角形底12厘米，对应的高4厘米，面积是多少平方厘米？',24,'底乘高除以2。','12*4/2')
num(149,4,'梯形上底5厘米、下底9厘米、高2厘米，面积是多少平方厘米？',14,'上下底之和乘高除以2。','(5+9)*2/2')
num(150,1,'两个区域恰好拼成一个图形，无重叠、无空隙，面积分别12和8平方厘米。总面积多少平方厘米？',20,'无重叠拼接，面积相加。','12+8')
num(150,2,'一个长6厘米、宽5厘米的长方形，剪去边长2厘米的正方形后，剩余面积多少平方厘米？',26,'长方形面积30减去正方形面积4。','6*5-2*2')
num(150,4,'长8厘米、宽5厘米的长方形内部挖去面积15平方厘米的图形，剩余面积多少平方厘米？',25,'总面积40减去15。','8*5-15')
num(163,4,'棱长4厘米的正方体，体积是多少立方厘米？',64,'棱长的三次方。','4**3')
choice(164,4,'一个杯子的容积指什么？',['杯子最多能容纳的液体体积','杯子外表面面积','杯子自身材料质量'],'A','容积是内部可容纳的体积。')
choice(189,2,'圆的周长与直径的比值是什么？',['π','2','半径'],'A','圆周率是圆的周长与直径的比值。')
choice(189,4,'大小不同的两个圆，周长与各自直径的比值怎样？',['相同，都是π','大圆的比值更大','小圆的比值更大'],'A','所有圆的周长与直径之比均为π。')
num(201,3,'温度计显示零下2摄氏度，用带正负号的数表示是多少摄氏度？',-2,'零下2摄氏度记为－2摄氏度。')
num(202,3,'约定上升记为正，电梯下降5层应记作多少层？',-5,'下降与上升意义相反，记为－5。')
num(206,3,'圆柱的两个底面之间的垂直距离为10厘米，它的高是多少厘米？',10,'圆柱高就是两个底面之间的垂直距离。')
num(207,4,'圆柱底面半径3厘米、高2厘米，体积是多少立方厘米？π取3.14。',56.52,'πr²h＝3.14×9×2。','3.14*3*3*2')
choice(209,1,'圆锥和圆柱等底等高，圆锥体积是圆柱的几分之几？',['1/2','1/3','3倍'],'B','必须同时等底等高，圆锥体积是圆柱的三分之一。')
num(211,3,'解比例：6:x＝2:5。x是多少？',15,'2x＝30，所以x＝15。','6*5/2')

# Statistics need an actual table/plot, not only arithmetic with a chart title.
num(9,4,'小红8颗糖，小明5颗糖，小红比小明多几颗？',3,'8比5多3。','8-5')
choice(43,3,'8个苹果，每2个装一袋，求装几袋，用什么算式？',['8÷2','8＋2','8－2'],'A','求8里面有几个2，用除法。')
num(55,4,'由2个千、3个百、4个十和5个一组成的数是多少？',2345,'按数位写出2345。')
num(59,1,'图书角原有20本书，添入15本，又借出8本，还剩多少本？',27,'先求添入后的数量，再减借出数量。','20+15-8')
num(59,2,'车上原有40人，第一站下车12人，第二站又下车10人，还剩几人？',18,'连续减去两站下车人数。','40-12-10')
num(110,4,'一道除法中除数5、商18、余数0，被除数是多少？',90,'除数乘商加余数。','5*18')
choice(114,4,'a＋b＝b＋a表示什么规律？',['加法交换律','加法结合律','乘法交换律'],'A','交换两个加数的位置，和不变。')
choice(115,4,'a×b＝b×a表示什么规律？',['乘法结合律','乘法交换律','加法交换律'],'B','交换两个因数的位置，积不变。')
choice(116,4,'a×（b＋c）等于哪个式子？',['a×b＋a×c','a×b＋c','a＋b×c'],'A','a要分别乘b和c。')
choice(117,1,'用乘法分配律简算99×5，哪种改写正确？',['100×5－5','100×5－1','99×（5－1）'],'A','99＝100－1，减去的是1×5。')
num(120,2,'把35缩小到原来的1/10，得到多少？',3.5,'小数点向左移动一位。','35/10')
choice(154,4,'下面哪个数同时是2和5的倍数？',['25','32','40'],'C','个位为0，同时是2和5的倍数。')
choice(170,4,'0.4化成最简分数是？',['4/10','2/5','4/100'],'B','4/10约分得2/5。')
num(195,1,'25%化成小数是多少？',0.25,'百分之二十五是0.25。','25/100')
num(195,4,'8%化成小数是多少？',0.08,'百分之八是0.08。','8/100')
num(196,4,'40千克的5%是多少千克？',2,'40乘5%。','40*5/100')
num(203,4,'原价200元的商品打七折，现价多少元？',140,'七折按原价70%计算。','200*7/10')
num(205,4,'原来200人，减少15%后还有多少人？',170,'减少30人，剩170人。','200*(1-15/100)')
from primary_review_figures import author_figures
author_figures(num,choice,qs)

# A complete node review does not imply that every skill in its criteria is tested.
# Remaining task families needing production/drawing are recorded in review output.
criteria={
52:['能结合情境解释商和余数','能判断剩余部分是否需要增加一个容器或舍去不足一份的部分'],
64:['能口算整十、整百及几百几十的加法','能解释相同计数单位相加'],
66:['能按情境选择合适的整十、整百数作估算','能比较估算与精确结果是否合理接近'],
93:['能用十分之一解释一位小数','能在具体量中表示一位小数并比较大小'],
167:['能把分子分母同时乘或除以同一个非零数','能说明分数大小不变，区别于分子分母同时加数'],
176:['在已知恰有一个次品且已知偏轻或偏重的条件下，能利用天平缩小范围','能说明每次称量的三种结果，并分析最坏情况下需要的次数'],
180:['能说明确定位置需要参照点、方向和距离','能解释北偏东等方向角，并在交换参照点时判断相反方向'],
186:['能把比的前后项同时除以公因数','能写出完整的最简整数比并保持前后顺序'],
193:['能指出扇形的两条半径和弧','能比较同一圆中不同圆心角对应扇形面积的大小'],
202:['能选定正方向和参照量','能用正负数表示具有相反意义的量'],
204:['能说明单利条件下利息＝本金×利率×期数，利率和期数的单位一致','能计算一年的利息并区分本金、利息和本息'],
}
for n,c in criteria.items():ts[f'cnm_p{n:03}']['mastery_criteria']=c
# Correct demonstrably irrelevant standards links and add evidenced statistical links.
for n in [151,176,216]:
 t=ts[f'cnm_p{n:03}'];t['standards']=[r for r in t['standards'] if r['id']!='cms-2022:3.NA.06']
 t['standards'].append({'id':'cms-2022:3.NA.10','confidence':'inferred'})
 t['scope_note']='教材中的问题解决专题；不是课标估算条款的直接内容。关联一般问题解决要求不代表国家课标逐项要求本题型。'
for n in [194,195,196,197,198,199,203,204,205]:
 t=ts[f'cnm_p{n:03}']
 for sid in ['cms-2022:3.SP.04','cms-2022:3.SP.05']:
  if not any(r['id']==sid for r in t['standards']):t['standards'].append({'id':sid,'confidence':'inferred'})
for n in [143,145,146,214]:
 t=ts[f'cnm_p{n:03}'];t['scope_note']='沿用教材型知识组织。2022小学内容要求未逐字列出本专题名称；相关等量关系或变化关系仅作教学关联，不据此声称该题型是国家课标独立考核要求。'
 for r in t['standards']:r['confidence']='inferred'
for q in qs.values():
 if q['topicId'].startswith('cnm_p') and q.get('fixed_from_source'):
  # Vary answer positions reproducibly without changing semantic choices.
  if q['type']=='choice':
   correct=next(c for c in q['choices'] if c['key']==q['answer'])
   shift=int(hashlib.sha256(q['id'].encode()).hexdigest()[:8],16)%len(q['choices'])
   q['choices']=q['choices'][shift:]+q['choices'][:shift]
   for i,c in enumerate(q['choices']):
    c['key']=chr(65+i)
    if c is correct:q['answer']=c['key']
  if q['id'].endswith('_q1'):ts[q['topicId']]['diagnostic_question']={'question':q['prompt'],'answer':q['answer']}

# Teaching sequence alone is not evidence of a necessary prerequisite.
soft_edges=[(14,1),(15,1),(23,14),(37,29),(56,41),(59,58),(88,78),(92,91),(99,77),(104,103),(115,114),(122,105),(128,127),(129,108),(136,82),(142,117),(148,147),(155,154),(158,157),(159,155),(165,153),(169,168),(171,128),(175,129),(177,173),(178,133),(192,190),(201,119),(204,203),(205,204),(208,207),(214,213)]
for n,p in soft_edges:
 d=next(d for d in data['dependencies'] if d['topicId']==f'cnm_p{n:03}' and d['prerequisiteId']==f'cnm_p{p:03}')
 d.update(strength='soft',reason=f'「{ts[d["prerequisiteId"]]["name"]}」可辅助学习或安排教学顺序，但答错不能证明「{ts[d["topicId"]]["name"]}」必然未掌握，不作硬性诊断阻断。')
# Add direct concepts where the old graph only named a preceding lesson.
for n,p,reason in [(122,101,'按角分类需要分辨锐角、直角和钝角。'),(159,153,'寻找公倍数需要理解倍数。'),(158,153,'寻找公因数需要理解因数。'),(175,108,'读取折线图需要理解统计图的数据刻度和对应关系。'),(180,82,'方向角表示位置需要理解方位。'),(180,100,'按角度描述方向需要角的度量。'),(208,206,'圆柱表面积需要认识底面与侧面。'),(208,192,'两个圆形底面的面积需要圆面积知识。'),(204,196,'按利率求利息需要求一个数的百分之几。')]:
 data['dependencies'].append({'topicId':f'cnm_p{n:03}','prerequisiteId':f'cnm_p{p:03}','strength':'hard','reason':reason})

def finish():
 data['topics']=[ts[t['id']] for t in data['topics']]
 data['questions']=[qs[q['id']] for q in data['questions']]+[q for id,q in qs.items() if id not in {x['id'] for x in base['questions']}]
 patch={'batch':'primary-2026-10.1','baseCommit':'06ed16f507119a52d21794bcd86a4763c7785208','baseDependencyOrder':[(d['topicId'],d['prerequisiteId']) for d in base['dependencies']],'topics':[],'questions':[],'dependencies':[]}
 for k in base:
  if k=='dependencies':
   for tid in sorted({d['topicId'] for d in base[k]+data[k]}):
    b=[d for d in base[k] if d['topicId']==tid];a=[d for d in data[k] if d['topicId']==tid]
    if a!=b:patch[k].append({'id':tid,'beforeHash':digest(b),'before':b,'after':a})
   continue
  old={x['id']:x for x in base[k]}
  for x in data[k]:
   b=old.get(x['id'])
   if x!=b:patch[k].append({'id':x['id'],'beforeHash':digest(b) if b is not None else None,'before':b,'after':x})
 patchpath.write_text(json.dumps(patch,ensure_ascii=False,indent=2)+'\n')
 print({k:len(patch[k]) for k in base})

if __name__=='__main__':finish()

# -*- coding: utf-8 -*-
"""Small inspectable SVG tasks with labelled units and non-colour-only keys."""
def svg(body,w=420,h=270):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><g fill="currentColor" font-size="15" font-family="sans-serif">{body}</g></svg>'
def text(x,y,s):return f'<text x="{x}" y="{y}">{s}</text>'
def line(x,y,xx,yy):return f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="currentColor" stroke-width="2"/>'
def plot(values,labels,kind='bar',second=None):
 b=text(10,20,'人数（人）' if kind=='bar' else '借书量（本）')
 for v in [0,5,10,15,20]:b+=text(15,225-v*8,str(v))+line(45,220-v*8,395,220-v*8)
 for i,(v,label) in enumerate(zip(values,labels)):
  x=85+i*90;b+=text(x-8,245,label)
  if kind=='bar':
   b+=f'<rect x="{x-15}" y="{220-v*8}" width="25" height="{v*8}" fill="currentColor" fill-opacity="0.65"/>'
   if second:
    v2=second[i];b+=f'<rect x="{x+13}" y="{220-v2*8}" width="25" height="{v2*8}" fill="none" stroke="currentColor" stroke-width="2"/>'
  else:
   b+=f'<circle cx="{x}" cy="{220-v*8}" r="4"/>'
   if i:b+=line(x-90,220-values[i-1]*8,x,220-v*8)
 if second:b+=text(190,20,'实心：一班  空心：二班')
 return svg(b)
def author_figures(num,choice,qs):
 def attach(n,s,figure):qs[f'cnm_p{n:03}_q{s}']['figure']=figure
 table='统计表：项目｜男生｜女生；跳绳｜12｜9；跑步｜8｜11。'
 num(85,3,table+'男生参加两个项目的人数合计多少？每人只参加一个项目。',20,'从男生一列取12和8相加。','12+8')
 choice(85,4,table+'要记录女生跑步的人数，应放在哪个位置？',['跳绳行、女生列','跑步行、女生列','跑步行、男生列'],'B','同时对准项目行和性别列。')
 bars=plot([10,15,5],['苹果','香蕉','梨'])
 num(108,2,'根据图中的条形统计图，喜欢香蕉的有多少人？',15,'香蕉条顶端对应15人刻度。')
 num(108,3,'根据条形统计图，喜欢香蕉的比喜欢苹果的多几人？',5,'读出15和10，相减得5。','15-10')
 choice(108,4,'根据条形统计图，喜欢哪种水果的人数最少？',['苹果','香蕉','梨'],'C','梨的条形最低，对应5人。')
 for s in [2,3,4]:attach(108,s,bars)
 grouped=plot([10,15,5],['跳绳','跑步','游泳'],second=[15,10,10])
 num(130,1,'读复式条形统计图，二班喜欢跳绳的有多少人？',15,'按图例读跳绳的空心条。')
 num(130,2,'读复式条形统计图，两个班喜欢跑步的共有多少人？',25,'一班15人加二班10人。','15+10')
 choice(130,3,'读复式条形统计图，哪项运动一班人数多于二班？',['跳绳','跑步','游泳'],'B','跑步一班15人，二班10人。')
 num(130,4,'读复式条形统计图，喜欢游泳的二班比一班多多少人？',5,'二班10人减一班5人。','10-5')
 for s in range(1,5):attach(130,s,grouped)
 curve=plot([10,15,5,20],['周一','周二','周三','周四'],'line')
 num(175,2,'读折线统计图，周三借出多少本书？',5,'周三的数据点对应5本。')
 choice(175,3,'读折线统计图，哪段相邻两天借书量增加最多？',['周一到周二','周二到周三','周三到周四'],'C','依次变化为加5、减10、加15。')
 num(175,4,'读折线统计图，周四比周一多借出多少本书？',10,'20减10。','20-10')
 for s in [2,3,4]:attach(175,s,curve)
 pie=svg('<circle cx="125" cy="130" r="85" fill="none" stroke="currentColor" stroke-width="2"/>'
  +'<path d="M125 130 L125 45 A85 85 0 0 1 125 215 Z" fill="currentColor" fill-opacity="0.25"/>'
  +line(125,45,125,215)+line(40,130,125,130)
  +text(142,125,'足球')+text(142,146,'50%')+text(57,100,'篮球')+text(57,120,'25%')+text(57,161,'其他')+text(57,181,'25%')
  +text(240,70,'全班40人')+text(240,98,'每人只选一项')+text(240,126,'最喜欢的运动'))
 num(199,2,'根据扇形统计图，全班40人，最喜欢篮球的有多少人？',10,'40的25%是10人。','40*25/100')
 choice(199,3,'根据扇形统计图，足球人数与篮球人数的比是？',['1:2','2:1','1:1'],'B','50%与25%之比为2:1。')
 choice(199,4,'若另一个班的足球比例也是50%，能仅凭比例判断两个班喜欢足球的人数相等吗？',['能','不能，还需要各班总人数'],'B','百分比相同，总量未必相同。')
 for s in [2,3,4]:attach(199,s,pie)
 # Actual geometric dissection: a diagonal divides one square into two triangles.
 figure=svg('<rect x="60" y="30" width="160" height="160" fill="none" stroke="currentColor" stroke-width="3"/>'+line(60,30,220,190),300,220)
 attach(24,2,figure)
 # A labelled ruler, including an offset origin, tests measurement rather than conversion.
 b=line(35,145,355,145)
 for v in range(9):b+=line(35+v*40,135,35+v*40,155)+text(30+v*40,180,str(v))
 b+=text(365,180,'cm')+'<rect x="115" y="95" width="200" height="30" fill="currentColor" fill-opacity="0.25"/>'+line(115,95,115,145)+line(315,95,315,145)
 attach(40,3,svg(b,420,210))
 # Correct the inherited lower ellipse visibility: top arc hidden, bottom arc visible.
 # This affects only primary figures containing the known cylinder template paths.
 import re
 for q in qs.values():
  if not q['topicId'].startswith('cnm_p'):continue
  containers=[q]+q.get('choices',[])
  for c in containers:
   f=c.get('figure','')
   if 'M 56 140 A 58 16' in f or (q['topicId']=='cnm_p207' and f):
    f=re.sub(r'(M 56 \d+ A \d+ \d+ 0 0 )([01])( \d+ \d+)',lambda m:m[1]+str(1-int(m[2]))+m[3],f)
    if q['id']=='cnm_p207_q1':f=f.replace('<text x="125.6" y="36"','<text x="125.6" y="18"')
    if q['id']=='cnm_p207_q2':f=f.replace('<text x="82.1" y="29"','<text x="82.1" y="17"')
    c['figure']=f;q['fixed_from_source']='小学首轮复核：圆柱底面后半弧虚线、前半弧实线。'

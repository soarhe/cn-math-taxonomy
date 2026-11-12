#!/usr/bin/env python3
"""Build additive curriculum nodes without altering the frozen diagnostic baseline."""
import json,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def build(check=False):
 rows=[]
 for line in (R/'authoring/primary-supplement/english-source-tasks.txt').read_text().splitlines():
  key,name,level,domain,locator,prompt,ref,criteria,wrong,partial=line.split('|')
  rows.append({'id':'cne_ps'+key,'name':name,'subject':'english','domain':domain,'grade':3 if level=='1' else 5,'semester':'跨册','chapter':'课标补充 · '+domain,'type':'procedural','description':'在实际任务中发展'+name+'；以独立表达、过程记录和作品作为观察依据。','mastery_criteria':criteria.split('；'),'external':False,'standards':[],'sourceReference':{'title':'义务教育英语课程标准（2022年版）','url':'https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582349487953.pdf','locator':'印刷页'+locator,'method':'按要求新编，非官方知识点编号或原文逐字转录'},'assessmentMode':'human-observation','root_reason':'跨任务课程能力；尚未验证先修边，不代表学习上没有前提。','diagnosticEnabled':False})
 overrides={'cne_p012':{'description':'观察实际图形中的颜色，结合文字判断图文是否一致；文字与图形冲突时指出并解释。'},'cne_p022':{'name':'食物喜好、想要与提供食物','description':'区分I like表达喜好、I would like表达想要；用Have some提供食物并回应。'},'cne_p049':{'name':'短元音与常见长元音对照'},'cne_p084':{'name':'学校场所与设施','description':'认读school、playground、library、computer；区分场所与设备，computer room才指计算机教室。'},'cne_p110':{'description':'用What is he like?询问人物特点（本节点侧重性格），与What does he like?询问喜好区分。'},'cne_p149':{'name':'Whose与物品归属','description':'用Whose dog is it?和It is mine.询问和说明归属；本节点本身不构成现在进行时要求。'}}
 out={'version':'primary-catalog-2026-11.1','baseline':'primary-2026-10.1','scope':'现有413节点的课程侧校正，加25个来自2022英语要求的能力节点；不宣称官方全文及词汇附录穷尽。','nodes':rows,'overrides':overrides}
 p=R/'data/primary-curriculum-supplement.json';s=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
 if check:assert p.read_text()==s
 else:p.write_text(s)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');build(p.parse_args().check)

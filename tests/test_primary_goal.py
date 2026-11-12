import json,unittest
from pathlib import Path
from fractions import Fraction
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text())
class GoalTests(unittest.TestCase):
 def test_all_existing_and_new_nodes_have_tasks_and_anchors(self):
  report=load('reviews/primary-supplement/completion.json')
  self.assertEqual(len(report['rows']),438)
  for key,n,nt in [('math',216,116),('english',222,103)]:
   c=report[key];self.assertEqual(c['knowledgePoints'],n);self.assertEqual(c['nodesWithTask'],n);self.assertEqual(c['taskCount'],nt);self.assertEqual(c['tasksWithCustomScoringExamples'],nt);self.assertFalse(c['unlinkedNodeIds'])
  for row in report['rows']:self.assertTrue(row['reviewEntryEvidence']);self.assertFalse(row['expertReviewed'])
 def test_specific_missing_capabilities_have_real_materials(self):
  tasks={t['id']:t for t in load('data/english-primary-activities.json')['tasks']}
  self.assertIn('Dear Jo',tasks['ep-node-message']['prompt']);self.assertIn('Amy is reading',tasks['ep-node-ongoing-read']['prompt'])
  self.assertIn('he、she、me、we',tasks['ep-node-long-e']['prompt']);self.assertIn('cne_p157',tasks['ep-node-route']['topicIds'])
  self.assertNotIn('cne_p194',tasks['ep-speak-weekend']['topicIds']);self.assertNotIn('cne_p197',tasks['ep-listen-weekend']['topicIds'])
 def test_math_new_references_independently_calculated(self):
  tasks={t['id']:t for t in load('data/primary-activities.json')['tasks']}
  values={'071':[368+457,705-268],'073':[124*3,203*4,230*4],'086':[23*14,18*12],'117':[25*16,125*24,99*37,48+76+52],'119':[47],'137':[24],'146':[32],'167':[str(Fraction(1,2)+Fraction(1,3)-Fraction(1,4))],'177':[str(Fraction(3,4)*3),str(Fraction(2,5)*4)],'203':[240*.8,1000*.02*2],'160':[2*(3*2+3*1+2*1),2*3.14*2*5+2*3.14*2**2]}
  for key,expected in values.items():
   for value in expected:self.assertIn(str(value).removesuffix('.0'),tasks['pact-node-'+key]['reference'])
 def test_supplement_does_not_invent_diagnostic_questions(self):
  cat=load('data/primary-curriculum-supplement.json');self.assertEqual(len(cat['nodes']),25)
  for n in cat['nodes']:self.assertFalse(n['diagnosticEnabled']);self.assertTrue(n['sourceReference']['locator']);self.assertNotIn('diagnostic_question',n)
  js=(R/'explore/app.js').read_text();self.assertIn('topic.diagnosticEnabled!==false',js);self.assertIn('curriculum.overrides',js)
 def test_no_generic_scoring_fallback(self):
  for t in load('data/primary-activities.json')['tasks']:
   self.assertEqual(len(t['scoringExample']['examples']),3);self.assertNotIn('提交证据显示未满足本项要求',t['scoringExample']['examples'][0])
  for t in load('data/english-primary-activities.json')['tasks']:
   self.assertEqual(len(t['scoringExamples']),3);self.assertNotIn('判分时逐项对应观察要求',t['scoringExamples'][0])
if __name__=='__main__':unittest.main()

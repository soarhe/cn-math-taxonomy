import hashlib,json,sys,unittest
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_primary_completion import build

def load(p):return json.loads((ROOT/p).read_text())
class CompletionTests(unittest.TestCase):
 def setUp(self):
  self.data=load('data/primary-activities.json');self.tasks={t['targetId']:t for t in self.data['tasks']}
 def test_all_original_findings_are_preserved_and_assigned(self):
  report=load('reviews/primary-completion/coverage.json');rows={r['targetId']:r for r in report['rows']}
  old=load('reviews/math-primary/coverage.json')['rows']
  self.assertEqual(len(rows),81)
  for r in old:
   now=rows[r['standardId']];self.assertEqual(now['previousFinding'],r['finding']);self.assertEqual(now['previousStatus'],r['coverage'])
   self.assertEqual(now['taskIds'],[self.tasks[r['standardId']]['id']]);self.assertEqual(now['contentStatus'],'authored-awaiting-review')
  self.assertEqual(len([r for r in rows.values() if r['kind']=='reference-example']),4)
 def test_build_is_reproducible(self):build(check=True)
 def test_no_dangling_relations_or_unsupported_mastery_claim(self):
  topics={t['id'] for t in load('data/topics.json')};ids={t['id'] for t in self.data['tasks']};targets=set(self.tasks)
  self.assertEqual(len(ids),81)
  for edge in self.data['relations']:
   self.assertIn(edge['from'],ids);self.assertIn(edge['to'],topics|targets)
   self.assertIn(edge['type'],['practises','addresses']);self.assertFalse(edge['diagnosticPropagation'])
  for t in self.tasks.values():
   self.assertFalse(t['autoMastery']);self.assertFalse(t['expertReviewed']);self.assertFalse(t['studentTrialCompleted']);self.assertEqual(t['assessmentMode'],'human-observation')
   self.assertGreaterEqual(len(t['instructions']),2);self.assertEqual(len(t['rubric']),3)
   self.assertEqual(t['gradeRange'],[t['stage']*2-1,t['stage']*2])
 def test_material_sources_resolve_and_media_is_not_synthetic(self):
  sources={s['id']:s for s in self.data['sources']}
  for t in self.tasks.values():
   for sid in t['sourceIds']:self.assertIn(sid,sources)
  for key in ['cms-2022:2.SP.04','cms-2022:3.SP.03']:
   self.assertIn('media-2024',self.tasks[key]['sourceIds']);self.assertIn('nbs-2024',self.tasks[key]['sourceIds'])
  self.assertIn('paper.people.com.cn/',sources['media-2024']['url'])
  self.assertIn('measure-history',self.tasks['cms-2022:2.IP.04']['sourceIds'])
 def test_reference_answers_by_independent_calculation(self):
  def has(sid,value):self.assertIn(str(value),self.tasks['cms-2022:'+sid]['reference'])
  has('2.NA.01',203*14);has('2.NA.01',672//21)
  has('2.NA.03',(180-3*24)//6);has('3.NA.06',float(Fraction(248,100)*19))
  has('2.SP.04',71909-68919);has('3.SP.03',71909+68919)
  has('3.SP.03',f'{71909/140828*100:.2f}');has('3.SP.03',f'{68919/140828*100:.2f}')
  has('3.NA.03',str(Fraction(3,4)));has('3.NA.04',str(Fraction(1,2)+Fraction(1,3)))
  has('3.SP.04',int((12+15)/(20+30)*100))
  has('3.NA.08',500*2//5);has('3.NA.08',500*3//5)
  has('3.NA.07',3*10+1)
 def test_frozen_diagnostic_data_and_audit_not_relabelled(self):
  lock=load('data/current-release.json')
  for name in ['topics.json','questions.json','dependencies.json','cn-curriculum-standards.json']:
   self.assertEqual(hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest(),lock['files'][name])
  old=load('reviews/math-primary/coverage.json');self.assertEqual(old['counts'],{'partial':67,'gap':10})
 def test_export_and_ui_have_no_diagnosis_writer(self):
  js=(ROOT/'activities/primary/app.js').read_text()
  self.assertIn("assessmentMode:'human-observation'",js);self.assertIn('autoMastery:false',js)
  self.assertIn("['','未观察']",js);self.assertNotIn('cnmDiagnose.session',js)
  self.assertIn('JSON.stringify(body,null,2)',js)
  explore=(ROOT/'explore/app.js').read_text();self.assertIn('primary-activities.json',explore);self.assertIn("'../activities/primary/?topic='",explore)
if __name__=='__main__':unittest.main()

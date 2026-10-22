import copy,json,sys,tempfile,unittest
from pathlib import Path
from decimal import Decimal
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_algebra_d2 import build,digest

def load(p):return json.loads((ROOT/p).read_text())
PATCH=load('authoring/algebra-d2-2026-10/patch.json')
class AlgebraD2BuildTests(unittest.TestCase):
 def fixture(self,r):
  (r/'data').mkdir();(r/'authoring/algebra-d2-2026-10').mkdir(parents=True)
  (r/'authoring/algebra-d2-2026-10/patch.json').write_text(json.dumps(PATCH))
  for k in ['topics','questions','dependencies']:
   rows=load('data/'+k+'.json')
   for c in PATCH[k]:
    rows=[x for x in rows if x['id']!=c['id']]
    if c['before'] is not None:rows.append(copy.deepcopy(c['before']))
   (r/'data'/f'{k}.json').write_text(json.dumps(rows))
 def test_rebuild_preserves_unrelated_and_is_idempotent(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r)
   originals={k:json.loads((r/'data'/f'{k}.json').read_text()) for k in ['topics','questions','dependencies']}
   for k in ['topics','questions']:
    for c in PATCH[k]:self.assertEqual(c['beforeHash'],digest(c['before']) if c['before'] else None)
   out=build(r);build(r,True)
   for k in ['topics','questions']:
    ids={c['id'] for c in PATCH[k]}
    self.assertEqual([x for x in originals[k] if x['id'] not in ids],[x for x in out[k] if x['id'] not in ids])
   self.assertEqual(originals['dependencies'],out['dependencies'])
   b={p.name:p.read_bytes() for p in (r/'data').glob('*.json')};build(r)
   self.assertEqual(b,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_question_drift_does_not_partially_write_topics(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);p=r/'data/questions.json';qs=json.loads(p.read_text())
   next(q for q in qs if q['id']=='cnm_030_q1')['prompt']='independent edit';p.write_text(json.dumps(qs))
   b={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):build(r)
   self.assertEqual(b,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_audit_evidence_and_version_migration(self):
  qs={q['id']:q for q in load('data/questions.json')}
  inv=load('reviews/math-junior/batch-d2/topic-inventory.json');self.assertEqual(len(inv),142)
  self.assertEqual(sum(x['status']=='targeted-revision' for x in inv),25)
  req=load('reviews/math-junior/batch-d2/requirements.json');self.assertEqual(len(req),49)
  self.assertEqual(sum(x['coverage']=='partial' for x in req),25)
  for row in req:
   self.assertIn(row['coverage'],['partial','pending']);self.assertFalse(row['expertReviewed'])
   for qid in row['evidenceQuestionIds']:self.assertIn(qid,qs)
  for row in load('reviews/math-junior/batch-d2/question-review.json'):
   self.assertEqual(row['contentSha256'],digest(qs[row['questionId']]))
  app=(ROOT/'diagnose/app.js').read_text()
  self.assertIn("const DATA_VERSION = 'algebra-2026-10.2'",app)
  self.assertIn('cnmDiagnose.session.algebra-2026-10.1.evidence-1.1',app)
  self.assertEqual(load('data/current-release.json')['counts']['questions'],6224)
  build(ROOT,True)
 def test_process_tasks_and_mathematical_invariants(self):
  added=[c['after'] for c in PATCH['questions'] if c['before'] is None]
  self.assertEqual(len(added),20)
  self.assertTrue(all(q['type']=='self' and len(q['rubric'])>=3 for q in added))
  for q in added:
   if 'figure' in q:
    svg=ET.fromstring(q['figure']);self.assertEqual(svg.attrib['role'],'img');self.assertTrue(svg.attrib['aria-label'])
  # Independent numerical boundary checks, not proof of the general statements.
  self.assertTrue(Decimal('1.4')**2<2<Decimal('1.5')**2)
  self.assertTrue(Decimal('3.1')**2<10<Decimal('3.2')**2)
  self.assertGreater(5,Decimal('2.2')**2)
  for n in range(-20,21):
   self.assertEqual((n*n+n)%2,0)
   self.assertEqual(((2*n+1)**2-(2*n-1)**2)%8,0)
  # Count grid edges independently from the shared-edge formula in the answer.
  self.assertEqual(2*25+(25+1),76)
  self.assertEqual([(t,100-5*t) for t in (0,10,20)],[(0,100),(10,50),(20,0)])
if __name__=='__main__':unittest.main()

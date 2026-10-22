import copy,json,sys,tempfile,unittest
from pathlib import Path
from decimal import Decimal
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_algebra_d3 import build,digest

def load(p):return json.loads((ROOT/p).read_text())
PATCH=load('authoring/algebra-d3-2026-10/patch.json')
class AlgebraD3BuildTests(unittest.TestCase):
 def fixture(self,r):
  (r/'data').mkdir();(r/'authoring/algebra-d3-2026-10').mkdir(parents=True)
  (r/'authoring/algebra-d3-2026-10/patch.json').write_text(json.dumps(PATCH))
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
   next(q for q in qs if q['id']=='cnm_098_q1')['prompt']='independent edit';p.write_text(json.dumps(qs))
   b={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):build(r)
   self.assertEqual(b,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_review_and_release(self):
  qs={q['id']:q for q in load('data/questions.json')}
  inv=load('reviews/math-junior/batch-d3/topic-inventory.json')
  self.assertEqual(len(inv),142);self.assertEqual(sum(x['status']=='targeted-revision' for x in inv),31)
  req=load('reviews/math-junior/batch-d3/requirements.json')
  self.assertEqual(len(req),49);self.assertEqual(sum(x['coverage']=='partial' for x in req),30)
  for x in req:
   self.assertFalse(x['expertReviewed']);self.assertIn(x['coverage'],['partial','pending'])
   for qid in x['evidenceQuestionIds']:self.assertIn(qid,qs)
  for x in load('reviews/math-junior/batch-d3/question-review.json'):
   self.assertEqual(x['contentSha256'],digest(qs[x['questionId']]))
  app=(ROOT/'diagnose/app.js').read_text()
  self.assertIn("const DATA_VERSION = '"+load('data/current-release.json')['version']+"'",app)
  self.assertIn('cnmDiagnose.session.algebra-2026-10.2.evidence-1.1',app)
  self.assertEqual(load('reviews/math-junior/batch-d2/release.json')['counts']['questions'],6224)
  self.assertEqual(load('reviews/math-junior/batch-d3/release.json')['counts']['questions'],6236)
  build(ROOT,True)
 def test_tasks_domains_and_reference_values(self):
  from fractions import Fraction as F
  added=[c['after'] for c in PATCH['questions'] if c['before'] is None]
  self.assertEqual(len(added),12)
  self.assertTrue(all(q['type']=='self' and len(q['rubric'])>=3 for q in added))
  # Independent finite-domain checks for integer feasibility, not blind solving.
  self.assertEqual([n for n in range(20) if 3*n+5==26],[7])
  self.assertFalse(any(n+(n+4)==45 for n in range(46)))
  self.assertEqual([(x,20-x) for x in range(21) if 30*x+15*(20-x)==420],[(8,12)])
  self.assertEqual(2*2+3*3,13);self.assertEqual(2*5+3*1,13)
  self.assertEqual(max(n for n in range(20) if 8+6*n<=50),7)
  self.assertEqual(min(n for n in range(20) if 45*n>=160),4)
  self.assertEqual(F(3,2),F(6,4))
  self.assertEqual(F(12,4),F(36,12))
  self.assertEqual(F(36,-21+3),F(48,-21-3))
  self.assertLess(-21,3)  # algebraic solution violates forward upstream travel
  qs={q['id']:q for q in load('data/questions.json')}
  self.assertEqual(qs['cnm_166_q3']['curriculum_scope'],'supplementary')
  self.assertEqual(qs['cnm_166_q3']['difficulty'],'advanced')
if __name__=='__main__':unittest.main()

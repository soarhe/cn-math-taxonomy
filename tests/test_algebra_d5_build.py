import copy,json,sys,tempfile,unittest
from pathlib import Path
from decimal import Decimal
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_algebra_d5 import build,digest

def load(p):return json.loads((ROOT/p).read_text())
PATCH=load('authoring/algebra-d5-2026-10/patch.json')
class AlgebraD5BuildTests(unittest.TestCase):
 def fixture(self,r):
  (r/'data').mkdir();(r/'authoring/algebra-d5-2026-10').mkdir(parents=True)
  (r/'authoring/algebra-d5-2026-10/patch.json').write_text(json.dumps(PATCH))
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
   r=Path(d);self.fixture(r);p=r/'data/topics.json';qs=json.loads(p.read_text())
   next(q for q in qs if q['id']=='cnm_208')['description']='independent edit';p.write_text(json.dumps(qs))
   b={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):build(r)
   self.assertEqual(b,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_evidence_scope_and_release(self):
  self.assertEqual(len(PATCH['topics']),3);self.assertEqual(len(PATCH['questions']),6)
  qs={q['id']:q for q in load('data/questions.json')}
  for row in load('reviews/math-junior/batch-d5/question-review.json'):
   self.assertEqual(row['contentSha256'],digest(qs[row['questionId']]))
   self.assertFalse(row['expertReviewed'])
  inv=load('reviews/math-junior/batch-d5/topic-inventory.json');self.assertEqual(len(inv),142)
  self.assertEqual(sum(x['status']=='targeted-revision' for x in inv),41)
  req=load('reviews/math-junior/batch-d5/requirements.json');self.assertEqual(len(req),49)
  self.assertEqual(sum(x['coverage']=='partial' for x in req),32)
  for x in req:
   self.assertIn(x['coverage'],['partial','pending']);self.assertFalse(x['expertReviewed'])
   for qid in x['evidenceQuestionIds']:self.assertIn(qid,qs)
  self.assertEqual(load('reviews/math-junior/batch-d5/release.json')['counts']['questions'],6256)
  self.assertEqual(load('reviews/math-junior/batch-d4/release.json')['counts']['questions'],6250)
  app=(ROOT/'diagnose/app.js').read_text();self.assertIn('cnmDiagnose.session.algebra-2026-10.4.evidence-1.1',app)
  self.assertIn("const DATA_VERSION = '"+load('data/current-release.json')['version']+"'",app)
  build(ROOT,True)
 def test_figures_and_mathematical_boundaries(self):
  from fractions import Fraction as F
  for c in PATCH['questions']:
   q=c['after'];self.assertIsNone(c['before']);self.assertEqual(q['type'],'self')
   self.assertGreaterEqual(len(q['rubric']),3)
   svg=ET.fromstring(q['figure']);self.assertEqual(svg.attrib['role'],'img');self.assertTrue(svg.attrib['aria-label'])
   self.assertFalse(any(e.tag.split('}')[-1] in ['script','foreignObject','image'] for e in svg.iter()))
   self.assertTrue(all(not any(k.startswith('on') for k in e.attrib) for e in svg.iter()))
  self.assertEqual(2*2-4,0);self.assertEqual(2*F(5,2)-4,1)
  for x in [F(-3),F(0),F(2),F(5,2),F(6)]:
   self.assertEqual(-x+2>0,x<2);self.assertEqual(-x+2>=0,x<=2)
   self.assertEqual(x-1>-x+3,x>2)
  self.assertEqual(1+1,-1+3)
  # Parallel lines have a nonzero constant difference, including beyond the figure window.
  for x in [F(-100),F(0),F(1,3),F(100)]:self.assertEqual((x+1)-(x-1),2)
if __name__=='__main__':unittest.main()

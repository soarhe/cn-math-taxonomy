import copy,hashlib,json,sys,tempfile,unittest
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_algebra import build,digest
from validate import question_errors
PATCH=json.loads((ROOT/'authoring/algebra-2026-10/patch.json').read_text())
def load(p):return json.loads((ROOT/p).read_text())
class AlgebraBuildTests(unittest.TestCase):
 def fixture(self,root,baseline=False):
  (root/'data').mkdir();(root/'authoring/algebra-2026-10').mkdir(parents=True)
  (root/'authoring/algebra-2026-10/patch.json').write_text(json.dumps(PATCH))
  for k in ['topics','questions','dependencies']:
   data=load('data/'+k+'.json')
   if baseline:
    for c in PATCH[k]:
     field='topicId' if k=='dependencies' else 'id';data=[x for x in data if x[field]!=c['id']]
     if k=='dependencies':data+=copy.deepcopy(c['before'])
     elif c['before'] is not None:data.append(copy.deepcopy(c['before']))
   (root/'data'/f'{k}.json').write_text(json.dumps(data,ensure_ascii=False))
 def test_patch_preimages_and_preservation(self):
  for k in ['topics','questions','dependencies']:
   for c in PATCH[k]:self.assertEqual(c['beforeHash'],digest(c['before']) if c['before'] is not None else None)
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r,True)
   originals={k:json.loads((r/'data'/f'{k}.json').read_text()) for k in ['topics','questions','dependencies']}
   out=build(r)
   for k,data in originals.items():
    field='topicId' if k=='dependencies' else 'id';ids={c['id'] for c in PATCH[k]}
    self.assertEqual([x for x in data if x[field] not in ids],[x for x in out[k] if x[field] not in ids])
   build(r,True)
 def test_idempotent_and_drift_safe(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);build(r)
   before={p.name:p.read_bytes() for p in (r/'data').glob('*.json')};build(r)
   self.assertEqual(before,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r,True);p=r/'data/questions.json';qs=json.loads(p.read_text());next(q for q in qs if q['id']=='cnm_p121_q1')['answer']='other edit';p.write_text(json.dumps(qs))
   before={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):build(r)
   self.assertEqual(before,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_review_scope_no_false_certification(self):
  req=load('reviews/math-junior/batch-d1/requirements.json');self.assertEqual(len(req),49)
  self.assertEqual(sum(r['requirementType']=='optional' for r in req),1)
  self.assertTrue(all(not r['expertReviewed'] for r in req))
  self.assertTrue(all(r['coverage'] in ('partial','pending') for r in req))
  self.assertEqual(sum(r['coverage']=='pending' for r in req),34)
  inv=load('reviews/math-junior/batch-d1/topic-inventory.json');self.assertEqual(len(inv),142)
  self.assertEqual(sum(r['status']=='targeted-revision' for r in inv),15)
  byid={q['id']:q for q in load('data/questions.json')}
  for row in req:
   for qid in row['evidenceQuestionIds']:self.assertIn(qid,byid)
  self.assertEqual(len(load('reviews/math-junior/batch-d1/question-review.json')),47)
 def test_current_release_and_stable_ids(self):
  lock=load('data/current-release.json')
  for n,sha in lock['files'].items():self.assertEqual(hashlib.sha256((ROOT/'data'/n).read_bytes()).hexdigest(),sha)
  for n,sha in lock['authoring'].items():self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),sha)
  for c in PATCH['topics']:self.assertEqual(c['before']['id'],c['after']['id'])
  self.assertEqual(lock['counts']['topics'],1505)
  self.assertEqual(lock['counts']['questions'],6204)
  build(ROOT,True)
 def test_rubric_and_scope_validation(self):
  q=next(q for q in load('data/questions.json') if q['id']=='cnm_018_q6');t={q['topicId']:{'external':False}}
  self.assertEqual(question_errors([q],t,False)[0],[])
  for changes in [{'rubric':[]},{'rubric':['']},{'rubric':'fake'},{'curriculum_scope':'fake'},{'type':'short'}]:
   self.assertTrue(question_errors([{**q,**changes}],t,False)[0])
 def test_numeric_reference_values_by_alternative_calculation(self):
  qs={q['id']:q for q in load('data/questions.json')}
  # Decimal place-value rounding uses a different algorithm from the published verify expressions.
  for qid,value,unit in [('cnm_p121_q1','3.8','1'),('cnm_p121_q2','6.3','1'),('cnm_p121_q3','2.46','.1'),('cnm_023_q1','.03586','.001')]:
   self.assertEqual(Decimal(qs[qid]['answer']),Decimal(value).quantize(Decimal(unit),rounding=ROUND_HALF_UP))
  self.assertEqual(Decimal('7.8')*Decimal('12.6'),Decimal('98.28'))
  self.assertIn('98.3',qs['cnm_023_q4']['answer'])
  self.assertTrue(Decimal('2.645')**2 < 7 < Decimal('2.655')**2)
  self.assertTrue(Decimal('2.705')**3 < 20 < Decimal('2.715')**3)
  self.assertTrue(Decimal('2.145')**3 < 10 < Decimal('2.155')**3)
  self.assertEqual((-12)*3+50,14)
  for n,c,x in [(5,2,Decimal('1.4')),(6,3,Decimal('1.7'))]:
   self.assertTrue((x-Decimal('.05'))**2<c<(x+Decimal('.05'))**2)
   self.assertIn(str(x),qs[f'cnm_234_q{n}']['answer'])
 def test_question_review_hashes(self):
  qs={q['id']:q for q in load('data/questions.json')}
  for row in load('reviews/math-junior/batch-d1/question-review.json'):
   self.assertEqual(digest(qs[row['questionId']]),row['contentSha256'])
if __name__=='__main__':unittest.main()

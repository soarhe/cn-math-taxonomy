import copy,hashlib,json,math,shutil,sys,tempfile,unittest
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_primary_review import build,digest
def load(p):return json.loads((ROOT/p).read_text())
class PrimaryReviewTests(unittest.TestCase):
 def test_current_patch_outputs(self):build(check=True)
 def fixture(self,r):
  (r/'data').mkdir();(r/'authoring/primary-2026-10').mkdir(parents=True)
  for n in ['topics','questions','dependencies','cn-curriculum-standards']:shutil.copyfile(ROOT/'data'/f'{n}.json',r/'data'/f'{n}.json')
  for p in (ROOT/'authoring/primary-2026-10').glob('*.json'):shutil.copyfile(p,r/'authoring/primary-2026-10'/p.name)
 def test_exact_historical_reconstruction_and_reapply(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);current={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   build(r,reverse=True)
   for n,h in load('reviews/math-primary/base-release.json')['files'].items():self.assertEqual(hashlib.sha256((r/'data'/n).read_bytes()).hexdigest(),h,n)
   build(r);build(r,check=True);build(r)
   self.assertEqual(current,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_drift_is_atomic(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);build(r,reverse=True);p=r/'data/questions.json';q=json.loads(p.read_text());q[0]['answer']='unexpected';p.write_text(json.dumps(q));before={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   # p001 q1 is unchanged, so corrupt an actual patched item.
   qid=load('authoring/primary-2026-10/patch.json')['questions'][-1]['id'];next(x for x in q if x['id']==qid)['answer']='drift';p.write_text(json.dumps(q));before={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'drift'):build(r)
   self.assertEqual(before,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_all_216_snapshots_and_77_evidence_decisions(self):
  ts=load('data/topics.json');qs=load('data/questions.json');ds=load('data/dependencies.json');rows=load('reviews/math-primary/node-review.json')['rows'];byid={t['id']:t for t in ts}
  ids={t['id'] for t in ts if t['id'].startswith('cnm_p')};self.assertEqual(len(rows),216);self.assertEqual({r['topicId'] for r in rows},ids)
  for r in rows:
   tid=r['topicId'];self.assertEqual(r['currentSnapshotSha256'],digest({'topic':byid[tid],'questions':[q for q in qs if q['topicId']==tid],'dependencies':[d for d in ds if d['topicId']==tid]}));self.assertFalse(r['expertReviewed'])
  ss={s['id'] for s in load('data/cn-curriculum-standards.json')['items'] if s['id'].startswith(('cms-2022:1.','cms-2022:2.','cms-2022:3.'))};cov=load('reviews/math-primary/coverage.json')['rows'];self.assertEqual(len(cov),77);self.assertEqual({r['standardId'] for r in cov},ss)
  for r in cov:
   self.assertEqual(bool(r['evidenceQuestionIds']),r['coverage']=='partial');self.assertTrue(r['finding'])
   self.assertTrue(set(r['evidenceQuestionIds'])<={q['id'] for q in qs if q['topicId'] in ids})
 def test_changes_stay_within_primary(self):
  p=load('authoring/primary-2026-10/patch.json')
  for kind in ['topics','questions','dependencies']:
   for c in p[kind]:self.assertTrue(c['id'].startswith('cnm_p'))
  # Junior review still describes exact current topics/questions/edges.
  ts=load('data/topics.json');qs=load('data/questions.json');ds=load('data/dependencies.json')
  for r in load('reviews/release-candidate/node-review.json')['rows']:
   tid=r['topicId'];self.assertEqual(r['currentSnapshotSha256'],digest({'topic':next(t for t in ts if t['id']==tid),'questions':[q for q in qs if q['topicId']==tid],'dependencies':[d for d in ds if d['topicId']==tid]}))
 def test_application_rounding_number_theory_and_measurement_answers(self):
  q={x['id']:x for x in load('data/questions.json')}
  expected={'052_q1':math.ceil(23/5),'052_q2':19//4,'052_q3':math.ceil(28/6),'052_q4':50//8,'158_q1':math.gcd(12,8),'158_q2':math.gcd(18,24),'158_q3':math.gcd(20,30),'158_q4':math.gcd(8,15),'145_q3':(17-5)/2,'208_q1':2*math.pi*1*1+2*math.pi*1*2,'040_q3':7-2,'131_q2':(26-8*2)/2,'216_q3':math.ceil(7/3)}
  expected['208_q1']=2*3.14*1*1+2*3.14*1*2
  for key,val in expected.items():self.assertAlmostEqual(float(q['cnm_p'+key]['answer']),val)
  for key,a,b,places in [('135_q1','1.6','2.4','0.1'),('135_q2','2.7','1.3','0.1'),('135_q4','2.5','1.25','0.01')]:
   self.assertEqual(Decimal(q['cnm_p'+key]['answer']),(Decimal(a)*Decimal(b)).quantize(Decimal(places),rounding=ROUND_HALF_UP))
 def test_graph_no_cycles_and_no_false_hard_sequence(self):
  ds=load('data/dependencies.json');edges={(d['topicId'],d['prerequisiteId']):d['strength'] for d in ds}
  for a,b in [(14,1),(104,103),(201,119),(204,203),(208,207)]:self.assertEqual(edges[(f'cnm_p{a:03}',f'cnm_p{b:03}')],'soft')
  for a,b in [(122,101),(159,153),(180,100),(208,192)]:self.assertEqual(edges[(f'cnm_p{a:03}',f'cnm_p{b:03}')],'hard')
 def test_source_errata_and_migration(self):
  ss={s['id']:s for s in load('data/cn-curriculum-standards.json')['items']};self.assertIn('平方厘米',ss['cms-2022:2.GG.03']['text']);self.assertIn('平方千米',ss['cms-2022:3.GG.03']['text']);self.assertIn('50',ss['cms-2022:3.IP.01']['page_or_ref'])
  app=(ROOT/'diagnose/app.js').read_text();self.assertIn('cnmDiagnose.session.junior-2026-10.1.evidence-1.2',app);self.assertIn("const DATA_VERSION = 'primary-2026-10.1'",app)
if __name__=='__main__':unittest.main()

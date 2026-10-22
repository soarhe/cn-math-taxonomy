import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
class ReleaseCandidateTests(unittest.TestCase):
 def test_all_patch_preimages_and_current_outputs(self):
  for p in sorted((ROOT/'authoring/release-candidate').glob('*.json')):
   a=json.loads(p.read_text())
   for k in ['topics','questions','dependencies']:
    data=load('data/'+k+'.json')
    for c in a[k]:
     self.assertEqual(c['beforeHash'],digest(c['before']) if c['before'] is not None else None)
     field='topicId' if k=='dependencies' else 'id';found=[x for x in data if x[field]==c['id']]
     self.assertEqual(found if k=='dependencies' else found[0],c['after'],p.name+'/'+c['id'])
 def test_complete_review_and_coverage_sets(self):
  ts=load('data/topics.json'); qs={q['id']:q for q in load('data/questions.json')};ds=load('data/dependencies.json')
  ids={t['id'] for t in ts if t['id'].startswith('cnm_') and t.get('grade') in [7,8,9]}
  rows=load('reviews/release-candidate/node-review.json')['rows']
  self.assertEqual(len(rows),317);self.assertEqual({r['topicId'] for r in rows},ids)
  for r in rows:
   tid=r['topicId'];snap={'topic':next(t for t in ts if t['id']==tid),'questions':[q for q in qs.values() if q['topicId']==tid],'dependencies':[d for d in ds if d['topicId']==tid]}
   self.assertEqual(r['currentSnapshotSha256'],digest(snap));self.assertFalse(r['expertReviewed'])
  coverage=load('reviews/release-candidate/coverage.json')['rows'];self.assertEqual(len(coverage),157)
  expected={s['id'] for s in load('data/cn-curriculum-standards.json')['items'] if s['id'].startswith('cms-2022:4.')}
  self.assertEqual({r['standardId'] for r in coverage},expected)
  for r in coverage:
   self.assertIn(r['coverage'],['partial','gap']);self.assertTrue(r['finding']);self.assertFalse(r['expertReviewed'])
   for qid in r['evidenceQuestionIds']:self.assertIn(qid,qs)
   if r['coverage']=='gap':self.assertEqual(r['evidenceQuestionIds'],[])
 def test_direct_primary_bridges_exact_inventory(self):
  ts=load('data/topics.json');ds=load('data/dependencies.json');junior={t['id'] for t in ts if t['id'].startswith('cnm_') and t.get('grade') in [7,8,9]}
  expected={d['prerequisiteId'] for d in ds if d['topicId'] in junior and d['prerequisiteId'].startswith('cnm_p')}
  rows=load('reviews/release-candidate/primary-bridges.json')['rows'];self.assertEqual(len(rows),28);self.assertEqual({r['topicId'] for r in rows},expected)
 def test_no_required_node_hard_depends_on_optional_or_supplementary(self):
  ts={t['id']:t for t in load('data/topics.json')}
  for d in load('data/dependencies.json'):
   t=ts[d['topicId']];p=ts[d['prerequisiteId']]
   if t['id'].startswith('cnm_') and t.get('grade') in [7,8,9] and t.get('curriculum_scope') not in ['optional','supplementary'] and d['strength']=='hard':
    self.assertNotIn(p.get('curriculum_scope'),['optional','supplementary'],str(d))
 def test_corrected_math_counterexamples(self):
  qs={q['id']:q for q in load('data/questions.json')}
  self.assertEqual(qs['cnm_p194_q4']['answer'],'1')
  self.assertEqual(qs['cnm_p159_q3']['answer'],'8')
  self.assertEqual(qs['cnm_112_q5']['curriculum_scope'],'supplementary')
  # The repaired incircle/perimeter data admit a 9-12-15 triangle.
  self.assertEqual(9*12/2,3*(9+12+15)/2)
  self.assertIn('36',qs['cnm_128_q5']['prompt'])
 def test_builder_drift_atomicity_and_idempotence(self):
  name='primary_bridges';spec=importlib.util.spec_from_file_location('rc_builder',ROOT/f'scripts/build_rc_{name}.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  patch=load('authoring/release-candidate/primary-bridges.json')
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'data').mkdir();(r/'authoring/release-candidate').mkdir(parents=True);(r/'authoring/release-candidate/primary-bridges.json').write_text(json.dumps(patch))
   for k in ['topics','questions','dependencies']:
    data=load('data/'+k+'.json');before={c['id']:c['before'] for c in patch[k]};data=[copy.deepcopy(before.get(x.get('id'),x)) for x in data];(r/'data'/f'{k}.json').write_text(json.dumps(data))
   p=r/'data/questions.json';good=p.read_text();data=json.loads(good);next(q for q in data if q['id']=='cnm_p085_q1')['answer']='unexpected edit';p.write_text(json.dumps(data));snap={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):mod.build(r)
   self.assertEqual(snap,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
   p.write_text(good);mod.build(r);snap={p.name:p.read_bytes() for p in (r/'data').glob('*.json')};mod.build(r);mod.build(r,True);self.assertEqual(snap,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
if __name__=='__main__':unittest.main()

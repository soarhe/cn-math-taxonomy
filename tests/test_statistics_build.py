import copy,json,sys,tempfile,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_statistics import build
PATCH=json.loads((ROOT/'authoring/statistics-2026-10/patch.json').read_text())
class StatisticsBuildTests(unittest.TestCase):
 def fixture(self,root,baseline=False):
  (root/'data').mkdir();(root/'authoring/statistics-2026-10').mkdir(parents=True)
  (root/'authoring/statistics-2026-10/patch.json').write_text(json.dumps(PATCH))
  for kind in ['topics','questions','dependencies']:
   data=json.loads((ROOT/'data'/f'{kind}.json').read_text())
   if baseline:
    for c in PATCH[kind]:
     field='topicId' if kind=='dependencies' else 'id'
     data=[x for x in data if x[field]!=c['id']]
     if kind=='dependencies':data+=copy.deepcopy(c['before'])
     elif c['before'] is not None:data.append(copy.deepcopy(c['before']))
   (root/'data'/f'{kind}.json').write_text(json.dumps(data,ensure_ascii=False))
 def test_baseline_apply_preserves_unrelated_records(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root,True)
   old=json.loads((root/'data/topics.json').read_text());out=build(root)
   ids={c['id'] for c in PATCH['topics']}
   self.assertEqual([x for x in old if x['id'] not in ids],[x for x in out['topics'] if x['id'] not in ids])
   self.assertEqual(len(out['topics']),1505);build(root,True)
 def test_idempotence(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);build(root)
   before={p.name:p.read_bytes() for p in (root/'data').glob('*.json')};build(root)
   self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'data').glob('*.json')})
 def test_drift_aborts_before_any_write(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root,True)
   p=root/'data/questions.json';qs=json.loads(p.read_text());next(x for x in qs if x['id']=='cnm_305_q4')['answer']='external edit';p.write_text(json.dumps(qs))
   before={p.name:p.read_bytes() for p in (root/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):build(root)
   self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'data').glob('*.json')})
 def test_release_and_review_scope(self):
  release=json.loads((ROOT/'data/statistics-release.json').read_text());self.assertFalse(release['expertReviewed'])
  rows=json.loads((ROOT/'reviews/math-junior/batch-b/node-review.json').read_text());self.assertEqual(len(rows),45)
  decisions=json.loads((ROOT/'reviews/math-junior/statistics/decisions.json').read_text());self.assertTrue(all(x['decision']=='accept' for x in decisions['cards']))
  current=ROOT/'data/current-release.json'
  lock=json.loads(current.read_text()) if current.exists() else release
  build(ROOT,True)  # Historical statistics objects must still match their canonical patch.
  for name,sha in lock['files'].items():self.assertEqual(hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest(),sha)
if __name__=='__main__':unittest.main()

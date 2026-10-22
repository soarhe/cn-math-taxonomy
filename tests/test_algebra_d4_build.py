import copy,json,sys,tempfile,unittest,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_algebra_d4 import build,digest

def load(p):return json.loads((ROOT/p).read_text())
class AlgebraD4BuildTests(unittest.TestCase):
 def fixture(self,r):
  patch=load('authoring/algebra-d4-2026-10/patch.json')
  (r/'data').mkdir();(r/'authoring/algebra-d4-2026-10').mkdir(parents=True)
  (r/'authoring/algebra-d4-2026-10/patch.json').write_text(json.dumps(patch))
  for k in ['topics','questions','dependencies']:
   rows=load('data/'+k+'.json')
   for c in patch[k]:
    field='topicId' if k=='dependencies' else 'id';rows=[x for x in rows if x[field]!=c['id']]
    if k=='dependencies':rows+=copy.deepcopy(c['before'])
    elif c['before'] is not None:rows.append(copy.deepcopy(c['before']))
   (r/'data'/f'{k}.json').write_text(json.dumps(rows))
 def test_rebuild_and_preservation(self):
  patch=load('authoring/algebra-d4-2026-10/patch.json')
  self.assertEqual(len(patch['topics']),7);self.assertEqual(len(patch['questions']),14)
  for k in ['topics','questions','dependencies']:
   for c in patch[k]:self.assertEqual(c['beforeHash'],digest(c['before']) if c['before'] is not None else None)
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r)
   before={k:json.loads((r/'data'/f'{k}.json').read_text()) for k in patch if k in ['topics','questions','dependencies']}
   out=build(r);build(r,True)
   for k in before:
    ids={c['id'] for c in patch[k]};field='topicId' if k=='dependencies' else 'id'
    self.assertEqual([x for x in before[k] if x[field] not in ids],[x for x in out[k] if x[field] not in ids])
   b={p.name:p.read_bytes() for p in (r/'data').glob('*.json')};build(r)
   self.assertEqual(b,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_edge_drift_blocks_all_writes(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);p=r/'data/dependencies.json';rows=json.loads(p.read_text())
   next(x for x in rows if x['topicId']=='cnm_091')['reason']='independent edit';p.write_text(json.dumps(rows))
   b={p.name:p.read_bytes() for p in (r/'data').glob('*.json')}
   with self.assertRaisesRegex(ValueError,'upstream drift'):build(r)
   self.assertEqual(b,{p.name:p.read_bytes() for p in (r/'data').glob('*.json')})
 def test_audit_and_release(self):
  self.assertEqual(sum(x['status']=='targeted-revision' for x in load('reviews/math-junior/batch-d4/topic-inventory.json')),38)
  req=load('reviews/math-junior/batch-d4/requirements.json');self.assertEqual(len(req),49)
  self.assertEqual(sum(x['coverage']=='partial' for x in req),30)
  qs={q['id']:q for q in load('data/questions.json')}
  for row in load('reviews/math-junior/batch-d4/question-review.json'):
   self.assertEqual(row['contentSha256'],digest(qs[row['questionId']]))
   self.assertEqual(qs[row['questionId']]['type'],'self');self.assertGreaterEqual(len(qs[row['questionId']]['rubric']),3)
  self.assertEqual(load('data/current-release.json')['counts']['questions'],6250)
  self.assertEqual(load('reviews/math-junior/batch-d3/release.json')['counts']['questions'],6236)
  app=(ROOT/'diagnose/app.js').read_text();self.assertIn('cnmDiagnose.session.algebra-2026-10.3.evidence-1.1',app)
  build(ROOT,True)
 def test_actual_graph_does_not_force_both_methods(self):
  js="""const assert=require('assert'),E=require('./diagnose/engine.js');
  const G=E.buildGraph(require('./data/topics.json'),require('./data/dependencies.json'),require('./data/questions.json'));
  const deps=require('./data/dependencies.json');
  for(const id of ['cnm_089','cnm_090']) assert.equal(deps.find(x=>x.topicId==='cnm_091'&&x.prerequisiteId===id).strength,'soft');
  let s=E.createSession(G,['cnm_091'],{seed:'d4',limit:100}),asked=[];
  for(let i=0;i<100;i++){const item=E.nextItem(G,s);if(!item)break;asked.push(item.topicId);s=E.applyAnswer(G,s,item.topicId,'wrong',{qid:item.question.id});}
  assert(asked.includes('cnm_091'));assert(!asked.includes('cnm_089'));assert(!asked.includes('cnm_090'));
  for(const id of ['cnm_089','cnm_090']) assert.equal(E.nextItem(G,E.createSession(G,[id])).topicId,id);
  """
  subprocess.run(['node','-e',js],cwd=ROOT,check=True)
 def test_reference_values_and_endpoint_semantics(self):
  from fractions import Fraction as F
  self.assertEqual(3*(-4)+2,(-4)-6)
  self.assertEqual(5*(9+2)-3*(2*9-1),4)
  self.assertEqual(F(3+1,2)-F(3,3),1)
  self.assertEqual(2*2+3*1,7);self.assertEqual(3*2-2*1,4)
  for x in [F(-4),F(-3),F(-5,2),F(0),F(4)]:self.assertEqual(2*(x-3)>=5*x+3,x<=-3)
  for x in [F(1),F(2),F(5,2),F(5),F(6)]:self.assertEqual(2*x-1>3 and x-5<=0,2<x<=5)
  self.assertEqual([x for x in range(-5,6) if x>=2 and x<=2],[2])
  self.assertFalse(any(x>2 and x<=2 for x in range(-5,6)))
if __name__=='__main__':unittest.main()

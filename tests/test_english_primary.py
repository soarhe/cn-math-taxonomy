import hashlib,json,unittest,wave,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class EnglishPrimaryTests(unittest.TestCase):
 def test_media_and_links(self):
  data=json.loads((R/'data/english-primary-activities.json').read_text());topics={t['id'] for t in json.loads((R/'data/topics.json').read_text())};standards={s['id'] for s in json.loads((R/'data/cn-curriculum-standards.json').read_text())['items']}
  self.assertEqual(len({t['id'] for t in data['tasks']}),38)
  for t in data['tasks']:
   self.assertTrue(set(t['topicIds'])<=topics);self.assertTrue(set(t['standardIds'])<=standards);self.assertFalse(t['autoMastery']);self.assertFalse(t['expertReviewed'])
   if t['audio']:
    p=R/'activities/english-primary'/t['audio']['path'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),t['audio']['sha256'])
    with wave.open(str(p)) as w:self.assertGreater(w.getnframes()/w.getframerate(),1)
    self.assertFalse(t['audio']['humanListeningReviewed'])
   if t['figure']:ET.parse(R/'activities/english-primary'/t['figure'])
 def test_coverage_not_overclaimed(self):
  rows=json.loads((R/'reviews/english-primary/coverage.json').read_text())['rows'];self.assertEqual(len(rows),35)
  for r in rows:self.assertEqual(bool(r['taskIds']),r['status']=='sample-authored');self.assertFalse(r['expertValidated'])
 def test_evidence_boundaries(self):
  js=(R/'activities/english-primary/app.js').read_text();self.assertIn('answerExposed=true',js);self.assertIn('autoMastery:false',js);self.assertIn('未观察',js);self.assertNotIn('cnmDiagnose.session',js);self.assertIn('historicalRecords',js);self.assertIn('score-without-evidence',js)
 def test_no_listening_claims_reading_and_level_correction(self):
  data=json.loads((R/'data/english-primary-activities.json').read_text())
  for t in data['tasks']:
   if t['skill']=='listening':self.assertFalse(t['standardIds'])
  task=next(t for t in data['tasks'] if t['id']=='ep-2-GR-02');self.assertEqual(task['gradeRange'],[3,4])
  reading=next(t for t in data['tasks'] if t['id']=='ep-1-RW-02');self.assertEqual(reading['skill'],'reading');self.assertIn('My name is Ben',reading['prompt'])
 def test_build_and_all_internal_records(self):
  import sys
  sys.path.insert(0,str(R/'scripts'))
  from build_english_primary import build
  build(check=True)
  report=json.loads((R/'reviews/english-primary/coverage.json').read_text());self.assertTrue(all(r['taskIds'] for r in report['rows']));self.assertEqual(len(report['observations']),114)
 def test_targeted_tasks_replace_weak_mappings(self):
  tasks={t['id']:t for t in json.loads((R/'data/english-primary-activities.json').read_text())['tasks']}
  self.assertFalse(tasks['ep-strategy-revise']['standardIds'])
  self.assertNotIn('ces-2022:1.FU.03',tasks['ep-speak-greeting']['standardIds'])
  self.assertNotIn('ces-2022:2.FU.02',tasks['ep-speak-weekend']['standardIds'])
  for tid in ['ep-2-VO-02','ep-1-FU-03','ep-2-FU-02']:
   self.assertEqual(len(tasks[tid]['observationItems']),3)
   self.assertEqual(len(tasks[tid]['scoringExamples']),3)
 def test_math_activity_requirements_are_visible_without_changing_edges(self):
  js=(R/'explore/app.js').read_text();self.assertIn('活动关联的课标要求',js);self.assertIn('activityStandards',js)
  records=json.loads((R/'reviews/primary-completion/observation-matrix.json').read_text());self.assertEqual(len(records['rows']),243)
if __name__=='__main__':unittest.main()

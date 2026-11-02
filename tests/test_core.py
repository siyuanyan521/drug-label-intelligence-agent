import sys,json,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from drug_label_agent.provenance import latest_record,sha256_file,verified_cache,save_checkpoint
from inspect_pdf import inspect
from pypdf import PdfWriter
class Tests(unittest.TestCase):
 def test_latest_ties(self):
  rows=[{'acceptance_date':'2020-01-01'},{'acceptance_date':'2024-01-01'},{'acceptance_date':'2024-01-01'}];self.assertEqual(len(latest_record(rows)),2)
 def test_invalid_date(self):
  with self.assertRaises(ValueError):latest_record([{'acceptance_date':'unknown'}])
 def test_empty(self):
  with self.assertRaises(ValueError):latest_record([])
 def test_atomic_replace(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'state.json';save_checkpoint(p,{'a':1});save_checkpoint(p,{'a':2});self.assertEqual(json.loads(p.read_text()),{'a':2});self.assertFalse(list(Path(d).glob('*.tmp')))
 def test_changed_cache(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'file';p.write_bytes(b'a');r={'file':'file','sha256':sha256_file(p),'verification':'VERIFIED'};self.assertTrue(verified_cache(r,d));p.write_bytes(b'b');self.assertFalse(verified_cache(r,d));r['sha256']=sha256_file(p);r['verification']='NOT_VERIFIED';self.assertFalse(verified_cache(r,d))
 def test_path_escape(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'file';p.write_bytes(b'a');inner=Path(d)/'inner';inner.mkdir();self.assertFalse(verified_cache({'file':'../file','sha256':sha256_file(p),'verification':'VERIFIED'},inner))
 def test_false_pdf(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.pdf';p.write_text('<html>error</html>')
   with self.assertRaises(ValueError):inspect(p)
 def test_blank_not_verified(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.pdf';w=PdfWriter();w.add_blank_page(width=100,height=100)
   with p.open('wb') as f:w.write(f)
   result=inspect(p);self.assertEqual(result['pages'],1);self.assertFalse(result['has_extractable_text']);self.assertEqual(result['identity_status'],'NEEDS_REVIEW')

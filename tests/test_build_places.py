import unittest
from ingestion.build_places import build
class PlaceIndexTests(unittest.TestCase):
 def test_no_duplicates_or_short_index(self):
  rows=[{"GEOID":str(i).zfill(7),"NAME":"City "+str(i),"ALAND":"4046856"} for i in range(15001)]
  out=build(rows)
  self.assertEqual(len(out),15001)
  self.assertEqual(len({x["geoid"] for x in out}),15001)
 def test_cdp_flag(self):
  rows=[{"GEOID":str(i).zfill(7),"NAME":("Sample CDP" if i==1 else "Town "+str(i)),"ALAND":"10000"} for i in range(15001)]
  self.assertEqual(next(x for x in build(rows) if x["geoid"]=="0000001")["type"],"CDP")

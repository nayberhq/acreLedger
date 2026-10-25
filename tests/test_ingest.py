import unittest
from ingestion.ingest import resolve, METERS2_PER_ACRE
class ResolverTests(unittest.TestCase):
    def test_city(self):
        rows=[{"GEOID":"1830000","NAME":"Rochester city","ALAND":str(int(2*METERS2_PER_ACRE))}]
        r=resolve(rows,"Rochester","IN")
        self.assertEqual(r["geoid"],"1830000")
        self.assertEqual(r["land_acres"],2.0)
    def test_missing(self):
        self.assertEqual(resolve([],"No Such Place","IN")["status"],"unresolved")
if __name__=="__main__":unittest.main()

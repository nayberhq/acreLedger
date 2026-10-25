import unittest
from ingestion.finance_raw import RawRecord
from ingestion.finance_parse import parse_finance,parse_government,match_government,Government
class FinanceTests(unittest.TestCase):
 def test_finance(self):
  r=parse_finance(RawRecord("source",1,"01000022608519U     87374322022R"))
  self.assertEqual((r.government_id,r.item_code,r.amount_thousands_usd,r.year,r.imputation_flag),("010000226085","19U",8737432,2022,"R"))
 def test_government(self):
  s="010000226085"+"ALABAMA".ljust(64)+"".ljust(35)+"".ljust(5)+"492153222"+"  "+"".ljust(7)+"  "+"".ljust(10)
  self.assertEqual(len(s),146)
  g=parse_government(RawRecord("directory",1,s))
  self.assertEqual(g.name,"ALABAMA")
 def test_ambiguous(self):
  g=Government("181234567890","Rochester","Fulton","12345",6000,"dir",1)
  self.assertEqual(match_government([g,g],"18","12345","Rochester")["status"],"ambiguous")
if __name__=="__main__":unittest.main()

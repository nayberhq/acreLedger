import unittest
from ingestion.fiscal_balance import calculate,InsufficientCoverage
class FiscalBalanceTests(unittest.TestCase):
 def test_contributor(self):
  r=calculate("Example",2024,100000,60000,10)
  self.assertEqual(r.net_balance_usd,40000)
  self.assertEqual(r.net_per_acre_usd,4000)
 def test_recipient(self):
  self.assertEqual(calculate("Example",2024,10000,25000,5).net_per_acre_usd,-3000)
 def test_missing_never_zero(self):
  with self.assertRaises(InsufficientCoverage):calculate("Example",2024,None,10000,5)
 def test_invalid_area(self):
  with self.assertRaises(ValueError):calculate("Example",2024,10000,10000,0)

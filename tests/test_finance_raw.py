import io, unittest, zipfile
from ingestion.finance_raw import inspect_records
class FinanceRawTests(unittest.TestCase):
    def archive(self, name, rows):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,"w") as z:z.writestr(name,"\n".join(rows)+"\n")
        return stream.getvalue()
    def test_finance_lossless(self):
        line="01000022608519U     87374322022R"
        out=list(inspect_records(self.archive("2022FinEstDAT.txt",[line]),"FinEstDAT.txt","finance"))
        self.assertEqual(out[0].raw,line)
        self.assertEqual(out[0].line_number,1)
    def test_reject_bad_width(self):
        with self.assertRaises(ValueError):
            list(inspect_records(self.archive("FinEstDAT.txt",["bad"]),"FinEstDAT.txt","finance"))
if __name__=="__main__":unittest.main()

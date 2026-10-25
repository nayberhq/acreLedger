"""Generate source-traceable pilot city finance extracts from raw Census ZIPs."""
import io,json,urllib.request,zipfile
from pathlib import Path
from ingestion.finance_raw import inspect_records
from ingestion.finance_parse import parse_finance,parse_government,match_government
from ingestion.ingest import load_gazetteer,resolve,PILOTS
URLS={"2022":"https://www2.census.gov/programs-surveys/gov-finances/tables/2022/2022_Individual_Unit_File.zip","2024":"https://www2.census.gov/programs-surveys/gov-finances/tables/2024/2024_Individual_Unit_Files.zip"}
def download(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"AcreLedger/0.1"}),timeout=120) as r:return r.read()
def extract(year,raw,identities):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist()
  directory=next(n for n in names if n.rsplit("/",1)[-1]==f"Fin_PID_{year}.txt")
  finance=next(n for n in names if "FinEstDAT" in n and n.endswith(".txt"))
 governments=[parse_government(r) for r in inspect_records(raw,directory,"government_directory")]
 results={}
 for name,state,identity in identities:
  if identity["status"]!="resolved":continue
  match=match_government(governments,identity["state_fips"],identity["place_fips"],name)
  results[f"{name}, {state}"]={"place_geoid":identity["geoid"],"match":match,"financial_items":[],"financial_status":"unavailable"}
 ids={c["government_id"] for x in results.values() if x["match"]["status"]=="matched" for c in x["match"]["candidates"]}
 byid={i:[] for i in ids}
 for rec in inspect_records(raw,finance,"finance"):
  if rec.raw[:12] in byid:
   item=parse_finance(rec)
   byid[item.government_id].append({"code":item.item_code,"amount_thousands_usd":item.amount_thousands_usd,"year":item.year,"imputation_flag":item.imputation_flag,"source_line":item.line_number})
 for x in results.values():
  if x["match"]["status"]=="matched":
   gid=x["match"]["candidates"][0]["government_id"]
   x["financial_items"]=byid[gid]
   x["financial_status"]="raw_items_found" if byid[gid] else "no_finance_records"
  x["source_url"]=URLS[year]
  x["source_member"]=finance
 return results
if __name__=="__main__":
 out=Path("data/finance-pilots");out.mkdir(parents=True,exist_ok=True)
 rows=load_gazetteer(".cache/acreledger")
 identities=[(name,state,resolve(rows,name,state)) for name,state in PILOTS]
 for year,url in URLS.items():
  results=extract(year,download(url),identities)
  (out/f"{year}.json").write_text(json.dumps(results,indent=2))
  print(json.dumps({year:{k:{"match":v["match"]["status"],"items":len(v["financial_items"]),"status":v["financial_status"]} for k,v in results.items()}},indent=2))

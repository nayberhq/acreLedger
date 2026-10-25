"""AcreLedger public-source ingestion. Python standard library only."""
import argparse, csv, io, json, os, re, sys, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

GAZETTEER = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gazetteer_files.zip"
GAZETTEER_PLACES = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gazetteer_places_national.zip"
ACS = "https://api.census.gov/data/2024/acs/acs5"
FINANCE = "https://www2.census.gov/programs-surveys/gov-finances/tables/2022/2022_Individual_Unit_File.zip"
PILOTS = [("Rochester", "IN"), ("Steubenville", "OH"), ("Hillsboro", "OR")]
STATES = {"IN": "18", "OH": "39", "OR": "41"}
METERS2_PER_ACRE = 4046.8564224

def fetch(url, cache, timeout=90):
    cache = Path(cache)
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "AcreLedger/0.1 public research (https://github.com/nayberhq/acreLedger)"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
        cache.write_bytes(data)
    return cache.read_bytes()

def load_gazetteer(cache_dir):
    raw = fetch(GAZETTEER_PLACES, Path(cache_dir)/"2024_places_national.zip")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files = [n for n in z.namelist() if n.lower().endswith(".txt")]
        if len(files) != 1:
            raise ValueError("Expected one gazetteer text file; found: " + str(files))
        txt = z.read(files[0]).decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(txt), delimiter="\t"))
    required = {"GEOID", "NAME", "ALAND"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Unexpected Gazetteer columns: " + str(list(rows[0]) if rows else []))
    return rows

def resolve(rows, name, state):
    fips = STATES.get(state.upper())
    if not fips:
        raise ValueError("Unsupported state abbreviation in this pilot: " + state)
    matches = [r for r in rows if r["GEOID"].startswith(fips) and re.sub(r" (city|town|village|borough|CDP)$","",r["NAME"],flags=re.I).casefold()==name.casefold()]
    if len(matches)!=1:
        return {"status":"unresolved","candidates":[{"name":r["NAME"],"geoid":r["GEOID"]} for r in matches]}
    r=matches[0]
    return {"status":"resolved","name":r["NAME"],"geoid":r["GEOID"],"state_fips":fips,
            "place_fips":r["GEOID"][2:],"land_acres":round(int(r["ALAND"])/METERS2_PER_ACRE,2),
            "land_area_source":GAZETTEER_PLACES,"land_area_year":2024}

def acs_population(identity,cache_dir,api_key=None):
    from urllib.parse import urlencode
    params={"get":"NAME,B01003_001E","for":"place:"+identity["place_fips"],"in":"state:"+identity["state_fips"]}
    if api_key: params["key"]=api_key
    url=ACS+"?"+urlencode(params)
    try:
        raw=fetch(url,Path(cache_dir)/("acs_"+identity["geoid"]+".json"))
        data=json.loads(raw)
        if len(data)!=2 or data[0][:2]!=["NAME","B01003_001E"]:
            raise ValueError("Unexpected ACS response")
        value=int(data[1][1])
        if value<0: raise ValueError("Suppressed ACS population")
        return {"status":"observed","population_estimate":value,"source":url,"period":"2020–2024 ACS 5-year"}
    except Exception as exc:
        return {"status":"unavailable","reason":str(exc)[:300],"source":url}

def source_manifest():
    return [
      {"id":"census_gazetteer","url":GAZETTEER_PLACES,"year":2024,"coverage":"national places","adapter":"implemented"},
      {"id":"census_acs5","url":ACS,"year":2024,"coverage":"all Census places","adapter":"implemented; key may be required"},
      {"id":"census_finance_individual","url":FINANCE,"year":2022,"coverage":"government units; requires identity crosswalk","adapter":"discovery only; not attributed"},
      {"id":"irs_zip_soi","url":"https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-zip-code-data-soi","coverage":"ZIP; not city","adapter":"discovery only; not attributed"},
      {"id":"usaspending","url":"https://www.usaspending.gov/","coverage":"federal awards; not beneficiary spending","adapter":"discovery only; not attributed"}
    ]

def run(city,state,cache_dir,api_key=None):
    report={"query":{"city":city,"state":state},"retrieved_at":datetime.now(timezone.utc).isoformat(),
            "sources":source_manifest(),"financial_status":"unavailable",
            "taxes_paid_usd":None,"spending_received_usd":None,"net_balance_usd":None,"net_per_acre_usd":None,
            "notes":["No government-finance-to-place crosswalk established.","Do not infer spending beneficiaries from award recipients.","No synthetic financial values permitted."]}
    try:
        identity=resolve(load_gazetteer(cache_dir),city,state)
        report["municipality"]=identity
        if identity["status"]=="resolved":
            report["population"]=acs_population(identity,cache_dir,api_key)
    except Exception as exc:
        report["municipality"]={"status":"error","reason":str(exc)[:500]}
    return report

def main():
    parser=argparse.ArgumentParser(description="Ingest source-backed municipal geography and coverage")
    parser.add_argument("--city")
    parser.add_argument("--state")
    parser.add_argument("--all-pilots",action="store_true")
    parser.add_argument("--cache",default=".cache/acreledger")
    parser.add_argument("--output",default="data/coverage")
    args=parser.parse_args()
    if not args.all_pilots and not(args.city and args.state):
        parser.error("Supply --all-pilots or both --city and --state")
    targets=PILOTS if args.all_pilots else [(args.city,args.state)]
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for city,state in targets:
        report=run(city,state,args.cache,os.environ.get("CENSUS_API_KEY"))
        path=out/(re.sub(r"[^a-z0-9]+","-",city.lower()).strip("-")+"-"+state.lower()+".json")
        path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        results.append({"file":str(path),"municipality":report["municipality"].get("status"),"financial":report["financial_status"]})
    print(json.dumps(results,indent=2))
    if any(x["municipality"]=="error" for x in results):sys.exit(1)

if __name__=="__main__":main()

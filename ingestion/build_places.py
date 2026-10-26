"""Build a national searchable municipality index from official Census Gazetteer."""
import json,re
from pathlib import Path
from ingestion.ingest import load_gazetteer, GAZETTEER_PLACES, METERS2_PER_ACRE

def build(rows):
    result=[]
    for r in rows:
        geoid=r["GEOID"]
        name=r["NAME"].strip()
        if len(geoid)!=7 or not geoid.isdigit(): continue
        # Gazetteer also contains CDPs; explicitly retain place type.
        kind="CDP" if re.search(r"\bCDP$",name,re.I) else "incorporation_candidate"
        result.append({"geoid":geoid,"name":name,"state_fips":geoid[:2],
                       "place_fips":geoid[2:],"type":kind,
                       "land_acres":round(int(r["ALAND"])/METERS2_PER_ACRE,2)})
    result.sort(key=lambda r:(r["name"].casefold(),r["state_fips"]))
    if len(result)<15000:raise ValueError(f"Suspiciously small national place index: {len(result)}")
    if len({r["geoid"] for r in result})!=len(result):raise ValueError("Duplicate place GEOID")
    return result

if __name__=="__main__":
    rows=build(load_gazetteer(".cache/acreledger"))
    out=Path("public/data/places.json");out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"source":GAZETTEER_PLACES,"year":2024,"places":rows},separators=(",",":")))
    print(f"Validated {len(rows)} Census places; saved {out}")

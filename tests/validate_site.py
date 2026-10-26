"""Fail closed if published financial records or the frontend are invalid."""
import json,re,subprocess
from pathlib import Path

def validate_page(path):
    html=Path(path).read_text(encoding="utf-8")
    scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script\s*>",html,re.S|re.I)
    assert len(scripts)==1, f"Expected one application script; got {len(scripts)}"
    assert html.lower().count("</html>")==1, "Duplicate HTML closing tag"
    assert html.rstrip().lower().endswith("</html>"), "Text leaked after closing HTML"
    assert "financial_items" in scripts[0], "Financial report renderer missing"
    assert "loadIndex()" in scripts[0], "Municipality index load not invoked"\n    assert "loadFinance()" in scripts[0], "Financial record loader missing"
    check=subprocess.run(["node","--check","-"],input=scripts[0],text=True,capture_output=True)
    assert check.returncode==0, "Invalid JavaScript: "+check.stderr

def validate_data(path,year):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    required={"Rochester, IN","Steubenville, OH","Hillsboro, OR"}
    assert required.issubset(data), "Missing pilot cities: "+str(required-set(data))
    count=0
    for city,entry in data.items():
        match=entry["match"]["status"]
        assert match in ("matched","unmatched","ambiguous"), (city,match)
        items=entry["financial_items"]
        if match!="matched":assert not items, "Unmatched city has records: "+city
        for item in items:
            assert re.fullmatch(r"[A-Z0-9]{3}",item["code"]), item
            assert type(item["amount_thousands_usd"]) is int, item
            assert item["year"]==year, item
            assert type(item["source_line"]) is int and item["source_line"]>0, item
            count+=1
    assert count>0, "No financial items in "+str(year)
    return count

if __name__=="__main__":
    validate_page("index.html")
    totals={year:validate_data(f"public/data/{year}.json",year) for year in (2022,2024)}
    print("PASS: HTML, JavaScript, ingestion records, and report prerequisites",totals)

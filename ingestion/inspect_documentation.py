"""Read the technical documentation embedded in official Census financial archives.

This tool only extracts field-layout evidence; it never guesses semantics.
"""
import io, json, re, subprocess, tempfile, urllib.request, zipfile
from pathlib import Path
URLS={
 "2022":"https://www2.census.gov/programs-surveys/gov-finances/tables/2022/2022_Individual_Unit_File.zip",
 "2024":"https://www2.census.gov/programs-surveys/gov-finances/tables/2024/2024_Individual_Unit_Files.zip"
}
TERMS=re.compile(r"record layout|record format|position|character|identification|item code|finance file|public use file|data file|dollar|thousand|government id|unit code",re.I)
def extract(year,url):
    request=urllib.request.Request(url,headers={"User-Agent":"AcreLedger/0.1"})
    with urllib.request.urlopen(request,timeout=120) as r: archive=r.read()
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        docs=[n for n in z.namelist() if "technical documentation" in n.lower() and n.lower().endswith(".pdf")]
        if len(docs)!=1:raise ValueError(f"Expected one technical PDF, found {docs}")
        with tempfile.TemporaryDirectory() as td:
            pdf=Path(td)/"documentation.pdf";pdf.write_bytes(z.read(docs[0]))
            proc=subprocess.run(["pdftotext","-layout",str(pdf),"-"],capture_output=True,text=True,check=True)
            lines=proc.stdout.splitlines()
    matches=[i for i,line in enumerate(lines) if TERMS.search(line)]
    selected=set()
    for i in matches:
        selected.update(range(max(0,i-3),min(len(lines),i+8)))
    evidence="\n".join(f"{i+1:05d} {lines[i]}" for i in sorted(selected))
    return {"year":year,"url":url,"documentation":docs[0],"total_lines":len(lines),"matched_lines":len(matches),"evidence":evidence}
if __name__=="__main__":
    out=Path("data/source-inspection");out.mkdir(parents=True,exist_ok=True)
    for year,url in URLS.items():
        try:
            r=extract(year,url)
            (out/f"{year}-technical-evidence.txt").write_text(r["evidence"])
            print(f"=== {year} technical documentation: {r['total_lines']} lines; {r['matched_lines']} matches ===")
            print(r["evidence"][:25000])
        except Exception as e:
            print(f"FAILED {year}: {e}")
            raise

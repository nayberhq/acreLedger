"""Inspect the actual Census government-finance ZIP before writing a parser."""
import io, json, urllib.request, zipfile
from pathlib import Path

URLS = {
 "2022":"https://www2.census.gov/programs-surveys/gov-finances/tables/2022/2022_Individual_Unit_File.zip",
 "2024":"https://www2.census.gov/programs-surveys/gov-finances/tables/2024/2024_Individual_Unit_Files.zip"
}
def inspect(year,url):
    req=urllib.request.Request(url,headers={"User-Agent":"AcreLedger source-format research"})
    with urllib.request.urlopen(req,timeout=90) as response: data=response.read()
    result={"year":year,"source":url,"archive_bytes":len(data),"members":[]}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for f in z.infolist():
            item={"name":f.filename,"bytes":f.file_size}
            if not f.is_dir() and f.file_size < 50_000_000 and f.filename.lower().endswith((".txt",".csv",".dat")):
                with z.open(f) as stream:
                    sample=[stream.readline().decode("latin-1").rstrip("\r\n") for _ in range(5)]
                item["sample_lines"]=sample
                item["sample_lengths"]=[len(s) for s in sample]
            result["members"].append(item)
    return result
if __name__=="__main__":
    out=Path("data/source-inspection");out.mkdir(parents=True,exist_ok=True)
    for year,url in URLS.items():
        try: result=inspect(year,url)
        except Exception as e: result={"year":year,"source":url,"error":str(e)}
        (out/(year+".json")).write_text(json.dumps(result,indent=2))
        print(json.dumps(result,indent=2))

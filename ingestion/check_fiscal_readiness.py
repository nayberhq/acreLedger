"""Strict pilot readiness test for actual net external fiscal balance.

This intentionally fails until observed/defensibly allocated tax and spending inputs exist.
"""
import json
from pathlib import Path
from ingestion.fiscal_balance import calculate,InsufficientCoverage

PILOTS=("Rochester, IN","Steubenville, OH","Hillsboro, OR")
def main():
    results={}
    for city in PILOTS:
        # No direct federal/state tax-incidence or beneficiary-spending dataset
        # has yet been ingested. Do not equate municipal receipts with those flows.
        try:
            calculate(city,2022,None,None,None)
        except InsufficientCoverage as exc:
            results[city]={"status":"blocked","reason":str(exc)}
    Path("data").mkdir(exist_ok=True)
    Path("data/fiscal-readiness.json").write_text(json.dumps(results,indent=2))
    raise SystemExit("Fiscal-readiness gate failed: no pilot city has a defensible net external fiscal balance yet.")
if __name__=="__main__":main()

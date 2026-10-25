"""Official Census finance public-use parser (documented 2022 and 2024 layouts)."""
from dataclasses import dataclass
from ingestion.finance_raw import RawRecord

@dataclass(frozen=True)
class FinanceItem:
    government_id: str
    item_code: str
    amount_thousands_usd: int
    year: int
    imputation_flag: str
    source_member: str
    line_number: int

@dataclass(frozen=True)
class Government:
    government_id: str
    name: str
    county_name: str
    place_fips: str
    population: int | None
    source_member: str
    line_number: int

def parse_finance(record: RawRecord) -> FinanceItem:
    s=record.raw
    if len(s)!=32: raise ValueError(f"Invalid finance width: {len(s)}")
    amount=s[15:27].strip()
    if not amount or not amount.lstrip("-").isdigit(): raise ValueError("Invalid finance amount")
    return FinanceItem(s[:12],s[12:15],int(amount),int(s[27:31]),s[31],record.source_member,record.line_number)

def parse_government(record: RawRecord) -> Government:
    s=record.raw
    if len(s)!=146:raise ValueError(f"Invalid government directory width: {len(s)}")
    pop=s[116:125].strip()
    return Government(s[:12],s[12:76].strip(),s[76:111].strip(),s[111:116],int(pop) if pop.isdigit() else None,record.source_member,record.line_number)

def match_government(governments, state_fips, place_fips, name):
    """Match official place FIPS; flag multiple candidate units rather than silently choosing."""
    candidates=[g for g in governments if g.government_id[:2]==state_fips and g.place_fips==place_fips]
    return {"status":"matched" if len(candidates)==1 else "ambiguous" if candidates else "unmatched",
            "candidates":[{"government_id":g.government_id,"name":g.name,"county":g.county_name} for g in candidates]}

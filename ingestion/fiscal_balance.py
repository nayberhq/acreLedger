"""Fiscal balance calculations. Missing inputs fail closed, never become zero."""
from dataclasses import dataclass

class InsufficientCoverage(ValueError): pass

@dataclass(frozen=True)
class FiscalBalance:
    municipality: str
    year: int
    eligible_taxes_usd: int
    eligible_spending_usd: int
    land_acres: float
    net_balance_usd: int
    net_per_acre_usd: float

def calculate(municipality,year,eligible_taxes_usd,eligible_spending_usd,land_acres):
    required={"eligible_taxes_usd":eligible_taxes_usd,"eligible_spending_usd":eligible_spending_usd,"land_acres":land_acres}
    missing=[k for k,v in required.items() if v is None]
    if missing:raise InsufficientCoverage("Missing required fiscal inputs: "+", ".join(missing))
    if not isinstance(eligible_taxes_usd,int) or not isinstance(eligible_spending_usd,int):
        raise ValueError("Taxes and spending must be integer USD amounts")
    if eligible_taxes_usd<0 or eligible_spending_usd<0 or land_acres<=0:
        raise ValueError("Invalid fiscal inputs")
    net=eligible_taxes_usd-eligible_spending_usd
    return FiscalBalance(municipality,year,eligible_taxes_usd,eligible_spending_usd,land_acres,net,net/land_acres)

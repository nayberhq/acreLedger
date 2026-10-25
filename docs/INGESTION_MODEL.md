# AcreLedger: generic municipal ingestion model

## Objective
Discover and normalize public fiscal data for any incorporated US municipality before deciding presentation. Never synthesize financial records to fill missing coverage.

## Canonical identity
- Resolve user input to Census place GEOID (state FIPS + place FIPS).
- Store legal name, state, vintage, land area, population, geometry and incorporated/Census-designated status.
- Maintain a separate crosswalk for Census government unit IDs, which do not necessarily correspond one-to-one with Census places.
- Do not conflate municipality, county, school district, and special district.

## Adapters
1. Census geography: place boundaries, area, population; national coverage.
2. Census government finances: individual unit records; annual sample gaps are missing, not zero. Preserve government ID, item code, fiscal year and units.
3. IRS SOI ZIP: income-tax measures; ZIP-to-place allocation requires residential crosswalk and must preserve source tax year.
4. USAspending: federal awards; retain recipient and place-of-performance geography separately. Do not assume either equals final beneficiary.
5. State-specific adapters: only after generic source coverage is measured; each must declare jurisdiction, categories, period, provenance and quality.

## Normalized observation
```json
{
  "municipality_geoid": "string",
  "source_id": "string",
  "source_url": "string",
  "retrieved_at": "ISO8601",
  "source_period": "YYYY or FY-YYYY",
  "government_level": "federal|state|county|municipal|district",
  "government_unit_id": "string|null",
  "category": "controlled-vocabulary-code",
  "amount_usd": null,
  "unit": "USD|USD_thousands|persons|acres",
  "geographic_basis": "place|zip|county|state|award_recipient|place_of_performance",
  "attribution": "direct|allocated|unallocated",
  "allocation_method": null,
  "quality": "observed|estimated|unavailable",
  "exclusion_flags": ["social_security", "medicare"],
  "notes": "string"
}
```

## Reconciliation rules
- Never sum federal/state transfers to local governments with the same downstream spending when calculating aggregate spending.
- Keep city own-source tax receipts separate from taxes paid to federal and state governments.
- Exclude Social Security and Medicare payroll taxes and corresponding benefits from headline measure.
- Track government-wide expenditure categories separately from resident-benefit attribution.
- Do not combine different fiscal years without explicit labeling or an adjustment model.
- Never substitute zero for unavailable records.
- Preserve corporate tax-incidence uncertainty; statutory payment location is not economic incidence.
- National shared public goods and unallocatable spending must remain unallocated unless a documented allocation scenario is selected.

## Pipeline
resolve_city -> discover_sources -> download/cache_raw -> parse -> normalize -> geographic_crosswalk -> reconcile -> calculate_supported_metrics -> coverage_report

Each adapter returns: status, records, source vintage, provenance, and error diagnostics.
Store raw source files with checksums; normalized records are reproducible.

## Initial pilot
Rochester IN, Steubenville OH, Hillsboro OR.
For each: report resolved GEOID, matched finance government unit, years covered, tax ZIP overlap, award geographic coverage, known gaps, and calculations possible. No synthetic numbers.

## Success criteria
- Any valid incorporated municipality resolves deterministically.
- Every returned figure links to original public source and transformation.
- Missing coverage is explicit.
- The same ingestion code supports all three pilot cities without city-specific financial logic.
- Presentation design begins only after measured pilot coverage.

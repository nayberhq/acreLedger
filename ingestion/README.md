# AcreLedger ingestion

This is a **source-first ingestion prototype**. No financial numbers are fabricated. The first adapter resolves Census places using the official 2024 Gazetteer and requests population estimates from the 2024 ACS five-year API. The financial sources are listed for discovery only; **no city net fiscal balance is currently computable**.

## Run

Python 3.10+ (standard library only):

```bash
python -m ingestion.ingest --all-pilots
python -m ingestion.ingest --city Rochester --state IN
python -m unittest discover -s tests
```

Outputs are written to `data/coverage/*.json`. Raw downloaded files are cached in `.cache/acreledger`. To use an ACS key, set `CENSUS_API_KEY` in the environment. The Census API may require a key.

### Important boundaries

- Census places can include CDPs, so future production code must distinguish incorporated places.
- A Census place GEOID is **not** a Census government-unit ID.
- The government finance individual-unit archive cannot be attributed to a place until an audited government-unit crosswalk is implemented.
- IRS ZIP and federal awards do not automatically map to city taxpayers or spending beneficiaries.
- Missing values are `null`, never zero.
- The 2024 geography and ACS vintage is distinct from the 2022 finance source year.
- Pilot state codes IN/OH/OR are implemented; extend state mapping before claiming nationwide city resolution.

Source links and details: [Ingestion model](../docs/INGESTION_MODEL.md).

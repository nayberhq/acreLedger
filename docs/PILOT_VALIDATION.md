# Pilot validation — 2022 and 2024 Census finance

Source: official Census individual-government finance archives, extracted by GitHub Actions run 40243070707.

| City | 2022 match | 2022 raw financial items | 2024 match | 2024 raw financial items |
|---|---|---:|---|---:|
| Rochester, IN | Unique | 34 | Unique | 28 |
| Steubenville, OH | Unique | 47 | Unmatched | 0 |
| Hillsboro, OR | Unique | 50 | Unique | 50 |

- Workflow: https://github.com/nayberhq/acreLedger/actions/runs/40243070707
- Artifact: https://github.com/nayberhq/acreLedger/actions/runs/40243070707/artifacts/12617317561
- All values are original source item codes and amounts in thousands of dollars.
- Matching currently uses Census government-directory place FIPS and state FIPS. A uniqueness result is not yet an independently audited jurisdiction crosswalk.
- No category totals or net fiscal balance are asserted until the item code dictionary and aggregate/component overlap are verified.
- Missing 2024 Steubenville coverage is unknown, not zero.

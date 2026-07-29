# Task Tests — Fixtures

This directory documents the **NOP baseline** — the state of output files
when an agent does nothing (produces no outputs). All 12 verifier tests
must FAIL against this baseline for the task to be valid.

## NOP baseline

A NOP agent produces **no files**. The verifier tests against:
- `/app/rdf.csv` — does not exist → `test_rdf_csv_exists` FAILS
- `/app/results.json` — does not exist → `test_results_json_exists` FAILS
- All downstream tests that open these files also FAIL (FileNotFoundError)

## Anti-cheat guarantee

The reference values (`REF_PEAK_R`, `REF_PEAK_GR`, `REF_MIN_R`, `REF_CN`)
are defined only inside `test_outputs.py` — which lives in `tests/` and is
overlaid by Harbor at **verify time only**. The agent has no access to this
file during its run, so it cannot read the expected values and hardcode them.

## Fixture files (not used by pytest — documentation only)

`nop_rdf.csv` and `nop_results.json` below show the minimum malformed inputs
that would still fail every test, for documentation purposes. They are not
loaded by any test.

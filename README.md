# argon-rdf-coordination

Compute the **radial distribution function g(r)** and **first coordination number** for a liquid argon system from a 100-frame molecular dynamics trajectory.

## Task overview

The agent is given a custom 100-frame, 108-atom Lennard-Jones liquid-argon Monte Carlo trajectory (`/app/data/traj.xyz`) at the liquid state point ρ\* = 0.844, T\* = 0.85 (≈ 102 K). It must:

1. Parse the multi-frame XYZ file and extract per-frame cubic box lengths.
2. Compute all Ar–Ar pair distances using **minimum-image periodic boundary conditions**.
3. Histogram distances into 160 bins (0.05 Å width, 0 – 8.0 Å) and normalise to get g(r).
4. Identify the first peak and first post-peak minimum of g(r).
5. Integrate 4πρ g(r) r² dr up to the first minimum to obtain the coordination number.
6. Write `/app/rdf.csv` (160-row g(r) curve) and `/app/results.json` (peak position, peak height, first minimum, coordination number).

## Why it's hard

The task requires correct implementation of several non-trivial concepts from liquid-state statistical mechanics: minimum-image PBC (a common source of errors), the exact normalisation of the pair histogram by the ideal-gas shell density, robust detection of the shallow first minimum of g(r) from noisy data, and correct trapezoidal integration of 4πρ g(r) r² dr. The trajectory is custom-generated and cannot be looked up online.

## Environment

- Base image: `python:3.13-slim-bookworm` (pinned digest)
- Runtime deps: `numpy==2.2.6`
- Test deps baked in: `pytest==8.4.1`, `pytest-json-ctrf==0.3.5`
- Input data: `task/environment/data/traj.xyz` (100 frames, 108 Ar atoms, box L ≈ 17.16 Å)

## Verification

Ten pytest tests in `task/tests/test_outputs.py` verify:

| Test | Criterion |
|------|-----------|
| `test_rdf_csv_exists` | `/app/rdf.csv` present |
| `test_rdf_csv_format` | Header `r,gr`, 160 rows, bin centres 0.025–7.975 Å |
| `test_rdf_physical_properties` | Hard-core zero at r < 2 Å; asymptote to 1 at r > 7 Å; peak > 1.5 |
| `test_results_json_exists` | `/app/results.json` present |
| `test_results_json_keys` | All four required keys present |
| `test_first_peak_position` | `first_peak_r` = 3.675 ± 0.10 Å |
| `test_first_peak_height` | `first_peak_gr` = 2.88 ± 0.40 |
| `test_first_minimum_position` | `first_min_r` = 4.675 ± 0.15 Å |
| `test_coordination_number` | `coordination_number` = 10.21 ± 1.5 |
| `test_coordination_number_rounded` | Value rounded to 2 decimal places |

The oracle solution scores reward **1.0**; the nop agent scores **0**.

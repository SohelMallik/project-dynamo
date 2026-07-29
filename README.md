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

- Base image: `python:3.13-slim-bookworm` (pinned digest `sha256:01f423…`)
- Runtime deps: `numpy==2.2.6`
- Verifier deps baked in: `pytest==8.4.1`, `pytest-json-ctrf==0.3.5`
- Input data: `task/environment/data/traj.xyz` (100 frames, 108 Ar atoms, box L ≈ 17.16 Å)

## Verification

Twelve pytest tests in `task/tests/test_outputs.py` verify:

| Test | Criterion |
|------|-----------|
| `test_rdf_csv_exists` | `/app/rdf.csv` present |
| `test_rdf_csv_format` | Header `r,gr`; 160 rows; bin centres 0.025–7.975 Å |
| `test_rdf_hard_core_exclusion` | g(r) < 0.05 for r < 2.0 Å (LJ hard core) |
| `test_rdf_asymptotic_limit` | mean g(r) ∈ (0.6, 1.4) for r > 7 Å (g(r) → 1) |
| `test_rdf_liquid_structure_peak` | peak g(r) > 1.5 (liquid shell structure) |
| `test_results_json_exists` | `/app/results.json` present |
| `test_results_json_keys` | All four required keys present |
| `test_first_peak_position` | `first_peak_r` = 3.675 ± 0.10 Å |
| `test_first_peak_height` | `first_peak_gr` = 2.884 ± 0.40 |
| `test_first_minimum_position` | `first_min_r` = 4.675 ± 0.15 Å |
| `test_coordination_number` | `coordination_number` = 10.21 ± 1.5 |
| `test_coordination_number_rounded` | Value rounded to 2 decimal places |

The oracle solution scores reward **1.0**; the nop agent scores **0**.

## Oracle reference values

| Key | Value |
|-----|-------|
| `first_peak_r` | 3.6750 Å |
| `first_peak_gr` | 2.8838 |
| `first_min_r` | 4.6750 Å |
| `coordination_number` | 10.21 |

## Project structure

```
task/
├── task.toml                  # Harbor task config, metadata, timeouts
├── instruction.md             # Agent instruction (output contract, formulas)
├── environment/
│   ├── Dockerfile             # Pinned base image; numpy + pytest baked in
│   └── data/
│       ├── traj.xyz           # 100-frame liquid-Ar trajectory (input)
│       └── README.md          # Data format description
├── solution/
│   ├── solve.sh               # Entry point: python3 /solution/solve.py
│   ├── solve.py               # Oracle: parse → PBC distances → RDF → coord. number
│   └── README.md              # Algorithm walkthrough
└── tests/
    ├── test.sh                # Verifier entry point (runs pytest, writes reward.txt)
    ├── test_outputs.py        # 12 pytest tests on /app/rdf.csv and /app/results.json
    └── conftest.py            # Ensures /app exists before tests run

.github/workflows/
├── dynamo-review.yml          # Auto-runs on every PR (static checks + rubric review)
├── dynamo-validate.yml        # /validate comment → Docker build + oracle + nop check
├── dynamo-run-trials.yml      # /run comment → live agent trials (pass@k)
└── dynamo-rerun.yml           # /rerun comment → force-refresh full review pipeline

references/
├── dynamo-rubric.toml         # Rubric criteria used by the review pipeline
├── diversity-taxonomy.toml    # Closed-set vocabulary for task metadata labels
└── check-base-image.sh        # Static check: validates Dockerfile base image policy

_v.py                          # Local oracle runner: patches paths, runs solution + verifier
```

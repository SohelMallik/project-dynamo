# Harbor Task Specification — argon-rdf-coordination

This document is a complete reference card for how this task is packaged
for the **Harbor** benchmark execution platform (Dynamo TB2 format).

---

## 1. What Harbor does

Harbor is the execution platform that:

1. **Builds** the Docker environment image from `task/environment/Dockerfile`
2. **Runs the agent** inside the container — the agent sees `instruction.md`
   and the pre-baked input data at `/app/data/`; it writes outputs to `/app/`
3. **Runs the verifier** — Harbor overlays `task/tests/` at `/tests/` and
   executes `test.sh`, which runs pytest and writes a reward score (0 or 1)
   to `/logs/verifier/reward.txt`

---

## 2. Input files (what the agent sees)

| Path inside container | Source | Description |
|---|---|---|
| `/app/data/traj.xyz` | `task/environment/data/traj.xyz` | 100-frame liquid-Ar MD trajectory — the agent's only input |

The agent discovers these by reading the instruction. No other files are
visible to the agent.

---

## 3. Output files (what the agent must produce)

| Path inside container | Declared in `artifacts` | Description |
|---|---|---|
| `/app/rdf.csv` | ✅ `task/task.toml` line 1 | Radial distribution function — 160 rows, header `r,gr` |
| `/app/results.json` | ✅ `task/task.toml` line 1 | Scalar results — 4 keys |

### `/app/rdf.csv` schema

```
r,gr
0.025000,0.00000000
0.075000,0.00000000
...
7.975000,<float>
```

- Header: exactly `r,gr`
- Rows: exactly 160
- `r`: bin centre in Å, from 0.025 to 7.975 in steps of 0.05
- `gr`: g(r) value, floating-point

### `/app/results.json` schema

```json
{
  "first_peak_r":        <float>,   // Å, position of first g(r) peak
  "first_peak_gr":       <float>,   // dimensionless, height of first peak
  "first_min_r":         <float>,   // Å, position of first post-peak minimum
  "coordination_number": <float>    // rounded to 2 decimal places
}
```

---

## 4. Container layout at runtime

```
/
├── app/                          ← WORKDIR; agent writes outputs here
│   ├── data/
│   │   └── traj.xyz              ← input trajectory (COPYed in Dockerfile)
│   ├── rdf.csv                   ← OUTPUT: agent must create this
│   └── results.json              ← OUTPUT: agent must create this
│
├── solution/                     ← Oracle (mounted at verify/oracle time only)
│   ├── solve.sh
│   └── solve.py
│
├── tests/                        ← Verifier (overlaid by Harbor at verify time)
│   ├── test.sh
│   ├── test_outputs.py
│   └── conftest.py
│
└── logs/verifier/
    ├── ctrf.json                 ← pytest JSON report
    └── reward.txt                ← "1" (pass) or "0" (fail)
```

---

## 5. task.toml structure

```toml
artifacts = ["/app/rdf.csv", "/app/results.json"]   # ← ROOT LEVEL (required)

[task]
name = "dynamo/argon-rdf-coordination"

[metadata]
category    = "scientific_computing_and_domain_science"
subcategory = "chemistry_and_materials_workflows"
task_objective = ["analyze", "implement"]
artifact_type  = ["dataset_or_tabular_file", "generated_output_artifact"]
expert_time_estimate_hours = 1.5

[verifier]
timeout_sec = 60.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 600.0
cpus       = 2
memory_mb  = 2048
storage_mb = 10240
gpus       = 0
allow_internet = true
mcp_servers    = []
```

---

## 6. Verifier flow

```
Harbor calls:  bash /tests/test.sh
                 └─ pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py
                      ├─ 12 test functions execute
                      └─ reward.txt = "1" if all pass, "0" otherwise
```

**12 verifier tests:**

| # | Test | Checks |
|---|------|--------|
| 1 | `test_rdf_csv_exists` | `/app/rdf.csv` present |
| 2 | `test_rdf_csv_format` | Header `r,gr`; 160 rows; first=0.025; last=7.975 |
| 3 | `test_rdf_hard_core_exclusion` | g(r) < 0.05 for r < 2.0 Å |
| 4 | `test_rdf_asymptotic_limit` | mean g(r) ∈ (0.6, 1.4) for r > 7 Å |
| 5 | `test_rdf_liquid_structure_peak` | peak g(r) > 1.5 |
| 6 | `test_results_json_exists` | `/app/results.json` present |
| 7 | `test_results_json_keys` | All 4 keys present |
| 8 | `test_first_peak_position` | `first_peak_r` = 3.675 ± 0.10 Å |
| 9 | `test_first_peak_height` | `first_peak_gr` = 2.884 ± 0.40 |
| 10 | `test_first_minimum_position` | `first_min_r` = 4.675 ± 0.15 Å |
| 11 | `test_coordination_number` | `coordination_number` = 10.21 ± 1.5 |
| 12 | `test_coordination_number_rounded` | Rounded to 2 decimal places |

---

## 7. Oracle reference values

| Key | Oracle value | Tolerance |
|-----|-------------|-----------|
| `first_peak_r` | **3.675 Å** | ± 0.10 Å |
| `first_peak_gr` | **2.8838** | ± 0.40 |
| `first_min_r` | **4.675 Å** | ± 0.15 Å |
| `coordination_number` | **10.21** | ± 1.5 |

---

## 8. GitHub Actions triggers

| Comment on PR | Action |
|---|---|
| *(auto on push)* | Full rubric review + static checks |
| `/validate` | Docker build + oracle (reward=1) + NOP (reward=0) |
| `/run` | Live agent trials — measures pass@k (costs API credits) |
| `/rerun` | Force-refresh full review pipeline |

---

## 9. Local development commands

```bash
# Quick oracle + NOP check (no Docker)
python _v.py

# Validate metadata labels
python references/check-diversity-labels.py task/task.toml

# Check base image policy
bash references/check-base-image.sh task/

# Build Docker image
docker build -t argon-rdf task/environment/

# Run oracle inside Docker
docker run --rm \
  -v "$(pwd)/task/solution:/solution:ro" \
  argon-rdf bash /solution/solve.sh

# Run verifier inside Docker
docker run --rm \
  -v "$(pwd)/task/tests:/tests:ro" \
  argon-rdf bash /tests/test.sh && \
  docker run --rm \
    -v "$(pwd)/task/tests:/tests:ro" \
    argon-rdf cat /logs/verifier/reward.txt
```

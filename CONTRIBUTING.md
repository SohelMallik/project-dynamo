# Contributing — Development Guide

This document explains how to run the task locally, validate it, and submit
a pull request to the Dynamo benchmark.

---

## Prerequisites

- Python 3.13 (matches the Docker base image)
- [Docker](https://docs.docker.com/get-docker/) (for full environment validation)
- `numpy==2.2.6`, `pytest==8.4.1`, `pytest-json-ctrf==0.3.5`

Install local dev deps:

```bash
pip install numpy==2.2.6 pytest==8.4.1 pytest-json-ctrf==0.3.5
```

---

## Run the oracle locally (no Docker)

`_v.py` patches all paths so the oracle solution runs against the local
trajectory file and the verifier tests run against the local outputs:

```bash
python _v.py
```

Expected output:

```
ORACLE  12/12 PASS  OK
NOP     12/12 FAIL  OK
```

---

## Run the oracle inside Docker

Build the environment image and run the reference solution:

```bash
# Build
docker build -t argon-rdf-coordination task/environment/

# Run oracle solution
docker run --rm \
  -v "$(pwd)/task/solution:/solution:ro" \
  -v "$(pwd)/task/tests:/tests:ro" \
  argon-rdf-coordination \
  bash /solution/solve.sh

# Run verifier
docker run --rm \
  -v "$(pwd)/task/tests:/tests:ro" \
  argon-rdf-coordination \
  bash /tests/test.sh

# Check reward
docker run --rm \
  -v "$(pwd)/task/tests:/tests:ro" \
  argon-rdf-coordination \
  bash -c "bash /tests/test.sh && cat /logs/verifier/reward.txt"
```

---

## Project structure

```
task/
├── task.toml                  # Harbor metadata, timeouts, artifact list
├── instruction.md             # Agent instruction — the only file the agent sees
├── environment/
│   ├── Dockerfile             # Pinned base image; all deps baked in at build time
│   └── data/
│       ├── traj.xyz           # 100-frame liquid-Ar MD trajectory (input data)
│       └── README.md          # Data format and parameter description
├── solution/
│   ├── solve.sh               # Entry point called by Harbor: python3 /solution/solve.py
│   ├── solve.py               # Oracle solution (parse → PBC RDF → coord. number → write)
│   ├── requirements.txt       # Pinned solution deps (matches Dockerfile)
│   └── README.md              # Algorithm walkthrough for reviewers
└── tests/
    ├── test.sh                # Harbor verifier entry point (runs pytest, writes reward.txt)
    ├── test_outputs.py        # 12 pytest tests on /app/rdf.csv and /app/results.json
    ├── requirements.txt       # Pinned verifier deps (matches Dockerfile)
    └── conftest.py            # Ensures /app exists before tests run

.github/
├── PULL_REQUEST_TEMPLATE.md   # PR submission checklist
└── workflows/
    ├── dynamo-review.yml      # Auto-runs on every PR (rubric + static checks)
    ├── dynamo-validate.yml    # /validate → Docker build + oracle + nop
    ├── dynamo-run-trials.yml  # /run → live agent trials (pass@k)
    └── dynamo-rerun.yml       # /rerun → force-refresh full review

references/
├── dynamo-rubric.toml         # Rubric criteria used by automated review
├── diversity-taxonomy.toml    # Closed-set vocabulary for task metadata labels
├── check-base-image.sh        # Static check: Dockerfile base image policy
└── check-diversity-labels.py  # Static check: metadata label vocabulary validation

_v.py                          # Local oracle + NOP runner (no Docker required)
```

---

## Validate with GitHub Actions

After pushing to a PR branch:

| Action | PR comment | What it does |
|--------|-----------|-------------|
| Automated | *(automatic on push)* | Full rubric review + static checks |
| Oracle + NOP check | `/validate` | Docker build → oracle scores 1, NOP scores 0 |
| Agent trials | `/run` | Live agent pass@k (spends API credits) |
| Force re-review | `/rerun` | Re-runs full review under current pipeline |

---

## Checklist before submitting a PR

- [ ] `python _v.py` prints `ORACLE 12/12 PASS OK` and `NOP 12/12 FAIL OK`
- [ ] `docker build task/environment/` succeeds with no warnings
- [ ] All identifiers consistent across `instruction.md`, `solve.py`, `test_outputs.py`
- [ ] `task/task.toml` category/subcategory match `references/diversity-taxonomy.toml`
- [ ] No solution or test files copied into `environment/Dockerfile`
- [ ] No hardcoded expected values in `solve.py` (all derived from computation)
- [ ] `test.sh` installs nothing at verify time

## Task submission checklist

**Task name:** `dynamo/argon-rdf-coordination`
**Category:** `scientific_computing_and_domain_science / chemistry_and_materials_workflows`

---

### Local validation

- [ ] `python _v.py` → `ORACLE 12/12 PASS OK` and `NOP 12/12 FAIL OK`
- [ ] `docker build task/environment/` succeeds without errors

### Instruction & output contract

- [ ] `task/instruction.md` uses absolute paths (e.g. `/app/data/traj.xyz`)
- [ ] All output keys (`first_peak_r`, `first_peak_gr`, `first_min_r`, `coordination_number`) are explicitly stated in the instruction
- [ ] Output schemas for `/app/rdf.csv` and `/app/results.json` are fully documented
- [ ] No step-by-step procedure or tool hints in the instruction

### Solution

- [ ] `task/solution/solve.sh` + `task/solution/solve.py` produce correct outputs via genuine computation
- [ ] No hardcoded expected values in `solve.py`
- [ ] Oracle scores match `task/solution/README.md` expected values table

### Tests

- [ ] Every test function has a docstring explaining what it checks
- [ ] Each test is atomic (one logical requirement per function)
- [ ] `test.sh` does **not** run `pip install`, `apt-get`, or download anything
- [ ] All 12 tests pass with the oracle; all 12 fail with NOP

### Environment

- [ ] `task/environment/Dockerfile` uses the pre-approved pinned base image digest
- [ ] `numpy`, `pytest`, `pytest-json-ctrf` are version-pinned in the Dockerfile
- [ ] `solution/` and `tests/` are **not** copied into the Docker image
- [ ] `/app` is pre-created in the Dockerfile

### Metadata (`task/task.toml`)

- [ ] `category` and `subcategory` match values in `references/diversity-taxonomy.toml`
- [ ] `task_objective` values are from the closed set in `diversity-taxonomy.toml`
- [ ] `artifact_type` values are from the closed set in `diversity-taxonomy.toml`
- [ ] `expert_time_estimate_hours` is non-zero and plausible
- [ ] `artifacts` list at root level matches the paths the tests read

### Anti-cheat

- [ ] `task/environment/data/` contains no expected answers or oracle outputs
- [ ] Reference values only appear in `task/tests/test_outputs.py` (verifier-only)
- [ ] The trajectory `traj.xyz` is not obtainable from any public database

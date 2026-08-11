# argon-rdf-coordination

Professional reference solution to compute the radial distribution function g(r)
and the first coordination number for a liquid-argon molecular dynamics trajectory.

This repository provides a clear, well-tested implementation intended for
education, benchmarking, and verification of agent-based solutions in the
Harbor/Dynamo tasks framework. The implementation focuses on correctness,
numerical stability, and reproducibility.

## Quick summary

- **Goal:** Compute Ar–Ar radial distribution function `g(r)` and the first
  coordination number from a 100-frame MD trajectory (108 atoms per frame).
- **Key techniques:** minimum-image periodic boundary conditions, histogram
  normalisation to ideal-gas shell counts, robust local extrema detection,
  trapezoidal integration of g(r) r².
- **Stack:** Python 3.13, NumPy, pytest; Dockerfile included for reproducible
  execution.

## Why this matters

Radial distribution functions and coordination numbers are fundamental
observables in liquid-state physics and molecular simulation. Correctly
computing these quantities requires attention to periodic boundaries, volume
normalisation, and numerical integration — mistakes produce physically wrong
results. This repository demonstrates a compact, auditable pipeline that
produces oracle-quality outputs and is automatically verifiable.

## Contents

- `task/environment/data/traj.xyz` — 100-frame, 108-atom Lennard-Jones liquid
  argon trajectory (input).
- `task/solution/solve.py` — reference implementation (vectorised NumPy).
- `task/solution/README.md` — algorithm walkthrough and developer notes.
- `task/tests/test_outputs.py` — 12 pytest tests that validate outputs.
- `.github/workflows/` — CI workflows used by the review and validation system.

## Usage

1. Create and activate a Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate        # Windows
```

2. Install runtime and test dependencies:

```bash
python -m pip install numpy==2.2.6
python -m pip install pytest==8.4.1 pytest-json-ctrf==0.3.5
```

3. Run the reference solution locally (reads `task/environment/data/traj.xyz`):

```bash
python task/solution/solve.py
```

Outputs written (by default) to the task runtime layout:

- `rdf.csv` — CSV with header `r,gr` and 160 rows (r bin centres, g(r) values).
- `results.json` — JSON with keys `first_peak_r`, `first_peak_gr`,
  `first_min_r`, `coordination_number` (rounded to 2 d.p.).

## Running verification tests

Run the test suite to verify correctness and reproducibility:

```bash
pytest -q task/tests/test_outputs.py
```

The test suite checks file formats, physical sanity (hard-core exclusion,
asymptotic behaviour), and numerical agreement with the oracle reference
values within tight tolerances.

## Expected (oracle) results

These values are produced by the reference solution and used by the verifier:

- `first_peak_r` = 3.6750 Å
- `first_peak_gr` = 2.8838
- `first_min_r` = 4.6750 Å
- `coordination_number` = 10.21

## Implementation notes (algorithm)

1. Parse the multi-frame XYZ file and extract the per-frame cubic box length
   `L` from the comment line.
2. For each frame compute the pairwise displacement tensor `dr_ij` and apply
   the minimum-image convention: `dr -= round(dr / L) * L`.
3. Compute pairwise distances (upper-triangle only) and histogram into 160
   fixed-width bins spanning `r ∈ [0, 8.0 Å)` with `dr = 0.05 Å`.
4. Normalise using the ideal-gas shell expectation summed across frames:
   `n_ideal = Σ_frames(N_pairs / L^3) * 4π r^2 dr`, then `g(r) = hist / n_ideal`.
5. Locate the first peak via `argmax(g(r))` and scan for the first local
   minimum beyond `r = 2.5 Å`. Integrate `4πρ ∫ g(r) r^2 dr` up to that minimum
   to yield the first coordination number.

## Contributing

Contributions are welcome. For code changes please:

1. Fork the repository and create a feature branch.
2. Add tests (or update existing ones) to cover new behavior.
3. Open a pull request describing the change and its rationale.

## Notes & suggestions

- The implementation intentionally keeps dependencies minimal to ensure CI
  stability and easy review.
- If you want a shorter, CV-friendly one-line summary of this project, I can
  provide tailored variants for roles such as `Computational Scientist`,
  `Data Scientist`, or `Software Engineer`.

## License

This repository does not include an explicit license. Before redistributing or
reusing, add a `LICENSE` file that expresses the intended permissions.

# Solution

## Overview

`solve.sh` is the Oracle reference solution for the
`dynamo/argon-rdf-coordination` task. It is mounted at `/solution/`
by Harbor and calls `solve.py` to do the real work.

## Algorithm (`solve.py`)

1. **Parse trajectory** — reads `/app/data/traj.xyz` frame by frame,
   extracting the cubic box length `L` from each comment line
   (`box=<L>`).

2. **Compute pair distances with minimum-image PBC** — for each frame,
   builds the full (N×N×3) displacement tensor, applies the minimum-
   image convention (`dr -= round(dr/L)*L`), and extracts the upper-
   triangle distances (N*(N-1)/2 pairs).

3. **Histogram → g(r)** — accumulates distances into 160 bins of
   width 0.05 Å (0 – 8.0 Å).  Normalises each bin by the ideal-gas
   shell count:

   ```
   n_ideal = N_pairs * 4π r² dr / L³   (summed over all frames)
   g(r) = histogram / n_ideal
   ```

4. **Find first peak and first minimum** — `argmax(g(r))` for the peak;
   scan for the first local minimum beyond r = 2.5 Å for the minimum.

5. **Coordination number** — integrate with `numpy.trapz`:

   ```
   n₁ = 4π ρ ∫₀^{r_min} g(r) r² dr
   ```

   where `ρ = N / ⟨L⟩³` (averaged box length).

6. **Write outputs** — `/app/rdf.csv` (header `r,gr`, 160 rows) and
   `/app/results.json` with keys `first_peak_r`, `first_peak_gr`,
   `first_min_r`, `coordination_number` (rounded to 2 d.p.).

## Expected outputs

| Key | Value |
|-----|-------|
| `first_peak_r` | 3.675 Å |
| `first_peak_gr` | 2.88 |
| `first_min_r` | 4.675 Å |
| `coordination_number` | 10.21 |

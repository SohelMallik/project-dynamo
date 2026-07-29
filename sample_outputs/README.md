# Sample Outputs — Oracle Reference

This folder contains the reference outputs produced by the oracle solution
(`task/solution/solve.py`) running on the provided trajectory
(`task/environment/data/traj.xyz`).

These files are for **reviewer reference only**. They are NOT shipped inside
the Docker environment image and are NOT accessible to the agent during
task execution.

---

## rdf.csv

Radial distribution function g(r) for liquid Ar, 160 bins, 0–8.0 Å.

| Column | Description |
|--------|-------------|
| `r`    | Bin centre (Å), from 0.025 to 7.975 in steps of 0.05 |
| `gr`   | g(r) value (dimensionless) |

First few rows:

```
r,gr
0.025000,0.00000000
0.075000,0.00000000
...
3.675000,2.88380000   ← first peak
...
4.675000,0.79580000   ← first minimum
...
7.975000,~1.0         ← asymptotic limit
```

## results.json

```json
{
  "first_peak_r": 3.675,
  "first_peak_gr": 2.8838,
  "first_min_r": 4.675,
  "coordination_number": 10.21
}
```

| Key | Value | Physical meaning |
|-----|-------|-----------------|
| `first_peak_r` | 3.675 Å | Position of first Ar–Ar coordination shell (~1.08 σ_LJ) |
| `first_peak_gr` | 2.8838 | Height of first g(r) peak (liquid structure factor) |
| `first_min_r` | 4.675 Å | First post-peak minimum (first-shell cutoff radius) |
| `coordination_number` | 10.21 | Number of nearest Ar neighbours in first shell |

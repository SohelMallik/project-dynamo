A molecular dynamics trajectory of liquid argon is stored at `/app/data/traj.xyz`. It contains 100 frames, each with 108 atoms in a cubic simulation box. The file is in standard multi-frame XYZ format: each frame starts with the atom count (108) on its own line, followed by a comment line of the form `Frame <n> box=<L>` where `<L>` is the cubic box side length in Ångströms, then 108 lines of `Ar  x  y  z` (coordinates in Å).

Compute the **radial distribution function g(r)** for Ar–Ar pairs across all 100 frames using **minimum-image periodic boundary conditions**. Use a bin width of **0.05 Å** and a maximum distance of **8.0 Å** (i.e., r from 0 to 8.0 Å, 160 bins). The bin centres are at r = 0.025, 0.075, 0.125, …, 7.975 Å. Normalise g(r) by the ideal-gas pair density: for each bin at distance r with width dr, the expected number of pairs in an ideal gas of the same bulk density is $N_{pairs} \cdot \frac{4\pi r^2 \, dr}{\rho_{bulk}}$, where $N_{pairs}$ is the number of distinct atom pairs per frame and $\rho_{bulk} = N / L^3$.

Write the g(r) results to `/app/rdf.csv` as a CSV file with a header row `r,gr` and 160 data rows, one per bin. Values are floating-point; `r` is the bin centre, `gr` is g(r).

From the g(r), determine the **first coordination number** $n_1$: integrate g(r) over the first peak, from r = 0 to the first minimum after the first peak (the first local minimum of g(r) for r > 2.5 Å). Use the trapezoidal rule on the g(r) data. The coordination number is:

$$n_1 = 4\pi\rho \int_0^{r_{\min}} g(r)\, r^2 \, dr$$

where $\rho = N/L^3$ and $r_{\min}$ is the bin centre of the first minimum.

Write the following values to `/app/results.json` as a JSON object with these exact keys:

- `"first_peak_r"`: the bin-centre r (Å) at which g(r) is maximum (the first peak position)
- `"first_peak_gr"`: the g(r) value at that peak
- `"first_min_r"`: the bin-centre r (Å) of the first local minimum after the first peak (for r > 2.5 Å)
- `"coordination_number"`: the first coordination number $n_1$ (float, rounded to 2 decimal places)

All four values must be present. The box length L varies slightly per frame (read it from each frame's comment line). Average L across all frames when computing $\rho$ for the coordination number integral.

You have 900 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.

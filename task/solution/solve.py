"""
Reference solution: compute Ar-Ar radial distribution function and
first coordination number from the multi-frame XYZ trajectory at /app/data/traj.xyz.

Algorithm:
  1. Parse all frames from the XYZ file, reading the box length L from the comment line.
  2. Accumulate pair distances using minimum-image PBC across all frames.
  3. Normalize the histogram into g(r): divide by the ideal-gas count
     n_ideal = N_pairs * 4*pi*r^2*dr / (L^3) per bin.
  4. Find the first peak (maximum g(r)) and first minimum after r=2.5 Å.
  5. Integrate with the trapezoidal rule for the coordination number.
  6. Write /app/rdf.csv and /app/results.json.
"""

import numpy as np
import json
import csv
import sys
import os

TRAJ_PATH = "/app/data/traj.xyz"
RDF_PATH  = "/app/rdf.csv"
JSON_PATH = "/app/results.json"

DR    = 0.05   # bin width, Å
RMAX  = 8.0    # max distance, Å
NBINS = int(RMAX / DR)   # 160 bins
R_MIN_SEARCH = 2.5       # Å — only look for first minimum beyond this


def parse_xyz(path):
    """
    Parse a multi-frame XYZ file.
    Returns a list of (L, positions) tuples where:
      L     - float, cubic box side length (Å)
      positions - (N, 3) float64 array of Cartesian coordinates (Å)
    The comment line must contain 'box=<value>'.
    """
    frames = []
    with open(path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            n_atoms = int(line)
            comment = f.readline().strip()
            # Extract box length from "Frame N box=<L>"
            for token in comment.split():
                if token.startswith("box="):
                    L = float(token.split("=")[1])
                    break
            coords = np.empty((n_atoms, 3), dtype=np.float64)
            for i in range(n_atoms):
                parts = f.readline().split()
                coords[i, 0] = float(parts[1])
                coords[i, 1] = float(parts[2])
                coords[i, 2] = float(parts[3])
            frames.append((L, coords))
    return frames


def compute_rdf(frames):
    """
    Accumulate pair distances with minimum-image PBC and return normalised g(r).
    Returns (bin_centres, gr, avg_L) where:
      bin_centres - (NBINS,) array of r values at bin centres
      gr          - (NBINS,) array of g(r) values
      avg_L       - average box length across frames
    """
    hist = np.zeros(NBINS, dtype=np.float64)
    total_frames = len(frames)
    total_norm   = 0.0   # sum over frames of (N_pairs / L^3)

    for L, pos in frames:
        N = len(pos)
        # Vectorised: compute all upper-triangle pair distances
        # Use broadcasting; for N=108 this is manageable.
        # pos shape: (N, 3)
        diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]  # (N, N, 3)
        diff -= np.round(diff / L) * L   # minimum image
        r2   = np.sum(diff ** 2, axis=2)                       # (N, N)
        # Upper triangle indices only (i < j)
        idx  = np.triu_indices(N, k=1)
        r    = np.sqrt(r2[idx])
        # Filter by rmax
        mask = r < RMAX
        np.add.at(hist, (r[mask] / DR).astype(int), 1)
        N_pairs = N * (N - 1) // 2
        total_norm += N_pairs / (L ** 3)

    bin_centres = (np.arange(NBINS) + 0.5) * DR

    # Normalise: g(r) = hist[i] / (n_ideal * n_frames)
    # n_ideal per frame per bin = N_pairs * 4*pi*r^2*dr / L^3
    # summed over frames: total_norm * 4*pi*r^2*dr
    shell_vol = 4.0 * np.pi * bin_centres ** 2 * DR
    n_ideal   = total_norm * shell_vol   # total expected over all frames

    with np.errstate(invalid="ignore", divide="ignore"):
        gr = np.where(n_ideal > 0, hist / n_ideal, 0.0)

    avg_L = np.mean([L for L, _ in frames])
    return bin_centres, gr, avg_L


def find_first_peak_and_min(r, gr):
    """
    Return (peak_idx, min_idx) where:
      peak_idx - index of the global maximum in gr (first peak)
      min_idx  - index of the first local minimum after the peak, for r > R_MIN_SEARCH
    """
    peak_idx = int(np.argmax(gr))

    # Search for the first local minimum after the peak and beyond R_MIN_SEARCH
    search_start = max(peak_idx + 1, int(R_MIN_SEARCH / DR))
    min_idx = None
    for i in range(search_start, len(gr) - 1):
        if gr[i] <= gr[i - 1] and gr[i] <= gr[i + 1]:
            min_idx = i
            break
    if min_idx is None:
        # Fallback: find global minimum in search window
        sub = gr[search_start:]
        min_idx = search_start + int(np.argmin(sub))

    return peak_idx, min_idx


def coordination_number(r, gr, min_idx, rho):
    """
    Integrate g(r)*r^2 from r[0] to r[min_idx] using the trapezoidal rule,
    multiply by 4*pi*rho.
    """
    r_int  = r[:min_idx + 1]
    gr_int = gr[:min_idx + 1]
    integral = np.trapezoid(gr_int * r_int ** 2, r_int)
    return 4.0 * np.pi * rho * integral


def main():
    print("Parsing trajectory...")
    frames = parse_xyz(TRAJ_PATH)
    print(f"  {len(frames)} frames loaded, N={len(frames[0][1])} atoms per frame")

    print("Computing RDF...")
    bin_centres, gr, avg_L = compute_rdf(frames)

    # Write rdf.csv
    with open(RDF_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["r", "gr"])
        for r_val, gr_val in zip(bin_centres, gr):
            writer.writerow([f"{r_val:.6f}", f"{gr_val:.8f}"])
    print(f"  Written {RDF_PATH}")

    # Find peak and minimum
    peak_idx, min_idx = find_first_peak_and_min(bin_centres, gr)
    print(f"  First peak at r={bin_centres[peak_idx]:.4f} Å, g(r)={gr[peak_idx]:.4f}")
    print(f"  First minimum at r={bin_centres[min_idx]:.4f} Å, g(r)={gr[min_idx]:.4f}")

    # Coordination number
    N = len(frames[0][1])
    rho = N / (avg_L ** 3)
    n1  = coordination_number(bin_centres, gr, min_idx, rho)
    print(f"  Average box length: {avg_L:.4f} Å")
    print(f"  rho = {rho:.6f} Å^-3")
    print(f"  First coordination number n1 = {n1:.4f} -> {round(n1, 2)}")

    results = {
        "first_peak_r":        round(float(bin_centres[peak_idx]), 4),
        "first_peak_gr":       round(float(gr[peak_idx]), 4),
        "first_min_r":         round(float(bin_centres[min_idx]), 4),
        "coordination_number": round(float(n1), 2),
    }
    with open(JSON_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Written {JSON_PATH}")
    print("Done.")
    return results


if __name__ == "__main__":
    main()

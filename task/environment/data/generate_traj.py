#!/usr/bin/env python3
"""
Generates the liquid-argon NVT Monte Carlo trajectory used as task input:
  task/environment/data/traj.xyz

This script is provided for full reproducibility of the input data.
It was run ONCE to produce traj.xyz; the resulting file is committed to the
repository. You do NOT need to run this script to use the task — the
trajectory file is already present.

Simulation parameters:
  N        = 108 atoms (Argon)
  rho*     = 0.844    (reduced density  ρ* = ρ σ³)
  T*       = 0.85     (reduced temperature T* = k_B T / ε)
  sigma    = 3.405 Å  (LJ sigma for Ar)
  epsilon  = 119.8 K  (LJ epsilon/k_B for Ar)
  r_cut    = 2.5 sigma (LJ cutoff)
  frames   = 100      (saved every 500 MC sweeps after equilibration)
  seed     = 20260605

Output: task/environment/data/traj.xyz
"""

import numpy as np
import os

# ── Simulation parameters ──────────────────────────────────────────────────
N        = 108          # number of atoms
RHO_STAR = 0.844        # reduced density ρ* = ρ σ³
T_STAR   = 0.85         # reduced temperature T* = k_B T / ε
SIGMA    = 3.405        # Å  — LJ sigma for Ar
EPSILON  = 119.8        # K  — LJ epsilon/k_B for Ar
R_CUT    = 2.5 * SIGMA  # Å  — LJ cutoff
N_EQUIL  = 50_000       # MC sweeps equilibration
N_PROD   = 500          # MC sweeps between saved frames
N_FRAMES = 100          # number of frames to save
SEED     = 20260605
OUT_PATH = os.path.join(os.path.dirname(__file__), "traj.xyz")

# ── Derived quantities ─────────────────────────────────────────────────────
rng  = np.random.default_rng(SEED)
rho  = RHO_STAR / (SIGMA ** 3)          # Å⁻³
L    = (N / rho) ** (1 / 3)             # box length, Å
beta = 1.0 / T_STAR                     # 1 / (k_B T) in reduced units


def lj_pair(r2, sigma2, eps):
    """Return LJ energy for squared distance r2."""
    s2   = sigma2 / r2
    s6   = s2 ** 3
    return 4.0 * eps * (s6 * s6 - s6)


def lj_pair_reduced(r2):
    """LJ in reduced units (sigma=1, eps=1)."""
    s6 = (1.0 / r2) ** 3
    return 4.0 * (s6 * s6 - s6)


def energy_of_atom(pos, idx, L, r_cut2):
    """Total pair energy of atom idx with all other atoms (minimum image PBC)."""
    dr  = pos[idx] - pos                        # (N, 3)
    dr -= np.round(dr / L) * L                  # minimum image
    r2  = np.sum(dr ** 2, axis=1)               # (N,)
    r2[idx] = 1e30                              # exclude self
    mask = r2 < r_cut2
    return np.sum(lj_pair_reduced(r2[mask]))


def total_energy(pos, L, r_cut2):
    """Full system energy (no double-counting)."""
    E = 0.0
    for i in range(len(pos)):
        E += energy_of_atom(pos, i, L, r_cut2)
    return E / 2.0


def mc_sweep(pos, L, r_cut2, beta, delta, rng):
    """One MC sweep: N attempted single-atom displacements."""
    N = len(pos)
    acc = 0
    for _ in range(N):
        i   = rng.integers(N)
        E_old = energy_of_atom(pos, i, L, r_cut2)
        trial = pos[i] + (rng.random(3) - 0.5) * 2 * delta
        trial %= L                              # wrap into box
        pos_old = pos[i].copy()
        pos[i]  = trial
        E_new   = energy_of_atom(pos, i, L, r_cut2)
        dE = E_new - E_old
        if dE < 0 or rng.random() < np.exp(-beta * dE):
            acc += 1
        else:
            pos[i] = pos_old
    return acc / N


# ── FCC-like initial configuration ────────────────────────────────────────
def fcc_init(N, L):
    """Place N atoms on an approximate FCC lattice in a cubic box of side L."""
    # Find number of unit cells needed: each FCC cell has 4 atoms
    n_cells = int(np.ceil((N / 4) ** (1 / 3)))
    basis   = np.array([[0, 0, 0], [0.5, 0.5, 0],
                        [0.5, 0, 0.5], [0, 0.5, 0.5]], dtype=float)
    a       = L / n_cells
    pos     = []
    for ix in range(n_cells):
        for iy in range(n_cells):
            for iz in range(n_cells):
                for b in basis:
                    pos.append((np.array([ix, iy, iz]) + b) * a)
                    if len(pos) == N:
                        return np.array(pos) % L
    return np.array(pos[:N]) % L


def main():
    print(f"Generating liquid-Ar NVT trajectory: N={N}, rho*={RHO_STAR}, T*={T_STAR}")
    print(f"  Box length L = {L:.6f} Å,  r_cut = {R_CUT:.4f} Å")
    print(f"  Equilibration: {N_EQUIL} sweeps,  Production: {N_PROD} sweeps/frame")

    r_cut2 = R_CUT ** 2
    pos    = fcc_init(N, L)

    # ── Equilibration ──────────────────────────────────────────────────────
    delta  = 0.1 * L   # initial displacement magnitude
    print("  Equilibrating...")
    for sweep in range(N_EQUIL):
        acc = mc_sweep(pos, L, r_cut2, beta, delta, rng)
        # Tune delta every 1000 sweeps to keep ~50% acceptance
        if (sweep + 1) % 1000 == 0:
            if acc > 0.55:
                delta = min(delta * 1.1, 0.5 * L)
            elif acc < 0.45:
                delta = max(delta * 0.9, 0.01)
    print(f"  Equilibration done. delta = {delta:.4f} Å")

    # ── Production run — save N_FRAMES frames ─────────────────────────────
    print(f"  Production: saving {N_FRAMES} frames...")
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for frame in range(N_FRAMES):
            for _ in range(N_PROD):
                mc_sweep(pos, L, r_cut2, beta, delta, rng)
            # Slightly fluctuate L to simulate NPT-like variation (NVT exact L)
            L_frame = L * (1.0 + rng.uniform(-0.0002, 0.0002))
            f.write(f"{N}\n")
            f.write(f"Frame {frame} box={L_frame:.6f}\n")
            for atom in pos:
                ax, ay, az = atom % L_frame
                f.write(f"Ar  {ax:.6f}  {ay:.6f}  {az:.6f}\n")
            if (frame + 1) % 10 == 0:
                print(f"    Frame {frame + 1}/{N_FRAMES}")

    print(f"  Written: {OUT_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()

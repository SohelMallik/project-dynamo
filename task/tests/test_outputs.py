"""
Verifier tests for the RDF and coordination number task.

Expected reference values (computed with the oracle solution):
  first_peak_r      ≈ 3.675 Å    (Ar-Ar first RDF peak, ~1.08 sigma_LJ)
  first_peak_gr     ≈ 2.88       (typical liquid-Ar first peak height)
  first_min_r       ≈ 4.675 Å    (first post-peak minimum)
  coordination_number ≈ 10.21    (first-shell coordination number)

Tolerances are calibrated to accept any correct approach:
  - ±0.10 Å on peak/minimum positions (accounts for ±2 bins width variation)
  - ±0.40 on peak g(r) value (accounts for slight normalization differences)
  - ±1.50 on coordination number (accounts for integration-bound choice variation)
"""

import json
import csv
import os
import math
import pytest

RDF_PATH  = "/app/rdf.csv"
JSON_PATH = "/app/results.json"

# --- Oracle reference values ---
REF_PEAK_R    = 3.675   # Å
REF_PEAK_GR   = 2.8838
REF_MIN_R     = 4.675   # Å
REF_CN        = 10.21


def test_rdf_csv_exists():
    """Verify that /app/rdf.csv was produced by the agent."""
    assert os.path.isfile(RDF_PATH), f"Expected output file {RDF_PATH} not found"


def test_rdf_csv_format():
    """
    Verify that /app/rdf.csv has the correct header ('r,gr') and exactly 160 data rows
    corresponding to bins from 0.025 to 7.975 Å with a 0.05 Å bin width.
    """
    with open(RDF_PATH, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["r", "gr"], (
        f"Expected header 'r,gr', got {rows[0]}"
    )
    data_rows = rows[1:]
    assert len(data_rows) == 160, (
        f"Expected 160 data rows (0 to 8.0 Å, 0.05 Å bins), got {len(data_rows)}"
    )

    # Verify first and last bin centres
    r_first = float(data_rows[0][0])
    r_last  = float(data_rows[-1][0])
    assert abs(r_first - 0.025) < 0.005, (
        f"First bin centre should be 0.025 Å, got {r_first:.4f}"
    )
    assert abs(r_last - 7.975) < 0.005, (
        f"Last bin centre should be 7.975 Å, got {r_last:.4f}"
    )


def test_rdf_hard_core_exclusion():
    """
    Verify that g(r) = 0 for very small r (hard-core exclusion, r < 2.0 Å).
    For liquid Ar with LJ sigma = 3.405 Å, no atom pairs exist at separations
    smaller than ~2.5 Å, so g(r) must be essentially zero below 2.0 Å.
    """
    with open(RDF_PATH, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)[1:]  # skip header

    r_vals  = [float(row[0]) for row in rows]
    gr_vals = [float(row[1]) for row in rows]

    short_range = [gr for r, gr in zip(r_vals, gr_vals) if r < 2.0]
    assert all(gr < 0.05 for gr in short_range), (
        "g(r) must be ~0 for r < 2.0 Å (hard-core exclusion)"
    )


def test_rdf_asymptotic_limit():
    """
    Verify that g(r) approaches 1 at large distances (r > 7.0 Å).
    By definition, g(r) → 1 as r → ∞ for a homogeneous fluid; at r > 7 Å
    liquid Ar structure is essentially uncorrelated and g(r) should be close to 1.
    """
    with open(RDF_PATH, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)[1:]  # skip header

    r_vals  = [float(row[0]) for row in rows]
    gr_vals = [float(row[1]) for row in rows]

    long_range = [gr for r, gr in zip(r_vals, gr_vals) if r > 7.0]
    avg_long = sum(long_range) / len(long_range)
    assert 0.6 < avg_long < 1.4, (
        f"g(r) should approach 1.0 for r > 7 Å, got mean = {avg_long:.3f}"
    )


def test_rdf_liquid_structure_peak():
    """
    Verify that g(r) has a clear first peak above 1.5, indicating liquid structure.
    For liquid Ar at rho*=0.844, T*=0.85 the first peak is ~2.5–3.2; any value
    above 1.5 confirms the distribution was correctly normalized and the liquid
    shell structure is resolved.
    """
    with open(RDF_PATH, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)[1:]  # skip header

    gr_vals = [float(row[1]) for row in rows]

    peak_gr = max(gr_vals)
    assert peak_gr > 1.5, (
        f"First peak of g(r) should exceed 1.5 for liquid structure, got {peak_gr:.3f}"
    )


def test_results_json_exists():
    """Verify that /app/results.json was produced by the agent."""
    assert os.path.isfile(JSON_PATH), f"Expected output file {JSON_PATH} not found"


def test_results_json_keys():
    """
    Verify that /app/results.json contains all four required keys:
    first_peak_r, first_peak_gr, first_min_r, coordination_number.
    """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    required_keys = ["first_peak_r", "first_peak_gr", "first_min_r", "coordination_number"]
    for key in required_keys:
        assert key in data, f"Missing required key '{key}' in {JSON_PATH}"


def test_first_peak_position():
    """
    Verify that the first RDF peak position is near 3.675 Å (within ±0.10 Å).
    For liquid Ar with LJ sigma=3.405 Å, the first peak is at ~1.08 sigma ≈ 3.68 Å.
    A tolerance of ±0.10 Å (±2 bins) accepts correct binning variants.
    """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    peak_r = float(data["first_peak_r"])
    assert abs(peak_r - REF_PEAK_R) <= 0.10, (
        f"first_peak_r = {peak_r:.4f} Å, expected {REF_PEAK_R:.4f} ± 0.10 Å"
    )


def test_first_peak_height():
    """
    Verify that the first RDF peak height g(r_peak) is near 2.88 (within ±0.40).
    Typical liquid Ar at rho*=0.844, T*=0.85 has a first peak of ~2.5-3.2.
    Tolerance of ±0.40 accepts variations from different normalization conventions.
    """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    peak_gr = float(data["first_peak_gr"])
    assert abs(peak_gr - REF_PEAK_GR) <= 0.40, (
        f"first_peak_gr = {peak_gr:.4f}, expected {REF_PEAK_GR:.4f} ± 0.40"
    )


def test_first_minimum_position():
    """
    Verify that the first post-peak minimum is near 4.675 Å (within ±0.15 Å).
    This separates the first and second coordination shells of liquid Ar.
    Tolerance of ±0.15 Å (±3 bins) accepts noisy minimum detection.
    """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    min_r = float(data["first_min_r"])
    assert abs(min_r - REF_MIN_R) <= 0.15, (
        f"first_min_r = {min_r:.4f} Å, expected {REF_MIN_R:.4f} ± 0.15 Å"
    )


def test_coordination_number():
    """
    Verify that the first coordination number is near 10.21 (within ±1.5).
    Liquid Ar at this state point has ~10-12 nearest neighbours depending
    on the exact integration cutoff chosen at the first minimum.
    A tolerance of ±1.5 accommodates different trapezoidal integration schemes
    and slight variations in where the first minimum is identified.
    """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    cn = float(data["coordination_number"])
    assert abs(cn - REF_CN) <= 1.5, (
        f"coordination_number = {cn:.2f}, expected {REF_CN:.2f} ± 1.5"
    )


def test_coordination_number_rounded():
    """
    Verify that coordination_number in results.json is rounded to 2 decimal places
    as specified in the instruction.
    """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    cn = data["coordination_number"]
    # Check it's a number and has at most 2 decimal places
    assert isinstance(cn, (int, float)), "coordination_number must be a number"
    cn_float = float(cn)
    # It should equal its own rounding to 2 decimals (within float precision)
    assert abs(cn_float - round(cn_float, 2)) < 1e-9, (
        f"coordination_number {cn} is not rounded to 2 decimal places"
    )

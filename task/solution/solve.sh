#!/bin/bash
# Reference solution: compute Ar-Ar RDF and first coordination number
# from the MD trajectory at /app/data/traj.xyz.
# Outputs: /app/rdf.csv and /app/results.json

set -e
python3 /solution/solve.py

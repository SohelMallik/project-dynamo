import types, os, sys

def patched_solve():
    c = open("task/solution/solve.py").read()
    c = c.replace('TRAJ_PATH = "/app/data/traj.xyz"', 'TRAJ_PATH = "task/environment/data/traj.xyz"')
    c = c.replace('RDF_PATH  = "/app/rdf.csv"',        'RDF_PATH  = "task/_r.csv"')
    c = c.replace('JSON_PATH = "/app/results.json"',   'JSON_PATH = "task/_j.json"')
    m = types.ModuleType("s"); exec(c, m.__dict__); return m.main()

def patched_verifier(rdf, jsn):
    c = open("task/tests/test_outputs.py").read()
    c = c.replace("/app/rdf.csv", rdf).replace("/app/results.json", jsn)
    v = types.ModuleType("v"); exec(c, v.__dict__); return v

print("--- ORACLE ---")
r = patched_solve()
print("  first_peak_r        :", r["first_peak_r"])
print("  first_peak_gr       :", round(r["first_peak_gr"], 4))
print("  first_min_r         :", r["first_min_r"])
print("  coordination_number :", r["coordination_number"])

v = patched_verifier("task/_r.csv", "task/_j.json")
tests = sorted(n for n in dir(v) if n.startswith("test_"))
op = of = 0
for t in tests:
    try:    getattr(v,t)(); print("  PASS ", t); op += 1
    except Exception as e: print("  FAIL ", t, "->", e); of += 1
os.remove("task/_r.csv"); os.remove("task/_j.json")

print("\n--- NOP ---")
v2 = patched_verifier("task/_nop_r.csv", "task/_nop_j.json")
nf = np_ = 0
for t in tests:
    try:    getattr(v2,t)(); print("  PASS (wrong!)", t); np_ += 1
    except: print("  FAIL (correct)", t); nf += 1

print("\nORACLE  %d/10 PASS  %s" % (op, "OK" if of==0 else "FAIL"))
print("NOP     %d/10 FAIL  %s" % (nf, "OK" if np_==0 else "FAIL"))
sys.exit(0 if of==0 and np_==0 else 1)

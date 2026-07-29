import types, os
os.makedirs("sample_outputs", exist_ok=True)
c = open("task/solution/solve.py").read()
c = c.replace('TRAJ_PATH = "/app/data/traj.xyz"', 'TRAJ_PATH = "task/environment/data/traj.xyz"')
c = c.replace('RDF_PATH  = "/app/rdf.csv"',        'RDF_PATH  = "sample_outputs/rdf.csv"')
c = c.replace('JSON_PATH = "/app/results.json"',   'JSON_PATH = "sample_outputs/results.json"')
m = types.ModuleType("s"); exec(c, m.__dict__); m.main()

import os
import json

model_name = "firebug"

# Load results.json from sim results of model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = f"../workspace/{model_name}"
results_path = os.path.abspath(os.path.join(script_dir, model_path, "results.json"))

# Load results.json
with open(results_path) as f:
    results = json.load(f)

print(results)

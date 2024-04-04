import json
import os
import sys
import importlib
import time

import numpy as np
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import Session


# Load dataset from csv file
def load_dataset(dataset):
    data = []
    with open(dataset, "r") as file:
        lines = file.readlines()
        for line in lines:
            row = line.strip().split(",")
            data.append(row)

    X = np.array(data)[1:, :3].astype(float)  # ["yoc", "area", "renov"]

    return X


# Create dataset for validation of thermal 3R2C models
def create_validation_data(X):
    # Year of construction: 1850 - 2024
    years = np.arange(1850, 2024, 1)
    # Concatenate years three times
    years = np.concatenate((years, years, years))
    # Sort years in ascending order
    years = np.sort(years)

    X_val = np.zeros((len(years), 3))
    X_val[:, 0] = years
    type_code = []  # Building type code, e.g. A1, A2, A3, B1, ...

    for i, year in enumerate(years):
        if year <= 1859:
            n = 0
            code = "A"
        elif year > 1859 and year <= 1918:
            n = 1
            code = "B"
        elif year > 1918 and year <= 1948:
            n = 2
            code = "C"
        elif year > 1948 and year <= 1957:
            n = 3
            code = "D"
        elif year > 1957 and year <= 1968:
            n = 4
            code = "E"
        elif year > 1968 and year <= 1978:
            n = 5
            code = "F"
        elif year > 1978 and year <= 1983:
            n = 6
            code = "G"
        elif year > 1983 and year <= 1994:
            n = 7
            code = "H"
        elif year > 1994 and year <= 2001:
            n = 8
            code = "I"
        elif year > 2001 and year <= 2009:
            n = 9
            code = "J"
        elif year > 2009 and year <= 2015:
            n = 10
            code = "K"
        elif year > 2015:
            n = 11
            code = "L"

        X_val[i, 1:] = X[i % 3 + (n * 3), 1:]
        type_code.append(code + str(i % 3 + 1))

    return X_val, type_code


# Path to model directory with model_congif.json and ferntree app
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.abspath(os.path.join(script_dir, "..", "workspace/validation"))
ft_path = os.path.abspath(os.path.join(script_dir, "..", "ferntree"))

# Create validation data
X = load_dataset(os.path.join(script_dir, "data/3R2C_validation.csv"))
X_val, type_code = create_validation_data(X)

# Load model-config.json
model_config_file = os.path.join(model_path, "model_config.json")
with open(model_config_file, "r") as file:
    model_specs = json.load(file)

# Set up database connection
sys.path.insert(0, os.path.join(ft_path, "components"))
database = importlib.import_module("database.database")
orm_models = importlib.import_module("database.orm_models")
db = database.PostgresDatabase()
engine = create_engine(db.db_url)


# Execute simulations with thermal model specs (yoc, area, renov) from validation data
E_th = []
start_time = time.time()
for i in range(X_val.shape[0]):
    print(f"{i} / {X_val.shape[0]}")

    yoc = int(X_val[i, 0])
    area = int(X_val[i, 1])
    renov = int(X_val[i, 2])
    print(f"yoc: {yoc}, area: {area}, renov: {renov}, type_code: {type_code[i]}")

    # Write model specs to model_config.json
    model_specs["house"]["heating_sys"]["thermal_model"]["yoc"] = yoc
    model_specs["house"]["heating_sys"]["thermal_model"]["heated_area"] = area
    model_specs["house"]["heating_sys"]["thermal_model"]["renovation"] = renov

    with open(model_config_file, "w") as file:
        json.dump(model_specs, file, indent=4)

    # Run simulation
    os.system(f"python {ft_path}/ferntree.py -m validation")

    # Get results of simulation
    with Session(engine) as session:
        results = session.query(orm_models.Timestep).all()

    # Get annual thermal energy demand
    P_heat_th = [row.P_heat_th for row in results]  # [kW], timebase 1h
    E_th.append(sum(P_heat_th) / 1e3)  # [MWh]
    print(f"{type_code[i]}: {E_th[-1]:.2f} MWh")


# Group average annual thermal energy demand by building type code
df = pd.DataFrame({"type_code": type_code[: len(E_th)], "E_th": E_th})
# Write dataset to csv file
df.to_csv(os.path.join(script_dir, "results/thermal_energy_demand.csv"), index=False)

end_time = time.time()
print(f"Execution time: {(end_time - start_time)/60.0:.2f} minutes.")

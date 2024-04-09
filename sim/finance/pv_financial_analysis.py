import os
import json
import time

import pandas as pd
import matplotlib.pyplot as plt

start_time = time.time()

model_name = "firebug"

# Load results.json from sim results of model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = f"../workspace/{model_name}"
results_path = os.path.abspath(os.path.join(script_dir, model_path, "results.json"))

# Load results.json
with open(results_path) as f:
    results = json.load(f)


# Input from simulation results
pv_size = results.get("model").get("pv_size")  # kWp
bat_cap = results.get("model").get("bat_cap")  # kWh
bat_power = results.get("model").get("bat_power")  # kW

annual_baseload_demand = results.get("results").get("annual_baseload_demand")  # kWh
annual_pv_generation = results.get("results").get("annual_pv_generation")  # kWh
annual_grid_consumption = results.get("results").get("annual_grid_consumption")  # kWh
annual_grid_feed_in = results.get("results").get("annual_grid_feed_in")  # kWh
annual_self_consumption = results.get("results").get("annual_self_consumption")  # kWh

# Required user input or default/estimated values
elecetricity_price = 0.31  # €/kWh
price_increase = 0.025  # annual price increase

down_payment_percentage = 0.2  # upfront payment of total cost
repayment_percentage = 0.05  # annual repayment of total cost
interest_rate = 0.03  # annual interest rate

price_per_kwp = 1700  # €/kWp
module_degredation = 0.01  # %/year
operating_cost = 0.015  # %/year
feed_in_tariff = 0.08  # €/kWh


# Calculations
system_cost = price_per_kwp * pv_size  # €
self_consumption_rate = annual_self_consumption / annual_pv_generation

df = pd.DataFrame()
df["year"] = range(31)
df["consumption"] = annual_baseload_demand
df["electricity_price"] = elecetricity_price * (1 + price_increase) ** df["year"]
df["electricity_cost_nopv"] = df["consumption"] * df["electricity_price"]
df["pv_generation"] = annual_pv_generation * (1 - module_degredation) ** df["year"]
df["self_consumption"] = df["pv_generation"] * self_consumption_rate
df["electricity_cost_pv"] = (df["consumption"] - df["self_consumption"]) * df[
    "electricity_price"
]
df["savings"] = df["electricity_cost_nopv"] - df["electricity_cost_pv"]
df["feed_in"] = df["pv_generation"] - df["self_consumption"]
df["feed_in_revenue"] = df["feed_in"] * feed_in_tariff
df["operating_cost"] = system_cost * operating_cost * (1 + price_increase) ** df["year"]
df["net_revenue"] = df["savings"] + df["feed_in_revenue"] - df["operating_cost"]
df["cumulative_net_revenue"] = df["net_revenue"].cumsum()

# Calculate loan
loan = [system_cost * (1 - down_payment_percentage)]
repayment = [0]  # system_cost * repayment_percentage
interest = [loan[0] * interest_rate]

for year in range(len(df) - 1):
    loan_next_year = loan[year] - repayment[year]
    loan.append(loan_next_year if loan_next_year > 0 else 0)
    repayment.append(loan[0] * repayment_percentage if loan_next_year > 0 else 0)
    interest.append(loan_next_year * interest_rate)

df["loan"] = loan
df["repayment"] = repayment
df["interest"] = interest
df["capital_cost"] = df["repayment"] + df["interest"]
df["cash_flow"] = df["net_revenue"] - df["capital_cost"]

# Year when loan is paid off
loan_paid_off = df[df["loan"] == 0].iloc[0]["year"] - 1

# Calculate when break-even is reached
break_even_year = int(df[df["cumulative_net_revenue"] > system_cost].iloc[0]["year"])
# Interpolate break-even year
break_even_year_exact = (break_even_year - 1) + (
    system_cost - df.iloc[break_even_year - 1]["cumulative_net_revenue"]
) / df.iloc[break_even_year]["net_revenue"]

end_time = time.time()
print(f"Execution time: {end_time - start_time:.2f} s")

# Plot break-even analysis

plt.figure(figsize=(10, 6))
plt.plot(df["year"], df["cumulative_net_revenue"], label="Cumulative Net Revenue")
# Plot cumulative cash flow
plt.plot(df["year"], df["cash_flow"].cumsum(), label="Cumulative Cash Flow")
plt.axvline(loan_paid_off, color="grey", linestyle="--", label="Load Paid Off")
plt.text(
    loan_paid_off + 0.5,
    df["cash_flow"].cumsum().max() * 0.3,
    f"Loan paid off after {int(loan_paid_off)} years",
)

# System cost
plt.axhline(system_cost, color="red", linestyle="--", label="System Cost")
plt.text(df["year"].max() * 0.1, system_cost * 1.1, f"System Cost: {system_cost:.2f} €")

# Break-even year
plt.axvline(break_even_year_exact, color="green", linestyle="--", label="Break Even")
plt.text(
    break_even_year_exact + 0.5,
    df["cumulative_net_revenue"].max() * 0.9,
    f"Break Even: {break_even_year_exact:.2f} years",
)
plt.ylim(0, df["cumulative_net_revenue"].max() * 1.1)


plt.xlabel("Year")
plt.ylabel("€")
plt.title("Break Even Analysis")
plt.legend()
plt.grid()
plt.show()

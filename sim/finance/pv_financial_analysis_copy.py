import os
import json
import time
import pandas as pd
import numpy as np


def load_results(model_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = f"../workspace/{model_name}"
    results_path = os.path.abspath(os.path.join(script_dir, model_path, "results.json"))

    with open(results_path) as f:
        results = json.load(f)

    return results


def calculate_financial_analysis(results, settings):
    pv_size = results["model"]["pv_size"]  # kWp
    annual_baseload_demand = results["results"]["annual_baseload_demand"]  # kWh
    annual_pv_generation = results["results"]["annual_pv_generation"]  # kWh
    annual_self_consumption = results["results"]["annual_self_consumption"]  # kWh

    electricity_price = settings["electricity_price"]  # €/kWh
    price_increase = settings["price_increase"]  # annual price increase
    price_per_kwp = settings["price_per_kwp"]  # €/kWp
    module_degradation = settings["module_degradation"]  # %/year
    operating_cost = settings["operating_cost"]  # %/year
    feed_in_tariff = settings["feed_in_tariff"]  # €/kWh

    system_cost = price_per_kwp * pv_size  # €
    self_consumption_rate = annual_self_consumption / annual_pv_generation

    years = np.arange(31)
    df = pd.DataFrame(
        {
            "year": years,
            "consumption": annual_baseload_demand,
            "electricity_price": electricity_price * (1 + price_increase) ** years,
            "pv_generation": annual_pv_generation * (1 - module_degradation) ** years,
        }
    )

    df["electricity_cost_nopv"] = df["consumption"] * df["electricity_price"]
    df["self_consumption"] = df["pv_generation"] * self_consumption_rate
    df["electricity_cost_pv"] = (df["consumption"] - df["self_consumption"]) * df[
        "electricity_price"
    ]
    df["savings"] = df["electricity_cost_nopv"] - df["electricity_cost_pv"]
    df["feed_in"] = df["pv_generation"] - df["self_consumption"]
    df["feed_in_revenue"] = df["feed_in"] * feed_in_tariff
    df["operating_cost"] = system_cost * operating_cost * (1 + price_increase) ** years
    df["net_revenue"] = df["savings"] + df["feed_in_revenue"] - df["operating_cost"]
    df["cumulative_net_revenue"] = df["net_revenue"].cumsum()

    return df


def calculate_loan(df, system_cost):
    down_payment_percentage = 0.2  # upfront payment of total cost
    repayment_percentage = 0.05  # annual repayment of total cost
    interest_rate = 0.03  # annual interest rate

    loan = [system_cost * (1 - down_payment_percentage)]
    repayment = [0]
    interest = [loan[0] * interest_rate]

    for year in df["year"].iloc[1:]:
        loan_next_year = max(loan[-1] - repayment[-1], 0)
        repayment_next_year = (
            loan[0] * repayment_percentage if loan_next_year > 0 else 0
        )
        interest_next_year = loan_next_year * interest_rate

        loan.append(loan_next_year)
        repayment.append(repayment_next_year)
        interest.append(interest_next_year)

    df["loan"] = loan
    df["repayment"] = repayment
    df["interest"] = interest
    df["capital_cost"] = df["repayment"] + df["interest"]
    df["cash_flow"] = df["net_revenue"] - df["capital_cost"]

    return df


def calculate_loan_paid_off_year(df):
    loan_paid_off = df.loc[df["loan"] == 0, "year"].iloc[0] - 1
    return loan_paid_off


def calculate_break_even_year(df, system_cost):
    break_even_year = df.loc[df["cumulative_net_revenue"] > system_cost, "year"].iloc[0]
    break_even_year_exact = (break_even_year - 1) + (
        system_cost - df.loc[break_even_year - 1, "cumulative_net_revenue"]
    ) / df.loc[break_even_year, "net_revenue"]
    return break_even_year_exact


def main():
    start_time = time.time()

    model_name = "firebug"
    results = load_results(model_name)

    settings = {
        "electricity_price": 0.31,  # €/kWh
        "price_increase": 0.025,  # annual price increase
        "price_per_kwp": 1700,  # €/kWp
        "module_degradation": 0.01,  # %/year
        "operating_cost": 0.015,  # %/year
        "feed_in_tariff": 0.08,  # €/kWh
    }
    df = calculate_financial_analysis(results, settings)
    system_cost = settings["price_per_kwp"] * results["model"]["pv_size"]
    df = calculate_loan(df, system_cost)
    loan_paid_off = calculate_loan_paid_off_year(df)
    break_even_year_exact = calculate_break_even_year(df, system_cost)

    print(f"Loan paid off year: {loan_paid_off}")
    print(f"Break-even year: {break_even_year_exact:.2f}")

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} s")


if __name__ == "__main__":
    main()

import os

import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
file_path = os.path.abspath(__file__)

year = 2023
months = range(1, 2)

df_year = pd.DataFrame()

for month in months:
    # Load dataset
    csv_name = f"ckw_opendata_smartmeter_dataset_b_{year}{month:02d}.csv"
    data_dir = os.path.join(os.path.dirname(file_path), "data", "ckw", csv_name)
    df_month = pd.read_csv(data_dir)

    area_codes = df_month["area_code"].unique()

    plt.figure(figsize=(30, 5))

    for area_code in area_codes:
        df_area = df_month[df_month["area_code"] == area_code]
        df_area.index = pd.to_datetime(df_area["timestamp"], utc=True)
        df_area = df_area.sort_index()
        df_area.index = pd.DatetimeIndex(df_area.index).tz_convert("Europe/Zurich")
        df_area = df_area.resample("1h").sum()
        df_area["power_kw"] = df_area["value_kwh"] / df_area["num_meter"]

        # print("Number of rows: ", len(df_area))
        # print(f"Max power_kw: {df_area["power_kw"].max():.2f} kW")
        # print(f"Min power_kw: {df_area["power_kw"].min():.2f} kW")

        plt.plot(df_area["power_kw"].iloc[: 24 * 2], label=area_code)

    plt.xlabel("Time")
    plt.ylabel("power_kw")
    # plt.legend()
    plt.grid()
    plt.show()

    # Group and sort by timestamp and sum up all value_kwh and num_meter
    df_month = df_month.groupby("timestamp").sum()

    # Convert timestamp index to datetime and drop column area_code
    df_month.index = pd.to_datetime(df_month.index, utc=True)
    df_month = df_month.sort_index()

    # Resample to 1h
    df_month = df_month.resample("1h").sum()

    # power_kw = value_kwh / num_meter
    df_month["power_kw"] = df_month["value_kwh"] / df_month["num_meter"]

    # Drop columns value_kwh, num_meter and area_code
    df_month = df_month.drop(columns=["value_kwh", "num_meter", "area_code"])

    # Append to df_year
    df_year = pd.concat([df_year, df_month])

    # Delete df_month
    del df_month

# Set timestamp from UTC to Europe/Zurich
df_year.index = pd.DatetimeIndex(df_year.index).tz_convert("Europe/Zurich")


# Scale profile to 3000kWh annual consumption
annual_consumption = df_year["power_kw"].sum()
df_year["power_kw"] = df_year["power_kw"] / annual_consumption * 3000

# print(df_year.head())
# print("Number of rows: ", len(df_year))

# print(f"Max power_kw: {df_year["power_kw"].max():.2f} kW")
# print(f"Min power_kw: {df_year["power_kw"].min():.2f} kW")
# print(f"Annual consumption: {df_year["power_kw"].sum():.2f} kWh")

# # Print min and max timestamp
# print("Min timestamp: ", df_year.index.min())
# print("Max timestamp: ", df_year.index.max())

# Plot power_kw
# rand_int = random.randint(0, 360)
# plt.figure(figsize=(30, 5))
# plt.plot(df_year["power_kw"].iloc[24 * rand_int:24 * (rand_int + 1)])
# plt.xlabel("Time")
# plt.ylabel("Power [kW]")
# plt.grid()
# plt.show()

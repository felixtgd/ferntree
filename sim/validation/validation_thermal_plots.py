import os

import pandas as pd
import matplotlib.pyplot as plt


# Read csv file with thermal energy demand
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "results/thermal_energy_demand.csv")
df = pd.read_csv(file_path)


# Plot bar charts with box plots of average annual thermal energy demand
def plot_bar_charts(df):
    df_mean = df.groupby("type_code").mean()
    # Three subplots next to each other in one row
    fig, ax = plt.subplots(figsize=(15, 5))
    fig.suptitle("Average annual thermal energy demand by building type")

    # First subplot for building types ending with 1
    ax.bar(df_mean.index, df_mean["E_th"])

    # Color bars of building types ending with 1 in red
    for i in range(len(df_mean.index)):
        if df_mean.index[i].endswith("1"):
            ax.patches[i].set_facecolor("tab:blue")
        elif df_mean.index[i].endswith("2"):
            ax.patches[i].set_facecolor("tab:orange")
        else:
            ax.patches[i].set_facecolor("tab:green")

    # Add box plot to each bar
    positions = range(len(df_mean.index))
    ax.boxplot(
        [df[df["type_code"] == type_code]["E_th"] for type_code in df_mean.index],
        positions=positions,
        showfliers=False,
    )
    ax.set_ylabel("Annual thermal energy demand [MWh]")
    ax.grid()
    # Set x-axis labels to building type codes
    ax.set_xticks(positions)
    ax.set_xticklabels(df_mean.index)

    # Save plot as png
    fig.savefig(os.path.join(script_dir, "results/annual_thermal_energy_demand.png"))


plot_bar_charts(df)

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
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Average annual thermal energy demand by building type')

    # First subplot for building types ending with 1
    df_mean_1 = df_mean[df_mean.index.str.endswith('1')]
    axs[0].bar(df_mean_1.index, df_mean_1["E_th"])
    # Add box plot to each bar
    positions = range(len(df_mean_1.index))
    axs[0].boxplot([df[df["type_code"] == type_code]["E_th"] for type_code in df_mean_1.index], positions=positions, showfliers=False)
    axs[0].set_ylabel('Annual thermal energy demand [MWh]')
    axs[0].set_title('Var1')
    axs[0].grid()
    # Set x-axis labels to building type codes
    axs[0].set_xticks(positions)
    axs[0].set_xticklabels(df_mean_1.index)

    # Second subplot for building types ending with 2
    df_mean_2 = df_mean[df_mean.index.str.endswith('2')]
    axs[1].bar(df_mean_2.index, df_mean_2["E_th"])
    # Add box plot to each bar
    axs[1].boxplot([df[df["type_code"] == type_code]["E_th"] for type_code in df_mean_2.index], positions=positions, showfliers=False)
    axs[1].set_title('Var2')
    axs[1].grid()

    # Third subplot for building types ending with 3
    df_mean_3 = df_mean[df_mean.index.str.endswith('3')]
    axs[2].bar(df_mean_3.index, df_mean_3["E_th"])
    # Add box plot to each bar
    axs[2].boxplot([df[df["type_code"] == type_code]["E_th"] for type_code in df_mean_3.index], positions=positions, showfliers=False)
    axs[2].set_title('Var3')
    axs[2].grid()

    # Save plot as png
    fig.savefig(os.path.join(script_dir, 'results/annual_thermal_energy_demand.png'))


# plot_bar_charts(df)

# Define same eplot as above but with all bars in one figure
def plot_bar_chart(df):
    df_mean = df.groupby("type_code").mean()
    # Create bar chart
    fig, ax = plt.subplots()
    fig.suptitle('Average annual thermal energy demand by building type')
    ax.bar(df_mean.index, df_mean["E_th"])
    # Add box plot to each bar
    positions = range(len(df_mean.index))
    ax.boxplot([df[df["type_code"] == type_code]["E_th"] for type_code in df_mean.index], positions=positions, showfliers=False)
    ax.set_ylabel('Annual thermal energy demand [MWh]')
    ax.set_xlabel('Building type code')
    ax.grid()
    # Set x-axis labels to building type codes
    ax.set_xticks(positions)
    ax.set_xticklabels(df_mean.index)
    # Save plot as png
    fig.savefig(os.path.join(script_dir, 'results/annual_thermal_energy_demand.png'))

# plot_bar_chart(df)
    

    # Plot bar charts with box plots of average annual thermal energy demand
def plot_bar_charts_a1(df):
    df_mean = df.groupby("type_code").mean()
    # Three subplots next to each other in one row
    fig, ax = plt.subplots(figsize=(15, 5))
    fig.suptitle('Average annual thermal energy demand by building type')

    # First subplot for building types ending with 1
    ax.bar(df_mean.index, df_mean["E_th"])

    # Color bars of building types ending with 1 in red
    for i in range(len(df_mean.index)):
        if df_mean.index[i].endswith('1'):
            ax.patches[i].set_facecolor('b')
        elif df_mean.index[i].endswith('2'):
            ax.patches[i].set_facecolor('o')
        else:
            ax.patches[i].set_facecolor('g')


    # Add box plot to each bar
    positions = range(len(df_mean.index))
    ax.boxplot([df[df["type_code"] == type_code]["E_th"] for type_code in df_mean.index], positions=positions, showfliers=False)
    ax.set_ylabel('Annual thermal energy demand [MWh]')
    ax.grid()
    # Set x-axis labels to building type codes
    ax.set_xticks(positions)
    ax.set_xticklabels(df_mean.index)

    # Save plot as png
    fig.savefig(os.path.join(script_dir, 'results/annual_thermal_energy_demand_a1.png'))

plot_bar_charts_a1(df)
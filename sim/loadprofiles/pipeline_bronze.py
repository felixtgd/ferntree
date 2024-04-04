import os
import h5py

import pandas as pd


def ingest_datasets(data_dir, verbose=False):
    print("\nBRONZE: Ingesting datasets")
    # Directory of raw datasets (bronze)
    bronze_dir = os.path.join(data_dir, "bronze")
    if not os.path.exists(bronze_dir):
        raise FileNotFoundError(f"Bronze directory '{bronze_dir}' does not exist!")

    # Years for which data is available
    years = ["2018", "2019", "2020"]

    # Define column names present in data
    cols = [
        "time",
        "S_1",
        "S_2",
        "S_3",
        "S_TOT",
        "P_1",
        "P_2",
        "P_3",
        "P_TOT",
        "P_TOT_WITH_PV",
        "Q_1",
        "Q_2",
        "Q_3",
        "Q_TOT",
        "U_1",
        "U_2",
        "U_3",
        "I_1",
        "I_2",
        "I_3",
        "PF_1",
        "PF_2",
        "PF_3",
    ]

    # Get data from all datasets and store in dataframe
    df = pd.DataFrame()
    for year in years:
        # Load the dataset for the current year
        data_file = f"{year}_data_60min.hdf5"
        if not os.path.isfile(os.path.join(bronze_dir, data_file)):
            raise FileNotFoundError(f"Dataset '{data_file}' does not exist!")

        print(f"Processing data from {data_file}")
        with h5py.File(os.path.join(bronze_dir, data_file), "r") as f:
            # Choose only houses without pv system
            data = f["NO_PV"]

            # Create dataframe for current year
            df_year = pd.DataFrame()

            # Iterate over all houses in the dataset
            for house in data.keys():
                # Get measurements from household meter
                data_sfh = data[house]["HOUSEHOLD"]["table"]

                # Convert list of tuples into list of lists
                data_sfh = [list(row) for row in data_sfh]

                # Create dataframe from list of lists
                df_tmp = pd.DataFrame(data_sfh, columns=cols)

                # Only care about time and S_TOT --> P_TOT are shit values!!!
                # USE S_TOT, values make more sense and actually resemble profiles in paper
                if False:
                    df_tmp = df_tmp[["time", "P_TOT"]]
                    # Rename P_TOT to P_{house}
                    df_tmp.rename(columns={"P_TOT": f"P_{house}"}, inplace=True)
                else:
                    df_tmp = df_tmp[["time", "S_TOT"]]
                    # # Multiply "S_TOT" with mean of "PF_1", "PF_2", "PF_3"
                    # df_tmp["S_TOT"] = df_tmp["S_TOT"] * df_tmp[["PF_1", "PF_2", "PF_3"]].mean(axis=1)
                    # # Drop columns "PF_1", "PF_2", "PF_3"
                    # df_tmp = df_tmp.drop(["PF_1", "PF_2", "PF_3"], axis=1)
                    # Rename P_TOT to P_{house}
                    df_tmp.rename(columns={"S_TOT": f"P_{house}"}, inplace=True)

                # If df_year is empty, set it to df_tmp, else merge the two dataframes
                if df_year.empty:
                    df_year = df_tmp
                else:
                    df_year = pd.merge(df_year, df_tmp, on="time", how="outer")

                if verbose:
                    # Percentage of missing P_TOT values
                    availability = (
                        1 - df_tmp[f"P_{house}"].isna().sum() / len(df_tmp)
                    ) * 100
                    print(f"{year} {house}: {availability:.2f}% data availability")

            # Append df_year to df
            df = pd.concat([df, df_year])

    # Silver directory for dataset
    silver_dir = os.path.join(data_dir, "silver")
    # Create dir if not exist
    if not os.path.exists(silver_dir):
        os.makedirs(silver_dir)

    # Save silver dataset containing preprocessed loadprofiles to csv
    output_file = os.path.join(silver_dir, "loadprofiles_sorted.csv")
    df.to_csv(output_file, index=False)
    print("Silver dataset saved to silver/loadprofiles_sorted.csv")
    print(f"Timesteps: {len(df)}, Houses: {len(df.columns)}")

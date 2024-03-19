import os
import h5py

import pandas as pd


def preprocess_loadprofiles():
    # Directory of datasets
    data_dir = "/Users/felixtangerding/Documents/Ferntree/Datasets/38_Germany"

    # Years for which data is available
    years = ["2018", "2019", "2020"]
    # years = ["2019"]


    # Define column names present in data
    cols = [
        "time",
        "S_1", "S_2", "S_3", "S_TOT",
        "P_1", "P_2", "P_3", "P_TOT", "P_TOT_WITH_PV",
        "Q_1", "Q_2", "Q_3", "Q_TOT",
        "U_1", "U_2", "U_3",
        "I_1", "I_2", "I_3",
        "PF_1", "PF_2", "PF_3",
        ]

    # Create dataframe with column "time" with hourly data for year 2023
    # df = pd.DataFrame(pd.date_range(start="2023-01-01", periods=8760, freq="H"), columns=["time"])
    df = pd.DataFrame()

    # Get data from all datasets and store in dataframe
    for year in years:

        # Load the dataset for the current year
        # data_file = f"{year}_data_60min.hdf5"
        data_file = f"{year}_data_60min.hdf5"
        print(f"Proprocessing data from {data_file}")
        with h5py.File(os.path.join(data_dir, data_file), "r") as f:
            # Choose only houses without pv system
            data = f["NO_PV"]

            # Create dataframe for current year
            df_year = pd.DataFrame()

            # Iterate over all houses in the dataset
            for house in data.keys(): #["SFH3", "SFH4", "SFH5"]:
                # Get measurements from household meter
                data_sfh = data[house]["HOUSEHOLD"]["table"]
                
                # Convert list of tuples into list of lists
                data_sfh = [list(row) for row in data_sfh]

                # Create dataframe from list of lists
                df_tmp = pd.DataFrame(data_sfh, columns=cols)

                # Only care about time and P_TOT --> P_TOT are shit values!!! 
                # USE S_TOT, values make more sense and actually resemble profiles in paper
                if False:
                    df_tmp = df_tmp[["time", "P_TOT"]]
                    # Rename P_TOT to P_{house}
                    df_tmp.rename(columns={"P_TOT": f"P_{house}"}, inplace=True)
                else:
                    df_tmp = df_tmp[["time", "S_TOT"]]
                    # Rename P_TOT to P_{house}
                    df_tmp.rename(columns={"S_TOT": f"P_{house}"}, inplace=True)

                # If df_year is empty, set it to df_tmp, else merge the two dataframes
                if df_year.empty:
                    df_year = df_tmp
                else:
                    df_year = pd.merge(df_year, df_tmp, on="time", how="outer")

                # Percentage of missing P_TOT values
                availability = (1 - df_tmp[f"P_{house}"].isna().sum() / len(df_tmp)) * 100
                print(f"{year} {house}: {availability:.2f}% data availability")

            # Append df_year to df
            df = pd.concat([df, df_year])

    # Save dataframe to csv
    df.to_csv("data_loadprofiles/loadprofiles_raw.csv", index=False)
    print(f"Dataframe ({df.shape}) saved to 'loadprofiles_raw.csv'")

# preprocess_loadprofiles()
    


# # Directory of datasets
# data_dir = "/Users/felixtangerding/Documents/Ferntree/Datasets/38_Germany"

# # Years for which data is available
# year = "2019"
# # years = ["2018"]


# # Define column names present in data
# cols = [
#     "time",
#     "S_1", "S_2", "S_3", "S_TOT",
#     "P_1", "P_2", "P_3", "P_TOT", "P_TOT_WITH_PV",
#     "Q_1", "Q_2", "Q_3", "Q_TOT",
#     "U_1", "U_2", "U_3",
#     "I_1", "I_2", "I_3",
#     "PF_1", "PF_2", "PF_3",
#     ]

# # Create dataframe with column "time" with hourly data for year 2023
# # df = pd.DataFrame(pd.date_range(start="2023-01-01", periods=8760, freq="H"), columns=["time"])
# df = pd.DataFrame()

# # Load the dataset for the current year
# data_file = f"{year}_data_60min.hdf5"
# print(f"Proprocessing data from {data_file}")
# with h5py.File(os.path.join(data_dir, data_file), "r") as f:
#     # Choose only houses without pv system
#     data = f["NO_PV"]

#     # Create dataframe for current year
#     df_year = pd.DataFrame()

#     # Iterate over all houses in the dataset
#     houses = data.keys()
#     house = "SFH3"
#     # Get measurements from household meter
#     data_sfh = data[house]["HOUSEHOLD"]["table"]
    
#     # Convert list of tuples into list of lists
#     data_sfh = [list(row) for row in data_sfh]

#     # Create dataframe from list of lists
#     df_tmp = pd.DataFrame(data_sfh, columns=cols)

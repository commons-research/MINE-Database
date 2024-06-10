# Variables to set
folder_path = './data/output/metacyc_generalized/20240601_lotus_generalized_n45/results/'
pattern="result_*.tsv"

# import libraries
import polars as pl     #for dataframe managemante and calculation
import glob
import os

def read_multiple_csv(folder_path, pattern="*.csv"):
    # Get a list of all CSV files in the folder
    files = glob.glob(os.path.join(folder_path, pattern))

    # print(len(files))
    # files = files[:2]
    # print(len(files))
    
    # Read all CSV files into DataFrames and concatenate them
    combined_df = (
        pl.concat([pl.scan_csv(file) for file in files])
        .unique()
        .collect()
    )

    return combined_df


combined_df = read_multiple_csv(folder_path, pattern)

# Print the combined DataFrame
combined_df.write_parquet(folder_path + "results_all.parquet")


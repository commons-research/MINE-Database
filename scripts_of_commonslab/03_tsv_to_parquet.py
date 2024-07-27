import polars as pl
import sys
import os

def convert_tsv_to_parquet(tsv_file):
    # Check if the file exists
    if not os.path.isfile(tsv_file):
        print(f"Error: File {tsv_file} does not exist.")
        return

    # Define the output file name
    parquet_file = os.path.splitext(tsv_file)[0] + ".parquet"

    # Check if the Parquet file already exists
    if os.path.isfile(parquet_file):
        print(f"Error: File {parquet_file} already exists.")
        print("Please rename or delete the existing Parquet file and run the script again.")
        return

    # Read the TSV file lazily
    try:
        lazy_frame = pl.scan_csv(tsv_file, separator='\t')
    except Exception as e:
        print(f"Error reading {tsv_file}: {e}")
        return

    # Write the LazyFrame to a Parquet file
    try:
        lazy_frame.sink_parquet(parquet_file)
        print(f"Successfully converted {tsv_file} to {parquet_file}")
    except Exception as e:
        print(f"Error writing {parquet_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 03_tsv_to_parquet.py <input_file.tsv>")
    else:
        input_file = sys.argv[-1]
        convert_tsv_to_parquet(input_file)
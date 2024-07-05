import polars as pl


# set parameters for polars print
pl.Config.set_tbl_rows(100)
pl.Config(fmt_str_lengths=550)



def unique_filter(lazy_df, colname = "", show_df = True):
    """unique values

    Filters out the unique values of specific columns and prints the size and dataframe (if wished).

    Args:
        lazy_df(str):   dataframe to be manipulated
        colname(str, list of str):  columnnames, where the operations takes place. 
                                    If empty, it will go through each one by one.
                                    If args given, he will take all at ones in account.
        show_df(bool):  If true, also a part of the dataframe will be printed.

    Returns:
        bool: 0 if succeeded.

    """
    if not colname:
        for col_name in lazy_df.columns:
            num_uni = lazy_df.select(pl.col(col_name)).unique().collect(streaming = True)
            if show_df:
                print(f'----{col_name}----\n {num_uni}\n \n')
            else:
                print(f'{col_name} : {num_uni.shape}')
    else: 
        num_uni = lazy_df.select(pl.col(colname)).unique().collect(streaming = True)
        
        if show_df:
            print(f'----{colname}----\n {num_uni}\n \n')
        else:
            print(f'{colname} : {num_uni.shape}')
    return 0


def lazyread_mines_parquet(parquet_file):
    """
    Try to read in a parquet file with the filename included "compounds" or "reactions".

    Args:
        parquet_file: path to parquet file.

    Returns:
        returns the lazyframe for polars

    Improvments:
        - if path is longer, it should only check for the filnema if compounds or reaction...
    """
    if "compounds" in parquet_file:
        print(f'Compound file - filter for predicted compounds')
        lazy_df = (
            pl.scan_parquet(path)
            .filter(pl.col("Type") == "Predicted")   
            )
    elif "reactions" in parquet_file:
        print(f'Reaction file')
        lazy_df = (
            pl.scan_parquet(path)
            )
    else:
        print(f'other file')
        lazy_df = (
            pl.scan_parquet(path)
            )
    return lazy_df


# path = "/home/pamrein/2024_masterthesis/MINE-Database/data/output/metacyc_generalized/20240601_lotus_generalized_n45/compounds_1_generalized_230106_frozen_metadata_for_MINES_split_*.parquet"
# df = lazyread_mines_parquet(path) 
# # compounds columns: ["ID", "Type", "Generation", "Formula", "InChIKey", "SMILES"]
# unique_filter(df, colname = ["ID", "Type", "Generation", "Formula", "InChIKey", "SMILES"], show_df = False)
# unique_filter(df, colname = ["InChIKey", "SMILES"], show_df = False)


path = "/home/pamrein/2024_masterthesis/MINE-Database/data/output/metacyc_generalized/20240601_lotus_generalized_n45/reactions_1_generalized_230106_frozen_metadata_for_MINES_split_*.parquet"
df = lazyread_mines_parquet(path) 
# reactions columns: ["ID", "Name", "ID equation", "SMILES equation", "Rxn hash", "Reaction rules"]
unique_filter(df, colname = ["ID", "Name", "ID equation", "SMILES equation", "Rxn hash", "Reaction rules"],  show_df = False)
unique_filter(df, colname = ["ID equation", "SMILES equation", "Rxn hash", "Reaction rules"],  show_df = False)

# path = "/home/pamrein/2024_masterthesis/MINE-Database/data/output/metacyc_generalized/20240601_lotus_generalized_n45/results/*.parquet"
# df = lazyread_mines_parquet(path) 
# # reactions columns: ["ID", "Name", "ID equation", "SMILES equation", "Rxn hash", "Reaction rules"]
# unique_filter(df, show_df = False)

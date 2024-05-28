import polars as pl  # for data manipulation
import numpy as np  # specialy for NaN
import sys  # for command line arguments
import getopt  # for checking command line arguments
import datetime  # for naming the output file

# for interactive mode
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator



# check input args
def read_arg(argv):
    arg_help = f'''
    Please give the arguments as following:
        {argv[0]} -s <start_components> -r <reactions> -c <compounds> -o <output_file> -a <reaction_rules_col> -b <compounds_col>
    
    for example:
        poetry run python scripts_of_commonslab/add_compounds_and_rules_to_dataframe.py -s "../MINE-Database/example_data/20240522_Solanum_1000.csv" -r "../MINE-Database/data/output/metacyc_generalized/20240522_1000_Solanum/reactions_1_generalized20240522_Solanum_1000.csv_4843.94_.tsv" -c "../MINE-Database/data/output/metacyc_generalized/20240522_1000_Solanum/compounds_1_generalized20240522_Solanum_1000.csv_4843.94_.tsv" -o "results.csv" -a "Reaction rules" -b "SMILES"
    '''

    try:
        opts, args = getopt.getopt(argv[1:], 
            "h:s:r:c:o:a:b:", 
            [
                "help",
                "start_components=",
                "reactions=",
                "compounds=",
                "output_file=",
                "reaction_rules_col=",
                "compounds_col=",
            ],
        )
    except getopt.GetoptError as err:
        # print help information and exit:
        print(arg_help)  
        sys.exit(2)

    df_start_components_path = ""
    df_reactions_path = ""
    df_compounds_path = ""
    output_file = ""
    reaction_rules_col = ""
    compounds_col = ""

    # If argument values given, overwrite the default values
    for o, a in opts:
        if o in ("-h", "--help"):
            print(arg_help)
            sys.exit()
        elif o in ("-s", "--start_components"):
            df_start_components_path = a
        elif o in ("-r", "--reactions"):
            df_reactions_path = a
        elif o in ("-c", "--compounds"):
            df_compounds_path = a
        elif o in ("-o", "--output_file"):
            output_file = a
        elif o in ("-a", "--reaction_rules_col"):
            reaction_rules_col = a
        elif o in ("-b", "--compounds_col"):
            compounds_col = a
        else:
            assert False, "unhandled option"
        
    return {
            "df_start_components_path" : df_start_components_path, 
            "df_reactions_path" : df_reactions_path, 
            "df_compounds_path" : df_compounds_path, 
            "output_file" : output_file,
            "reaction_col" : reaction_rules_col, 
            "compounds_col" : compounds_col
            }




if __name__ == "__main__":

    # if arguments in the CLI are given, they will be loaded
    if sys.argv[1:]:
        input_args = read_arg(sys.argv)

    # if no arguments given, this variables will be taken (to modify)
    else:
        input_args = {
            "df_start_components_path" : "../MINE-Database/example_data/20240522_Solanum_1000.csv", 
            "df_reactions_path" : "../MINE-Database/data/output/metacyc_generalized/20240522_1000_Solanum/reactions_1_generalized20240522_Solanum_1000.csv_4843.94_.tsv", 
            "df_compounds_path" : "../MINE-Database/data/output/metacyc_generalized/20240522_1000_Solanum/compounds_1_generalized20240522_Solanum_1000.csv_4843.94_.tsv", 
            "output_file" : "results.csv",
            "reaction_col" : "Reaction rules", 
            "compounds_col" : "SMILES", 
            }

    # load the pickaxe reactions and pickaxe compounds and the given startcompounds
    df_start_components = pl.read_csv(input_args["df_start_components_path"], separator=",")
    df_reactions = pl.read_csv(input_args["df_reactions_path"], separator="\t", truncate_ragged_lines=True)
    df_compounds = pl.read_csv(input_args["df_compounds_path"], separator="\t", truncate_ragged_lines=True)


    # # print the possible col names
    # print(f"reactions: {df_reactions.columns}")
    # print(f"compounds: {df_compounds.columns}")


    # specify which columns should be extracted
    reaction_col = input_args["reaction_col"]
    compounds_col = input_args["compounds_col"]


    ## extract the ID (should be used the wikidata_structure of LOTUS - should be the same as in the startcompounds)
    # split the "ID equation" to reactants and products
    df_reactions = df_reactions.with_columns(
        ID_equation_separated = pl.col("ID equation").str.split(by=">>")).with_columns(
            pl.col("ID_equation_separated").list.slice(0,1).cast(pl.List(pl.Utf8)).list.join("").alias("reactant"),
            pl.col("ID_equation_separated").list.slice(1,2).cast(pl.List(pl.Utf8)).list.join("").alias("product"),
    )

    # search with regex for the wikidatalink and the pkc numbers. 
    # in general we should find one wikidata link in the reactants and sometimes multiple pkc and wikidatalinks in the product
    df_reactions = df_reactions.with_columns(
        pl.col("reactant").str.extract(r"http://www.wikidata.org/entity/Q(\d+)", 0).alias("reactant_2"),
        pl.col("product").str.extract_all(r"pkc(\d+)|http://www.wikidata.org/entity/Q(\d+)").alias("product_2"),
    )


    # filter for the predicted compounds
    df_compounds_predicted = df_compounds.filter(pl.col("Type") == "Predicted")

    # change the columns name for the join function
    df_compounds_predicted = df_compounds_predicted.rename({"ID": "product_2"})
    df_compounds_predicted = df_compounds_predicted.drop(["Type", "Generation"])


    df_compounds_to_join = df_compounds_predicted.select(["product_2", compounds_col])

    df_reactions_and_compounds = df_reactions.explode("product_2").join(df_compounds_to_join, on="product_2", how="left")

    # make a new dataframe with the ID (wikidata_structure), the rule and the predicted compound
    df_reactions_and_compounds = df_reactions_and_compounds[["reactant_2", reaction_col, compounds_col]]
    df_reactions_and_compounds = df_reactions_and_compounds.rename({"reactant_2" : "ID", compounds_col: str("predicted_" + compounds_col) })

    print(df_reactions_and_compounds)
    

    df_reactions_and_compounds.write_csv(input_args["output_file"])
    print(f'file is saved: {input_args["output_file"]}')
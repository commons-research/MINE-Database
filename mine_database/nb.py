import pandas as pd
from downloaders import BaseDownloader

downloader = BaseDownloader()

npc_dataset_url = "https://zenodo.org/record/13880847/files/NPClassifier_dataset.tsv"
npc_dataset_path = "data/NPClassifier_dataset.tsv"

downloader.download(
    npc_dataset_url,
    npc_dataset_path,
)

# Load the NPC dataframe

df = pd.read_csv(npc_dataset_path, sep="\t")

# We rename the 'index' column to SMILES

df = df.rename(columns={"index": "smiles"})

# Generate an index for each SMILES string
# For this we use "npc_" as a prefix and the row index as the suffix

df["id"] = "npc_" + df.index.astype(str)

# We now keep only the 'index' and 'SMILES' columns

df = df[["id", "smiles"]]

# Save the NPC dataframe as a csv file called 'npc_dataset.tsv'

df.to_csv("data/npc_dataset.csv", index=False)


## We can then run the following command to generate the rules for the NPC dataset

# python mine_database/pickaxe_commons.py --coreactant_list ./mine_database/data/original_rules/EnzymaticCoreactants.tsv --rule_list ./mine_database/data/original_rules/EnzymaticReactionRules.tsv --generations 1 --compound_file ./data/npc_dataset.csv --output_dir ./data/output/npc --processes 60 --verbose --explicit_h --database npc_mines


### Here we try to visualize the SMARTS

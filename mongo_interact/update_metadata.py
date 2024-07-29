import pandas as pd
from pymongo import MongoClient
import gzip

# Replace with your MongoDB connection string
connection_string = "mongodb://localhost:27017/"

# Load the metadata from a .gz compressed CSV file
metadata_file_path = './example_data/230106_frozen_metadata.csv.gz'

# Function to read a gzip compressed CSV file into a DataFrame
def read_gz_csv(file_path):
    with gzip.open(file_path, 'rt') as f:
        df = pd.read_csv(f)
    return df

metadata_df = read_gz_csv(metadata_file_path)

# Connect to MongoDB
client = MongoClient(connection_string)
db = client['test-mines']  # Replace with your actual database name
compounds_col = db['compounds']

# Step 1: List all Starting Compounds' InChIKeys
starting_compounds_inchikeys = compounds_col.find({"Type": "Starting Compound"}, {"InChI_key": 1, "_id": 0})
starting_compounds_inchikeys = [doc['InChI_key'] for doc in starting_compounds_inchikeys]

# Step 2: Subset the metadata DataFrame for these InChIKeys
metadata_subset_df = metadata_df[metadata_df['structure_inchikey'].isin(starting_compounds_inchikeys)]

# Step 3: Iterate over the rows of the subset DataFrame and update MongoDB documents
for index, row in metadata_subset_df.iterrows():
    inchi_key = row['structure_inchikey']
    
    # Create a dictionary of the metadata
    metadata = {
        "structure_wikidata": row['structure_wikidata'],
        "structure_inchi": row['structure_inchi'],
        "structure_smiles": row['structure_smiles'],
        "structure_molecular_formula": row['structure_molecular_formula'],
        "structure_exact_mass": row['structure_exact_mass'],
        "structure_xlogp": row['structure_xlogp'],
        "structure_smiles_2D": row['structure_smiles_2D'],
        "structure_cid": row['structure_cid'],
        "structure_nameIupac": row['structure_nameIupac'],
        "structure_nameTraditional": row['structure_nameTraditional'],
        "structure_stereocenters_total": row['structure_stereocenters_total'],
        "structure_stereocenters_unspecified": row['structure_stereocenters_unspecified'],
        "structure_taxonomy_npclassifier_01pathway": row['structure_taxonomy_npclassifier_01pathway'],
        "structure_taxonomy_npclassifier_02superclass": row['structure_taxonomy_npclassifier_02superclass'],
        "structure_taxonomy_npclassifier_03class": row['structure_taxonomy_npclassifier_03class'],
        "structure_taxonomy_classyfire_chemontid": row['structure_taxonomy_classyfire_chemontid'],
        "structure_taxonomy_classyfire_01kingdom": row['structure_taxonomy_classyfire_01kingdom'],
        "structure_taxonomy_classyfire_02superclass": row['structure_taxonomy_classyfire_02superclass'],
        "structure_taxonomy_classyfire_03class": row['structure_taxonomy_classyfire_03class'],
        "structure_taxonomy_classyfire_04directparent": row['structure_taxonomy_classyfire_04directparent'],
        "organism_wikidata": row['organism_wikidata'],
        "organism_name": row['organism_name'],
        "organism_taxonomy_gbifid": row['organism_taxonomy_gbifid'],
        "organism_taxonomy_ncbiid": row['organism_taxonomy_ncbiid'],
        "organism_taxonomy_ottid": row['organism_taxonomy_ottid'],
        "organism_taxonomy_01domain": row['organism_taxonomy_01domain'],
        "organism_taxonomy_02kingdom": row['organism_taxonomy_02kingdom'],
        "organism_taxonomy_03phylum": row['organism_taxonomy_03phylum'],
        "organism_taxonomy_04class": row['organism_taxonomy_04class'],
        "organism_taxonomy_05order": row['organism_taxonomy_05order'],
        "organism_taxonomy_06family": row['organism_taxonomy_06family'],
        "organism_taxonomy_07tribe": row['organism_taxonomy_07tribe'],
        "organism_taxonomy_08genus": row['organism_taxonomy_08genus'],
        "organism_taxonomy_09species": row['organism_taxonomy_09species'],
        "organism_taxonomy_10varietas": row['organism_taxonomy_10varietas'],
        "reference_wikidata": row['reference_wikidata'],
        "reference_doi": row['reference_doi'],
        "manual_validation": row['manual_validation']
    }
    
    # Update the document in MongoDB
    compounds_col.update_one({'InChI_key': inchi_key}, {'$set': metadata}, upsert=False)

print("Metadata update completed.")

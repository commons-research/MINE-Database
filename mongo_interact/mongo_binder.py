from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(
    "mongodb://localhost:27017/"
)  # Update with your MongoDB connection string
db = client["lotus_mines"]  # Update with your database name

# Collections
compounds_col = db["compounds"]
meta_data_col = db["meta_data"]
operators_col = db["operators"]
product_of_col = db["product_of"]
reactant_in_col = db["reactant_in"]
reactions_col = db["reactions"]


# Function to get metadata for a compound
def get_compound_metadata(compound_id):
    compound_data = compounds_col.find_one({"_id": compound_id})
    if compound_data:
        meta_data = meta_data_col.find_one({"_id": compound_id})
        return {**compound_data, **meta_data} if meta_data else compound_data
    return None


# Fetch and process reactions
reactions = reactions_col.find()
results = []

for reaction in reactions[:5]:  # Limit to 5 reactions for demonstration
    reaction_data = {
        "Reaction ID": reaction["ID"],
        "SMILES Reaction": reaction["SMILES_rxn"],
        "Operators": reaction["Operators"],
        "Reactants": [],
        "Products": [],
    }

    for reactant in reaction["Reactants"]:
        reactant_metadata = get_compound_metadata(reactant[1])
        if reactant_metadata:
            reaction_data["Reactants"].append(reactant_metadata)

    for product in reaction["Products"]:
        product_metadata = get_compound_metadata(product[1])
        if product_metadata:
            reaction_data["Products"].append(product_metadata)

    results.append(reaction_data)

# Convert results to a DataFrame for better visualization (if needed)
import pandas as pd

results_df = pd.DataFrame(results)
results_df.head()

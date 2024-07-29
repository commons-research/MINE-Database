import argparse
from pymongo import MongoClient

taxonomy_rank = "organism_taxonomy_03phylum"
taxonomy_value = "Streptophyta"

def retrieve_predicted_inchikeys(connection_string, database_name, taxonomy_rank, taxonomy_value):
    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client[database_name]
    compounds_col = db['compounds']
    reactions_col = db['reactions']

    # Step 1: Retrieve all starting compounds with the specified taxonomy rank and value
    query = {"Type": "Starting Compound", taxonomy_rank: taxonomy_value}
    starting_compounds = compounds_col.find(query)

    # Debug: Count and list all starting compounds retrieved
    starting_compounds_list = list(starting_compounds)
    print(f"Found {len(starting_compounds_list)} starting compounds with {taxonomy_rank} = {taxonomy_value}")

    # Step 2: For each starting compound, retrieve all predicted InChIKeys
    results = []

    for starting_compound in starting_compounds_list:
        starting_inchikey = starting_compound['InChI_key']
        reactant_id = starting_compound['_id']

        # Debug: Print the starting compound details
        print(f"Processing starting compound: {starting_inchikey}, ID: {reactant_id}")

        # Find all reactions where this starting compound is a reactant
        reactions = reactions_col.find({"Reactants": {"$elemMatch": {"$elemMatch": {"$eq": reactant_id}}}})

        # Debug: Count and list all reactions retrieved for the starting compound
        reactions_list = list(reactions)
        print(f"Found {len(reactions_list)} reactions for starting compound {starting_inchikey}")

        for reaction in reactions_list:
            for product in reaction['Products']:
                product_id = product[1]
                product_compound = compounds_col.find_one({"_id": product_id, "Type": "Predicted"})

                if product_compound:
                    product_inchikey = product_compound['InChI_key']
                    results.append((starting_inchikey, product_inchikey))

    # Print the results
    if results:
        for pair in results:
            print(f"Starting InChIKey: {pair[0]} -> Predicted InChIKey: {pair[1]}")
    else:
        print("No predicted InChIKeys found for the specified starting compounds.")

    print("Data retrieval completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve predicted InChIKeys for starting compounds based on organism taxonomy rank.")
    parser.add_argument("--connection_string", required=True, help="MongoDB connection string")
    parser.add_argument("--database_name", required=True, help="Name of the MongoDB database")
    parser.add_argument("--taxonomy_rank", default="organism_taxonomy_05order", help="The taxonomy rank field to filter on (default: organism_taxonomy_05order)")
    parser.add_argument("--taxonomy_value", required=True, help="The value of the taxonomy rank to filter on")

    args = parser.parse_args()

    retrieve_predicted_inchikeys(args.connection_string, args.database_name, args.taxonomy_rank, args.taxonomy_value)
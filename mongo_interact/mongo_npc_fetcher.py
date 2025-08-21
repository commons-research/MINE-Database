from pymongo import MongoClient
from collections import defaultdict
import csv
import json
from tqdm import tqdm  # Import tqdm
import argparse


# Function to get metadata for a compound
def get_compound_metadata(compound_id):
    compound_data = compounds_col.find_one({"_id": compound_id})
    if compound_data:
        meta_data = meta_data_col.find_one({"_id": compound_id})
        return {**compound_data, **meta_data} if meta_data else compound_data
    return None


# Function to extract only the starting compound
def extract_starting_compound(compound_list):
    for reactant in compound_list:
        compound_metadata = get_compound_metadata(reactant[1])
        if compound_metadata and compound_metadata.get("Type") == "Starting Compound":
            return {
                "smiles": compound_metadata.get("SMILES", ""),
                "inchikey": compound_metadata.get("InChI_key", ""),
            }
    return None


# Function to extract product compound data with only 'Predicted' type
def extract_predicted_products(compound_list, reaction_operators):
    products = []
    for product in compound_list:
        compound_metadata = get_compound_metadata(product[1])
        if compound_metadata and compound_metadata.get("Type") == "Predicted":
            # Check if the operator is not in the blacklist
            if reaction_operators and reaction_operators[0] not in OPERATOR_BLACKLIST:
                products.append(
                    {
                        "smiles": compound_metadata.get("SMILES", ""),
                        "inchikey": compound_metadata.get("InChI_key", ""),
                        # 'operators': reaction_operators[0]  # Single operator
                    }
                )
    return products


def main(limit=None):
    # Connect to MongoDB
    client = MongoClient(
        "mongodb://localhost:27017/"
    )  # Update with your MongoDB connection string
    db = client["npc_mines"]  # Update with your database name

    # Collections
    global compounds_col, meta_data_col, reactions_col
    compounds_col = db["compounds"]
    meta_data_col = db["meta_data"]
    reactions_col = db["reactions"]

    # Define blacklist of operators
    global OPERATOR_BLACKLIST
    OPERATOR_BLACKLIST = [
        "1.13.1_03",
        "1.13.11_03",
        "1.4.3_01",
        "2.6.1_01",
        "3.1.1_02",
        "3.1.1_05",
        "3.1.4_01",
        "3.2.1_01",
        "3.5.1_02",
        "3.7.1_02",
        "3.8.1_03",
        "4.1.2_05",
        "4.2.3_02",
        "4.3.1_02.rev",
        "4.3.1_04.rev",
    ]  # Add your operators to this list

    # Group products by starting compound's InChIKey
    grouped_reactions = defaultdict(
        lambda: {"starting_compound": None, "product_compounds": []}
    )

    # Fetch total reactions count
    total_reactions = reactions_col.count_documents(
        {}
    )  # Count all documents in the reactions collection

    # Fetch reactions with an optional limit
    reactions = reactions_col.find().limit(limit) if limit else reactions_col.find()

    # Wrap the reactions with tqdm for progress tracking
    for reaction in tqdm(reactions, total=total_reactions, desc="Processing reactions"):
        # Extract starting compound
        starting_compound = extract_starting_compound(reaction["Reactants"])
        if starting_compound:
            inchikey = starting_compound["inchikey"]

            # Add the starting compound info (only once for each unique InChIKey)
            if not grouped_reactions[inchikey]["starting_compound"]:
                grouped_reactions[inchikey]["starting_compound"] = starting_compound

            # Extract predicted product compounds and add them to the list
            predicted_products = extract_predicted_products(
                reaction["Products"], reaction["Operators"]
            )
            grouped_reactions[inchikey]["product_compounds"].extend(predicted_products)

    # Convert the grouped reactions to a list and remove duplicates in product compounds
    results = []
    for inchikey, reaction_data in grouped_reactions.items():
        unique_products = {
            p["inchikey"]: p for p in reaction_data["product_compounds"]
        }.values()  # Remove duplicates by InChIKey
        reaction_data["product_compounds"] = list(unique_products)
        results.append(reaction_data)

    # Return results as JSON
    json_results = json.dumps(results, indent=4)

    # Optionally, save the JSON to a file
    with open(
        "./data/output/npc_expanded_grouped_starting_and_predicted_products.json", "w"
    ) as f:
        f.write(json_results)

    # Prepare data for CSV export
    csv_data = []
    for inchikey, reaction_data in grouped_reactions.items():
        starting_compound = reaction_data["starting_compound"]
        for product in reaction_data["product_compounds"]:
            csv_data.append(
                [
                    starting_compound["smiles"],
                    starting_compound["inchikey"],
                    product["smiles"],
                    product["inchikey"],
                    # product['operators']
                ]
            )

    # Write to CSV file
    csv_file = "./data/starting_compounds_and_predicted_products.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(
            [
                "Starting Compound SMILES",
                "Starting Compound InChIKey",
                "Product Compound SMILES",
                "Product Compound InChIKey",
            ]
        )

        # Write data
        writer.writerows(csv_data)

    print(f"CSV file '{csv_file}' has been created.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process MongoDB reactions.")
    parser.add_argument(
        "--limit", type=int, help="Limit the number of reactions to process."
    )
    args = parser.parse_args()

    main(limit=args.limit)  # Run the main function

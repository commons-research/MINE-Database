from pymongo import MongoClient
import pandas as pd

# Replace with your MongoDB connection string
connection_string = "mongodb://localhost:27017/"


def get_inchikey_and_type_by_id(compound_id, compounds_col):
    compound = compounds_col.find_one({"_id": compound_id})
    if compound:
        return compound.get("InChI_key"), compound.get("Type")
    return None, None


def retrieve_starting_predicted_pairs(connection_string, database_name):
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)

        # Select the database and collections
        db = client[database_name]
        compounds_col = db["compounds"]
        reactions_col = db["reactions"]

        # Fetch reactions
        reactions = reactions_col.find()
        results = []

        for reaction in reactions:
            reactant_inchikeys = []
            product_inchikeys = []

            # Get InChIKeys and Types for reactants
            for reactant in reaction["Reactants"]:
                inchikey, type_ = get_inchikey_and_type_by_id(
                    reactant[1], compounds_col
                )
                if inchikey and type_ == "Starting Compound":
                    reactant_inchikeys.append(inchikey)

            # Get InChIKeys and Types for products
            for product in reaction["Products"]:
                inchikey, type_ = get_inchikey_and_type_by_id(product[1], compounds_col)
                if inchikey and type_ == "Predicted":
                    product_inchikeys.append(inchikey)

            # Collect the starting-predicted pairs
            for reactant_inchikey in reactant_inchikeys:
                for product_inchikey in product_inchikeys:
                    results.append((reactant_inchikey, product_inchikey))

        # Convert results to DataFrame
        results_df = pd.DataFrame(
            results, columns=["Starting InChIKey", "Predicted InChIKey"]
        )

        # Save to CSV
        results_df.to_csv("starting_predicted_pairs.csv", index=False)

        print("Data retrieval and CSV export successful.")
    except Exception as e:
        print("Error retrieving data:", e)


# Specify your database name
database_name = "test-mines"

# Run the retrieval function
retrieve_starting_predicted_pairs(connection_string, database_name)

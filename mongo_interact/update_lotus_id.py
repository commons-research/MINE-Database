# To update the LOTUS database on mongodb with the id of the actual produced moledules
# used for "lotus_mines_enzymatic"


import polars as pl
from pymongo import MongoClient, UpdateOne

# Load the CSV file using Polars
file_path = (
    "/home/pamrein/MINE-Database/example_data/230106_frozen_metadata_cleaned.csv"
)
data = pl.read_csv(file_path)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["lotus_mines_enzymatic"]

# Fetch the compounds collection
compounds_collection = db["compounds"]

# Create or select the lotus collection
lotus_collection = db["lotus"]

# Convert the Polars DataFrame to a list of dictionaries
data_dicts = data.to_dicts()

# Prepare bulk operations
bulk_operations = []

print(f"connected to the server")

# Iterate over each row in the data dictionary
for row in data_dicts:
    structure_inchikey = row["structure_inchikey"]

    # Find the corresponding compound
    compound = compounds_collection.find_one({"ID": structure_inchikey})

    if compound:
        print(f"inchy added: {compound} \t| searched for: {structure_inchikey}")

        # Prepare the document to insert/update into the lotus collection
        document = row
        document["_id"] = compound["_id"]

        # Create an upsert operation (update if exists, insert if not)
        bulk_operations.append(
            UpdateOne({"_id": document["_id"]}, {"$set": document}, upsert=True)
        )

# Execute bulk operations
if bulk_operations:
    result = lotus_collection.bulk_write(bulk_operations)
    print(
        f"Inserted {result.upserted_count} documents and updated {result.modified_count} documents."
    )

print("All documents have been processed.")

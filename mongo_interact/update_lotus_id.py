# To update the LOTUS database on mongodb with the id of the actual produced moledules
# used for "lotus_mines_enzymatic"


import polars as pl
from pymongo import MongoClient

# Load the CSV file using Polars
file_path = '/mnt/data/230106_frozen_metadata_cleaned_short.csv'
data = pl.read_csv(file_path)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['lotus_mines_enzymatic']

# Fetch the compounds collection
compounds_collection = db['compounds']

# Create the lotus collection
lotus_collection = db['lotus']

# Convert the Polars DataFrame to a list of dictionaries
data_dicts = data.to_dicts()

# Iterate over each row in the data dictionary
for row in data_dicts:
    structure_inchikey = row['structure_inchikey']

    # Find the corresponding compound
    compound = compounds_collection.find_one({'ID': structure_inchikey})

    if compound:
        # Prepare the document to insert into the lotus collection
        document = row
        document['_id'] = compound['_id']

        # Insert the document into the lotus collection
        lotus_collection.insert_one(document)
        print(f"Inserted document with _id: {compound['_id']}")

print("All documents have been inserted.")


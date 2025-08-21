from pymongo import MongoClient

# Replace with your MongoDB connection string
connection_string = "mongodb://localhost:27017/"


def test_mongodb_connection(connection_string):
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)

        # List databases
        databases = client.list_database_names()
        print("Databases:", databases)

        # Select a database (replace 'your_database_name' with your actual database name)
        db = client["test-mines"]

        # List collections in the database
        collections = db.list_collection_names()
        print("Collections in database:", collections)

        # Select a collection (replace 'your_collection_name' with your actual collection name)
        collection = db["test-mines"]

        # Fetch and print some documents from the collection
        documents = collection.find().limit(5)
        for doc in documents:
            print(doc)

        print("MongoDB connection and data retrieval successful.")
    except Exception as e:
        print("Error connecting to MongoDB:", e)


# Run the test function
test_mongodb_connection(connection_string)

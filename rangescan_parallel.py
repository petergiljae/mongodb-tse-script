from pymongo import MongoClient
from bson import ObjectId
import concurrent.futures
import argparse

def find_first_id(collection):
    result = collection.find_one({}, sort=[('_id', 1)])
    if result:
        return result['_id']
    else:
        return None

def get_id_ranges(total_documents, batch_size, collection):
    id_ranges = []
    num_batches = total_documents // batch_size
    remainder = total_documents % batch_size

    start_id = find_first_id(collection)
    for _ in range(num_batches):
        cursor = collection.find({"_id": {"$gte": start_id}},{"_id:":1})
        cursor.batch_size(batch_size)
        for index, document in enumerate(cursor):
            if index == batch_size:
                end_id = document["_id"]
                id_ranges.append((start_id, end_id))
                start_id = end_id
                break

    if remainder > 0:
        end_id = ObjectId('ffffffffffffffffffffffff')
        id_ranges.append((start_id, end_id))

    return id_ranges

def process_documents(documents):
    for document in documents:
        # Process each document here
        print(document)

def query_documents(collection, start_id, end_id):
    query = {"_id": {"$gte": start_id, "$lt": end_id}}
    print(query)
    cursor = collection.find(query)
    documents = [doc for doc in cursor]
    process_documents(documents)

def main(database_name, collection_name, batch_size):
    # MongoDB connection details
    client = MongoClient("mongodb://localhost:27017,localhost:27018,localhost:27018/?replicaSet=replset")
    db = client[database_name]
    collection = db[collection_name]

    # Get the total number of documents in the collection
    total_documents = collection.count_documents({})
    print(total_documents)

    # Determine the batch size and ID ranges
    id_ranges = get_id_ranges(total_documents, batch_size, collection)

    # Create a thread pool executor for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit queries for each ID range in parallel
        futures = []
        for start_id, end_id in id_ranges:
            future = executor.submit(query_documents, collection, start_id, end_id)
            futures.append(future)

        # Wait for all queries to complete
        concurrent.futures.as_completed(futures)

    # Close the MongoDB connection
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel MongoDB Document Processing")
    parser.add_argument("database_name", help="Name of the MongoDB database")
    parser.add_argument("collection_name", help="Name of the MongoDB collection")
    parser.add_argument("batch_size", type=int, help="Batch size for parallel processing")

    args = parser.parse_args()
    main(args.database_name, args.collection_name, args.batch_size)

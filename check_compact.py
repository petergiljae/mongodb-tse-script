from pymongo import MongoClient

# Replace this with your actual MongoDB connection string
connection_string = "mongodb://localhost:27017"
database_name = "admin"

try:
    client = MongoClient(connection_string)
    database = client[database_name]

    # Start the compact operation here
    # For example, to compact a collection called "your_collection_name":
    # database.command('compact', 'your_collection_name')

    # Check the currentOp output to monitor the compact operation
    current_op_result = database.command('currentOp')
    in_progress_ops = current_op_result.get('inprog', [])

    compact_in_progress = False

    for operation in in_progress_ops:
        command = operation.get('command', {})
        namespace = operation.get('ns', {})
        if 'compact' in command:
            compact_in_progress = True
            # You can also check additional information about the compact operation here
            # For example, the 'ns' field contains the namespace (database.collection) being compacted.
            # ns = operation.get('ns', '')
            print(f"Compacting: {namespace}")
            break

    if compact_in_progress:
        print("Compact operation in progress.")
    else:
        print("No compact operation in progress.")

except Exception as e:
    print("An error occurred:", e)
finally:
    client.close()

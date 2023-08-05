import pymongo
import math
import argparse


class ScaleFactor:
    def __init__(self, unit="MB"):
        self.unit = unit.upper()
        self.factor = self._get_scale_factor()

    def _get_scale_factor(self):
        units = {
            "B": 1,
            "KB": math.pow(1024, 1),
            "MB": math.pow(1024, 2),
            "GB": math.pow(1024, 3),
            "TB": math.pow(1024, 4),
            "PB": math.pow(1024, 5),
            "EB": math.pow(1024, 6),
            "ZB": math.pow(1024, 7),
            "YB": math.pow(1024, 8),
        }
        return units.get(self.unit, 1)

def format_unit(metric):
    return f"{round((metric / scale.factor) * 100) / 100} {scale.unit}"

def format_pct(numerator, denominator):
    return f"{round((numerator / denominator) * 1000) / 10}%"

def format_ratio(metric):
    return f"{round(metric * 100) / 100}:1"

def print_coll_header(coll_total):
    print("\n" + "=" * term_width)
    print(f"Collections (visible): {coll_total}")

def print_collection(coll_name, coll_stats):
    print(f" {('-' * (term_width - 1)).rjust(term_width)}")
    data_size = coll_stats.get('size', 0) + coll_stats.get('totalIndexSize', 0)
    storage_size = coll_stats.get('storageSize', 0)
    free_storage_size = coll_stats.get('freeStorageSize', 0)
    compression = data_size / storage_size if storage_size != 0 else 0
    objects = coll_stats.get('objects', 0)
    orphans = coll_stats.get('orphans', 0)

    print(f"{(' ' + coll_name).ljust(row_header)} "
          f"{format_unit(data_size).rjust(column_width)} "
          f"{format_ratio(compression).rjust(column_width + 1)} "
          f"{format_unit(storage_size).rjust(column_width)} "
          f"{format_unit(free_storage_size).rjust(column_width + 8)} "
          f"{str(objects).rjust(column_width)} "
          f"{str(orphans).rjust(column_width - 5)}")

def print_db_header(db_name):
    print("\n")
    print("=" * term_width)
    print(f"Database: {db_name}".ljust(row_header + 1),
          f"Data size".rjust(column_width),
          f"Compression".rjust(column_width + 1),
          f"Size on disk".rjust(column_width),
          f"Free blocks (reuse)".rjust(column_width + 8),
          f"Object count".rjust(column_width),
          f"Orphans".rjust(column_width - 4))
    print("=" * term_width)

def print_db_stats(stats):
    total_namespace_size = 0
    total_compression = 0
    total_storage_size = 0
    total_free_storage_size = 0
    total_objects = 0
    total_orphans = 0
    total_index_size = 0
    total_index_keys = 0  # New variable to hold the total index keys
    total_nindex_size = 0 
    indexes = []

    for coll in stats["collections"]:
        total_namespace_size += coll["stats"].get('size', 0) + coll["stats"].get('totalIndexSize', 0)
        total_compression += coll["stats"].get('compression', 0)
        total_storage_size += coll["stats"].get('storageSize', 0)
        total_free_storage_size += coll["stats"].get('freeStorageSize', 0)
        total_objects += coll["stats"].get('objects', 0)
        total_orphans += coll["stats"].get('orphans', 0)
        total_orphans += coll["stats"].get('orphans', 0)
        total_index_size += coll["stats"].get('totalIndexSize', 0)
        total_nindex_size += coll["stats"].get('nindexes', 0)

        # Fetch the actual index size using the dataSize attribute
#        for index in coll["stats"].get('indexDetails', {}).values():
#            indexes.append(index)  # Append each index info to the list
#            total_index_size += index.get('dataSize', 0)
#            total_index_keys += index.get('numKeys', 0)

    print("=" * term_width)
    print(f"Namespaces subtotal: {len(stats['collections'])} "
          f"{format_unit(total_namespace_size).rjust(column_width)} "
          f"{format_ratio(total_compression).rjust(column_width + 1)} "
          f"{format_unit(total_storage_size).rjust(column_width)} "
          f"{format_unit(total_free_storage_size).rjust(column_width + 8)} "
          f"{str(total_objects).rjust(column_width)} "
          f"{str(total_orphans).rjust(column_width - 5)}")

    print(f"Indexes subtotal: {str(total_nindex_size)}"
          f"{format_unit(total_index_size).rjust(column_width)} "  # Use the accurate index size
          f"{''.rjust(column_width + 1)} "
#          f"{format_unit(total_index_size).rjust(column_width)} "  # Use the accurate index size
    )
    print("=" * term_width)

def is_collection_a_view(database, coll_name):
    """
    Check if the collection is a view.

    :param database: The MongoDB database instance.
    :param coll_name: The name of the collection to check.
    :return: True if the collection is a view, False otherwise.
    """
    try:
        coll_options = database[coll_name].options()
        return coll_options.get('viewOn') is not None
    except Exception:
        return False
    
def get_stats(client):
    db_path = {}
    db_names = client.list_database_names()
    for db_name in db_names:
        database = client[db_name]
        db_stats = database.command("dbStats")
        collections = database.list_collection_names()
        collection_stats = []
        for coll_name in collections:
            if is_collection_a_view(database, coll_name):
                continue
            coll_stats = database.command("collStats", coll_name)
            num_documents = database.command("collStats", coll_name)['count']
            coll_stats["objects"] = num_documents
            collection_stats.append({"name": coll_name, "stats": coll_stats})
        db_path[db_name] = {"stats": db_stats, "collections": collection_stats}
    return db_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MongoDB Database Statistics Tool")
    parser.add_argument("connection_string", type=str, help="MongoDB connection string")
    args = parser.parse_args()
    term_width = 134
    column_width = 14
    row_header = 40
    scale = ScaleFactor("MB")
    
    try:
        client = pymongo.MongoClient(args.connection_string)
        stats = get_stats(client)
    
        for db_name, stats in stats.items():
            print_db_header(db_name)
            print_coll_header(len(stats["collections"]))
            for coll in stats["collections"]:
                print_collection(coll["name"], coll["stats"])
            print_db_stats(stats)
              
    except pymongo.errors.ConnectionFailure:
        print("Failed to connect to MongoDB. Please check the connection string.")


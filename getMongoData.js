// Wrap your code in a function
function getMongoData() {
var stats = {
    "dbs": 0,
    "collections": 0,
    "objects": 0,
    "dataSize": 0,
    "storageSize": 0,
    "indexes": 0,
    "indexSize": 0
};

var databases = db.adminCommand({listDatabases: 1}).databases;

for (var i in databases) {
    var dbName = databases[i].name;

    // Skip the "config" and "admin" databases
    if (dbName === "config" || dbName === "admin" || dbName === "local") {
        continue;
    }

    var configDBStats = db.getSiblingDB(dbName).stats();

    if (configDBStats.raw) {
        // Sharded cluster structure
        var configStats = db.getSiblingDB(dbName).stats().raw;
        var shardStatsArray = [];
        
        for (var shardName in configStats) {
            var shardStats = configStats[shardName];
            if (shardStats.db) {
                // Add the shard name to the shard statistics
                shardStats.shardName = shardName.split("/")[0]; // Extract the shard name
                shardStatsArray.push(shardStats);
            }
        }
        
        // Access the shard statistics array
        shardStatsArray.forEach(function(shardStats) {
            // Access and print the shard name and DB name
            print("Shard Name: " + shardStats.shardName);
            print("Shard DB: " + shardStats.db);
            // You can access and print other statistics as needed
            print("Collections: " + shardStats.collections);
            print("Objects: " + shardStats.objects);
            print("Data Size: " + shardStats.dataSize);
            print("Storage Size: " + shardStats.storageSize);
            print("Indexes: " + shardStats.indexes);
            print("Index Size: " + shardStats.indexSize);
            // Add more statistics as needed
            print("\n"); // Separate each shard's stats with a newline
        })
        
    } else {
        // Non-sharded cluster structure
        print("Database name: " + configDBStats.db)
        print("Collections: " + configDBStats.collections);
        print("Objects: " + configDBStats.objects);
        print("Data Size: " + configDBStats.dataSize);
        print("Storage Size: " + configDBStats.storageSize);
        print("Indexes: " + configDBStats.indexes);
        print("Index Size: " + configDBStats.indexSize);
        // Add more statistics as needed
        print("\n"); // Separate each db stats with a newline
    }
}

stats; // Return the stats object
}
// Call the function
getMongoData();
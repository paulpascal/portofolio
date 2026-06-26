# MongoDB Sharded Cluster

A reproducible, containerised **MongoDB sharded cluster** that demonstrates horizontal scaling,
replication and fault tolerance for large collections. The whole topology, config servers, multiple
shards (each a replica set), and a `mongos` router, runs locally with Docker Compose.

## Topology

- **Config servers**: a 3-member replica set holding cluster metadata.
- **Shards**: four shards, each a replica set, so data is partitioned horizontally and each partition is
  replicated for resilience.
- **Router (`mongos`)**: the entry point that routes queries to the right shard.
- **Sharding key**: hashed on `matricule` for even distribution across shards.

## Run

```bash
docker-compose up -d
```

Then initialise the replica sets and register the shards (the cluster is brought up step by step):

```bash
# 1. initialise the config-server replica set
docker exec -it <configsvr> mongosh --port 27201 admin   # rs.initiate({ ... })

# 2. initialise each shard's replica set (shard1..shard4)
docker exec -it <shard1_primary> mongosh --port 27301 admin   # rs.initiate({ ... })

# 3. add the shards through the router
docker exec -it <mongos> mongosh --port 27100
#   sh.addShard("shard1/...")  ... for each shard

# 4. enable sharding and shard a collection
#   sh.enableSharding("dit")
#   sh.shardCollection("dit.students", { matricule: "hashed" })
```

(See the inline commands in this repo for the exact host names and ports.)

## What it demonstrates

Hands-on cluster operations: configuring sharding and replica sets, distributing a collection with a
hashed shard key, and reasoning about scalability, replication and fault tolerance, all orchestrated with
Docker Compose.

## Stack

MongoDB · Docker · Docker Compose

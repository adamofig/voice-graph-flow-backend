references: 
https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/vector-search-quick-start/?deployment-type=self

here is the documentation for mongodb vector search, check is it works. 
otherwise try with atlas. 

its being hard to achive this in local. 


# Local MongoDB Setup for Vector Search

This guide describes how to set up a local MongoDB 8.0 instance with Search Index support using Docker. This setup is required for performing semantic search using the `$vectorSearch` stage in your local environment.

## Architecture

The setup consists of two main components:
- **mongod**: The MongoDB Community Server (port 27017).
- **mongot**: The MongoDB Search engine component (port 27028).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (MacOS/Windows) or Docker Engine (Linux).
- `mongosh` installed locally (optional, for verification).

## Files in `docker-mongodb/`

- `docker-compose.yml`: Orchestrates the services.
- `mongod.conf`: MongoDB server configuration.
- `mongot.conf`: MongoDB Search configuration.
- `init-mongo.sh`: Initialization script to create the `searchCoordinator` role.
- `pwfile`: Password file for service interconnection.

## Setup Instructions

1.  **Navigate to the directory**:
    ```bash
    cd docker-mongodb
    ```

2.  **Start the services**:
    ```bash
    docker compose up -d
    ```

3.  **Verify the setup**:
    Check the logs to ensure initialization is complete:
    ```bash
    docker compose logs -f
    ```
    Wait until you see: `MongoDB initialization completed`.

4.  **Confirm Search Service is working**:
    Connect to your local MongoDB:
    ```bash
    mongosh "mongodb://localhost:27017/?directConnection=true"
    ```
    Switch to your database and try listing search indexes:
    ```javascript
    use rag_project
    db.vectorData.listSearchIndexes()
    ```
    If it returns `[]` (empty list) instead of an error, the search service is operational.

## Usage in Python

Your `database.py` should use the following connection string for local development:
```python
MONGODB_URI = "mongodb://localhost:27017/?directConnection=true"
```

> [!IMPORTANT]
> This setup is intended for **local development and testing only**. It is not secured for production use.

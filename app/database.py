import os
from pymongo import MongoClient
from bson.binary import Binary, BinaryVectorDtype
from dotenv import load_dotenv

load_dotenv()

class MongoManager:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://admin:password123@localhost:27017")
        self.client = None
        self.db = None
        self.collection = None

    def connect(self, db_name=None, collection_name="vectorData"):
        """Connects to MongoDB and sets the database and collection."""
        try:
            self.client = MongoClient(self.uri)
            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
            # Use database name from URI if not provided
            if db_name is None:
                # Try to get the default database from the client (parsed from URI)
                self.db = self.client.get_default_database()
                if self.db is None:
                    self.db = self.client["rag_project"]
                print(f"Using database: {self.db.name}")
            else:
                self.db = self.client[db_name]
                print(f"Using database (provided): {self.db.name}")

            self.collection = self.db[collection_name]
            
            # Ensure the collection exists by creating it if it doesn't
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                print(f"Collection '{collection_name}' created.")
            
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False

    def to_bson_vector(self, vector, dtype=BinaryVectorDtype.FLOAT32):
        """Converts a list of floats to BSON Binary vector format."""
        return Binary.from_vector(vector, dtype)

    def create_vector_index(self, collection_name="vectorData", field_name="vector", dimensions=1536):
        """Creates a native MongoDB 8.0 vector index using HNSW."""
        if self.db is None:
            print("Error: Not connected to a database.")
            return

        try:
            # MongoDB 8.0 native vector index definition
            index_model = {
                "name": "vector_index",
                "type": "vector",
                "definition": {
                    "fields": [
                        {
                            "path": field_name,
                            "type": "vector",
                            "numDimensions": dimensions,
                            "similarity": "cosine",
                            "indexConfig": {
                                "type": "hnsw"
                            }
                        }
                    ]
                }
            }
            
            # Use command to create the index (native MongoDB 8.0 syntax)
            self.db.command({
                "createIndexes": collection_name,
                "indexes": [index_model]
            })
            print(f"Vector index created on {collection_name}.{field_name}")
        except Exception as e:
            # If it already exists, it might fail, which is often fine in a script
            print(f"Note: Vector index creation info: {e}")

    def create_text_index(self, collection_name="vectorData", field_name="text"):
        """Creates a text index for the specified field."""
        if self.db is None:
            print("Error: Not connected to a database.")
            return

        try:
            self.collection.create_index([(field_name, "text")], name="text_search_index")
            print(f"Text index created on {collection_name}.{field_name}")
        except Exception as e:
            print(f"Note: Text index creation info: {e}")

    def keyword_search(self, query_text, limit=5):
        """Performs a native MongoDB text search using the $text operator."""
        if self.collection is None:
            print("Error: Not connected to a collection.")
            return []

        pipeline = [
            {
                "$match": {
                    "$text": {"$search": query_text}
                }
            },
            {
                "$addFields": {
                    "score": {"$meta": "textScore"}
                }
            },
            {
                "$sort": {"score": {"$meta": "textScore"}}
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "score": 1,
                    "source": 1,
                    "chunk_index": 1,
                    "metadata": 1
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))

    def vector_search(self, query_vector, limit=5, num_candidates=100, include_explain=False):
        """Performs a native MongoDB 8.0 vector search."""

        print(f"Starting vector search (explain={include_explain})")
        if self.collection is None:
            print("Error: Not connected to a collection.")
            return []

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "vector",
                    "queryVector": query_vector,
                    "numCandidates": num_candidates,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "score": {"$meta": "vectorSearchScore"},
                    "source": 1,
                    "chunk_index": 1,
                    "metadata": 1
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        if include_explain:
            print("Fetching explain details...")
            try:
                explain_data = self.db.command(
                    "aggregate", self.collection.name,
                    pipeline=[pipeline[0]], # Only the $vectorSearch stage
                    cursor={},
                    explain=True
                )
                
                # Extract relevant explain info for the user
                # Based on MongoDB Vector Search explain output
                if "stages" in explain_data:
                    vs_stage = explain_data["stages"][0].get("$vectorSearch", {})
                    explain_info = vs_stage.get("explain", {})
                    
                    # Return list with explain metadata attached
                    return {
                        "results": results,
                        "explain": explain_info
                    }
            except Exception as e:
                print(f"Failed to get explain data: {e}")
                return {
                    "results": results,
                    "explain_error": str(e)
                }

        return results

    def atlas_search(self, query_text, limit=5):
        """Performs an Atlas Search using the $search operator."""
        if self.collection is None:
            print("Error: Not connected to a collection.")
            return []

        pipeline = [
            {
                "$search": {
                    "index": "text_index", # As per user request example
                    "text": {
                        "query": query_text,
                        "path": "text", # Assuming 'text' is the field for content
                        "fuzzy": {"maxEdits": 1}
                    },
                    "scoreDetails": True,
                    "highlight": {
                        "path": "text"
                    }
                }
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "score": {"$meta": "searchScore"},
                    "scoreDetails": {"$meta": "searchScoreDetails"},
                    "highlights": {"$meta": "searchHighlights"},
                    "source": 1,
                    "chunk_index": 1,
                    "metadata": 1
                }
            }
        ]
        print('about to start agregation')
        return list(self.collection.aggregate(pipeline))

    def insert_chunk(self, data):
        """Inserts a single chunk document into the collection."""
        if self.collection is not None:
            return self.collection.insert_one(data)
        else:
            print("Error: Not connected to a collection.")
            return None

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    from embedding import get_embedding
    
    # Test connection and search
    mongo = MongoManager()
    if mongo.connect():
        print("Connection test passed.")
        
        # Test Query: "What does Adamo do?"
        query_text = "What does Adamo do?"
        print(f"\nSearching for: '{query_text}'")
        
        try:
            # 1. Get embedding
            raw_vector = get_embedding(query_text)
            # 2. Convert to BSON
            bson_vector = mongo.to_bson_vector(raw_vector)
            # 3. Search
            results = mongo.vector_search(bson_vector, limit=3)
            
            if results:
                print(f"Found {len(results)} relevant chunks:")
                for i, res in enumerate(results):
                    print(f"\n[{i+1}] Score: {res.get('score', 'N/A')}")
                    print(f"Text: {res.get('text')[:200]}...")
            else:
                print("No results found. Ensure you have indexed documents first.")
                
        except Exception as e:
            print(f"Error during search test: {e}")
        finally:
            mongo.close()
    else:
        print("Connection test failed.")

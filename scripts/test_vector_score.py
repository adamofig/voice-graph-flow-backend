from app.database import MongoManager
from app.embedding import get_embedding

mongo = MongoManager()
if mongo.connect():
    query = "Walmart relocation"
    raw_vector = get_embedding(query)
    bson_vector = mongo.to_bson_vector(raw_vector)
    
    print("\n--- Testing vector_search with explain=True ---")
    output = mongo.vector_search(bson_vector, limit=2, include_explain=True)
    
    if isinstance(output, dict):
        print("Results keys:", output.keys())
        for i, res in enumerate(output["results"]):
            print(f"[{i+1}] Score: {res.get('score')}")
        
        if "explain" in output:
            print("Explain data found!")
            # print(output["explain"])
    else:
        print("Output is not a dict, something went wrong with explain mode.")

    print("\n--- Testing vector_search with explain=False ---")
    results = mongo.vector_search(bson_vector, limit=2, include_explain=False)
    for i, res in enumerate(results):
        print(f"[{i+1}] Score: {res.get('score')}")
    
    mongo.close()

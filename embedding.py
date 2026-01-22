import os
from google import genai
from typing import List, Union, Optional
from dotenv import load_dotenv

# Load environment variables (for GOOGLE_API_KEY)
load_dotenv()

def get_embedding(
    contents: Union[str, List[str]], 
    model: str = "text-embedding-004",
    api_key: Optional[str] = None
) -> Union[List[float], List[List[float]]]:
    """
    Generates embeddings for the given content using the Google GenAI SDK.
    
    Args:
        contents: A single string or a list of strings to embed.
        model: The Google embedding model to use. Defaults to "text-embedding-004".
        api_key: Optional API key. If not provided, it will look for GOOGLE_API_KEY env var.
        
    Returns:
        A list of floats (if single string) or a list of lists of floats (if multiple strings).
    """
    client = genai.Client(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
    
    result = client.models.embed_content(
        model=model,
        contents=contents
    )
    
    # The SDK returns a list of embeddings
    # If a single content was passed, we might want to return just that one vector
    # But for consistency with the SDK's batch-first approach:
    embeddings = [item.values for item in result.embeddings]
    
    if isinstance(contents, str):
        return embeddings[0]
    
    return embeddings

if __name__ == "__main__":
    # Test block for easy verification and Jupyter usage
    test_text = "Hello world, this is a test of the Gemini embedding system."
    try:
        vector = get_embedding(test_text)
        print(f"Successfully generated embedding!")
        print(f"Vector length: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
    except Exception as e:
        print(f"Error generating embedding: {e}")
        print("Note: Ensure GOOGLE_API_KEY is set in your .env file.")

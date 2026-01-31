from openai import OpenAI
from configuration.settings import OPENAI_API_KEY
from loguru import logger

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str, model="text-embedding-3-small"):
    """
    Generate an embedding for the input text using OpenAI's API.
    
    Args:
        text (str): The text to generate an embedding for.
        model (str): The model to use. Defaults to "text-embedding-3-small". 
                     Check if "text-embedding-ada-002" is needed for compatibility.
    
    Returns:
        list[float]: The embedding vector.
    """
    text = text.replace("\n", " ")
    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        return None

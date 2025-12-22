import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()

qdrant_url = os.getenv('QDRANT_URL')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

try:
    collections = client.get_collections()
    print("Connection Successful! Collections:")
    for col in collections.collections:
        print(col.name)
except Exception as e:
    print(f"Connection Failed: {e}")
import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("mistral_api_key")
SERPAPI_API_KEY = os.getenv("serpapi")
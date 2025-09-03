import os
from dotenv import load_dotenv

load_dotenv()

# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = "card"

# Upstage
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

# Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Vector DB
EMBEDDING_DIMENSION = 4096

# Text Splitter
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Cache
TEXT_CACHE_DIR = "text_cache"

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Server
API_V1_STR = "/api/v1"
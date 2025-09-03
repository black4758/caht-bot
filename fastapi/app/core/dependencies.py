from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_upstage import UpstageEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase # Import motor

from app.core.config import (
    PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME,
    UPSTAGE_API_KEY, GEMINI_API_KEY, EMBEDDING_DIMENSION,
    CHUNK_SIZE, CHUNK_OVERLAP,
    MONGODB_URI, DB_NAME # Import MongoDB config
)

# Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Upstage Embeddings
embeddings = UpstageEmbeddings(api_key=UPSTAGE_API_KEY, model="solar-embedding-1-large")

# Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

# Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

# MongoDB Client
_mongo_client: AsyncIOMotorClient = None

async def get_mongo_db() -> AsyncIOMotorDatabase:
    global _mongo_client
    if _mongo_client is None:
        print(f"Attempting to connect to MongoDB at {MONGODB_URI}")
        _mongo_client = AsyncIOMotorClient(MONGODB_URI)
        try:
            # The ping command is cheap and does not require auth.
            await _mongo_client.admin.command('ping')
            print("MongoDB connection successful!")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            _mongo_client = None # Reset client if connection fails
            raise
    return _mongo_client[DB_NAME]

def get_pinecone_index():
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating a new Pinecone index: {PINECONE_INDEX_NAME} with dimension {EMBEDDING_DIMENSION}")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=PINECONE_ENVIRONMENT
            )
        )
    return pc.Index(PINECONE_INDEX_NAME)

def get_embeddings():
    return embeddings

def get_llm():
    return llm

def get_text_splitter():
    return text_splitter
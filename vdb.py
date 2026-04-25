from dotenv import load_dotenv
load_dotenv()
import os
import uuid
from typing import List, Optional
from qdrant_client import QdrantClient
from models import Transaction

# Connection to Qdrant Vector DB
QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
COLLECTION_NAME = "transactions"

# Initialize Qdrant client
try:
    # Handle case where QDRANT_HOST might be a full URL (including http://)
    if QDRANT_HOST.startswith(("http://", "https://")):
        qdrant_client = QdrantClient(url=QDRANT_HOST)
    else:
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
except Exception as e:
    print(f"Warning: Could not connect to Qdrant during init: {e}")
    qdrant_client = None


def store_transactions_in_vdb(transactions: List[Transaction]):
    """
    Store transactions in Qdrant using the high-level .add() method.
    This handles embedding generation automatically using FastEmbed.
    """
    if not transactions or qdrant_client is None:
        return

    documents = [tx.to_document_string() for tx in transactions]
    metadatas = [tx.model_dump() for tx in transactions]
    ids = [str(uuid.uuid4()) for _ in transactions]

    try:
        qdrant_client.add(
            collection_name=COLLECTION_NAME,
            documents=documents,
            metadata=metadatas,
            ids=ids
        )
        print(f"Successfully stored {len(transactions)} transactions in Qdrant (using FastEmbed).")
    except Exception as e:
        print(f"Error storing transactions in Qdrant: {e}")


def clear_vdb():
    """Wipes all transactions from the vector database."""
    if qdrant_client is None:
        return False

    try:
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"Cleared Qdrant collection '{COLLECTION_NAME}'")
        return True
    except Exception as e:
        print(f"Failed to clear Qdrant collection: {e}")
        return False


def query_transactions(query: str, limit: int = None) -> List[Transaction]:
    """
    Retrieve relevant transactions based on a semantic query using .query().
    This handles query embedding automatically.
    """
    if qdrant_client is None:
        return []

    search_limit = limit if limit is not None else 1000

    try:
        results = qdrant_client.query(
            collection_name=COLLECTION_NAME,
            query_text=query,
            limit=search_limit
        )
        
        # Results from .query() have metadata which contains our transaction data
        return [Transaction(**res.metadata) for res in results]
    except Exception as e:
        print(f"Error querying Qdrant: {e}")
        return []


def get_all_transactions() -> List[Transaction]:
    """Fetch all stored transactions using scroll."""
    if qdrant_client is None:
        return []

    try:
        # Standard scroll works the same way
        results, next_page = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000
        )
        return [Transaction(**hit.payload) for hit in results]
    except Exception as e:
        print(f"Error fetching all transactions: {e}")
        return []

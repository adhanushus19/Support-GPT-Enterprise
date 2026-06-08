import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config import settings
from src.rag.embedding import embedding_provider
from src.models.schemas import Citation

class VectorStoreManager:
    """
    Manages vector storage and retrieval using ChromaDB.
    Supports version filtering, semantic search, and metadata querying.
    """
    def __init__(self):
        # Configure Chroma client based on config settings
        if settings.CHROMA_HOST and settings.CHROMA_PORT:
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT
            )
        else:
            # Persistent or in-memory SQLite storage
            persist_dir = settings.VECTOR_DB_PERSIST_DIR
            if settings.APP_ENV == "testing":
                # Always run in-memory for unit test isolation
                self.client = chromadb.EphemeralClient()
            else:
                os.makedirs(persist_dir, exist_ok=True)
                self.client = chromadb.PersistentClient(path=persist_dir)

        # Retrieve or create collection
        self.collection_name = "kb_documents"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    async def add_document_chunks(
        self, 
        doc_id: str, 
        chunks: List[str], 
        metadata: Dict[str, Any], 
        version: str = "v1"
    ) -> None:
        """
        Embed document chunks and save to ChromaDB.
        """
        if not chunks:
            return
            
        embeddings = await embedding_provider.get_embeddings(chunks)
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Inject KB version into metadata for filtering
        metadatas = []
        for i in range(len(chunks)):
            meta = metadata.copy()
            meta["version"] = version
            meta["chunk_index"] = i
            meta["doc_id"] = doc_id
            metadatas.append(meta)
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=chunks
        )

    async def query_kb(
        self, 
        query: str, 
        version: str = "v1", 
        top_k: int = 3, 
        category_filter: Optional[str] = None
    ) -> List[Citation]:
        """
        Run a semantic search against the knowledge base collection.
        Enforces KB version filters and optional category filters.
        """
        query_vector = await embedding_provider.get_embedding(query)
        
        # Structure metadata filter
        where_filter: Dict[str, Any] = {"version": version}
        if category_filter:
            where_filter = {
                "$and": [
                    {"version": version},
                    {"category": category_filter}
                ]
            }

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_filter
        )

        citations = []
        if not results or "documents" not in results or not results["documents"][0]:
            return []

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, distances):
            # Compute score from cosine distance (cosine distance = 1 - cosine similarity)
            score = 1.0 - dist if dist is not None else 0.5
            source = meta.get("title", meta.get("doc_id", "Unknown Document"))
            
            # Format source label with version
            source_label = f"{source} ({meta.get('version', 'v1')})"
            
            citations.append(Citation(
                source=source_label,
                text=doc,
                score=round(score, 4),
                version=meta.get("version", "v1")
            ))

        return citations

    def clear_database(self) -> None:
        """Helper to purge all indexed documents (used in test teardown)."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            pass

vector_store = VectorStoreManager()

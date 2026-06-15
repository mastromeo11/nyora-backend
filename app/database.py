import chromadb
from app.config import CHROMA_PATH, COLLECTION_NAME
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

class BGEEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        from app.embedding.text_embedder import embed_text
        return embed_text(input)

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.text_collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=BGEEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"}
        )
        self.image_collection = self.client.get_or_create_collection(
            name="image_collection",
            metadata={"hnsw:space": "cosine"}
        )
        self._initialized = True

    def add_documents(self, ids: list[str], documents: list[str], metadatas: list[dict] = None):
        """
        Inserts document chunks and their metadata into ChromaDB.
        
        Args:
            ids (list[str]): Unique identifiers for each chunk.
            documents (list[str]): The text content of each chunk.
            metadatas (list[dict]): Optional metadata dictionaries (e.g. source, page).
        """
        try:
            self.text_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"Error adding documents to collection: {e}")
            raise e

    def search_documents(self, query_texts: list[str], n_results: int = 5) -> dict:
        """
        Queries ChromaDB collection with semantic similarity using query texts.
        
        Args:
            query_texts (list[str]): A list of query string search targets.
            n_results (int): The number of matching chunks to retrieve.
            
        Returns:
            dict: The matching documents, IDs, distances, and metadatas.
        """
        try:
            return self.text_collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
        except Exception as e:
            print(f"Error searching documents in collection: {e}")
            raise e

    def reset_db(self):
        """
        Clears the collection and resets database state.
        """
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        try:
            self.client.delete_collection("image_collection")
        except Exception:
            pass
        self.text_collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=BGEEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"}
        )
        self.image_collection = self.client.get_or_create_collection(
            name="image_collection",
            metadata={"hnsw:space": "cosine"}
        )

    def add_image_document(self, id: str, embedding: list[float], metadata: dict):
        """
        Inserts image embeddings and their metadata into ChromaDB image_collection.
        """
        try:
            self.image_collection.add(
                ids=[id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Error adding image document to collection: {e}")
            raise e

    def search_images(self, query_embedding: list[float], n_results: int = 5) -> dict:
        """
        Queries ChromaDB image collection with semantic similarity using raw CLIP embeddings.
        """
        try:
            return self.image_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
        except Exception as e:
            print(f"Error searching image collection: {e}")
            raise e

db = Database()

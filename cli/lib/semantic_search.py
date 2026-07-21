from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
#helpful functions and variables declared below
def verify_model():
    ss_instance = SemanticSearch()
    model = ss_instance.model
    print(f"Model loaded: {model}")
    print(f"Max sequence length: {model.max_seq_length}")

def embed_text(text):
    ss_instance = SemanticSearch()
    model = ss_instance.model
    embedding = ss_instance.generate_embedding(text)
    print(f"Text: {text}")
    print(f"First 3 dimensions: {embedding[:3]}")
    print(f"Dimensions: {embedding.shape[0]}")#class 

def verify_embeddings():
    ss_instance = SemanticSearch()
    model = ss_instance.model
    with open("data/movies.json","r") as movies_file:
        movies = json.load(movies_file)
        documents = movies["movies"]
    embeddings = ss_instance.load_or_create_embeddings(documents)
    print(f"Number of docs:   {len(documents)}")
    print(f"Embeddings shape: {embeddings.shape[0]} vectors in {embeddings.shape[1]} dimensions")

def embed_query_text(query):
    ss_instance = SemanticSearch()
    embedding = ss_instance.generate_embedding(query)
    print(f"Query: {query}")
    print(f"First 3 dimensions: {embedding[:3]}")
    print(f"Shape: {embedding.shape}")

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


class SemanticSearch():
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = None
        self.documents = None
        self.document_map = {}

    def generate_embedding(self, text):
        if text.strip() == " " or text =="":
            raise ValueError("text cant be empty")
        encoded_text = self.model.encode([text])
        return encoded_text[0]
    
    def build_embeddings(self, documents):
        self.documents = documents
        movieString = []
        for document in documents:
            self.document_map[document['id']] = document
            formatted_text = f"{document['title']}: {document['description']}"
            movieString.append(formatted_text)
        
        self.embeddings = self.model.encode(movieString,show_progress_bar=True)
        
        
        np.save("cache/movie_embeddings.npy",self.embeddings)

        return self.embeddings 

    def load_or_create_embeddings(self, documents):
        self.documents = documents
        for document in documents:
            self.document_map[document['id']] = document
        if os.path.exists("cache/movie_embeddings.npy"):
            self.embeddings = np.load("cache/movie_embeddings.npy")
            if len(self.embeddings) == len(documents):
                return self.embeddings
        return self.build_embeddings(documents)
    
    def search(self,query,limit):
        if self.embeddings is None:
            raise ValueError("No embeddings loaded. Call `load_or_create_embeddings` first.")
        query_embedding = self.generate_embedding(query)
        results = []
        for i, doc_embedding in enumerate(self.embeddings):
            score = float(cosine_similarity(query_embedding, doc_embedding))
            doc = self.documents[i]
            results.append((score, doc))
        results.sort(key=lambda x: x[0], reverse=True)

        formatted_results = []
        for score, doc in results[:limit]:
            formatted_results.append({
                "score": score,
                "title": doc["title"],
                "description": doc["description"],
            })

        return formatted_results
    
            

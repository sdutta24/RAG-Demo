import os
from dotenv import load_dotenv
import requests
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams,PointStruct
)
from groq import Groq
from pathlib import Path

load_dotenv()
load_dotenv(Path(__file__).with_name(".env"))

GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdutta24/AI_Demo/refs/heads/main/techcorp_leave_attendance_policies.txt"
CHUNK_SIZE = 50
collection_name = "docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

SYSTEM_PROMPT = """You are a helpful HR assistant.
Answer the user's question using ONLY the context provided below.
If the context does not contain enough information, say so — do not make things up.
Always cite the section name when referencing specific information."""

def load_document(url: str) ->str:
    response = requests.get(url, timeout =10)
    response.raise_for_status()
    return response.text

def parse_word_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> list[dict]:
    clean_lines = []
    for line in text.splitlines():
        line = line.strip().lstrip("#").strip().strip("-").strip()
        if line:
            clean_lines.append(line)

    words = " ".join(clean_lines).split() # join all the cleaned line in one string and split into a list of words
    chunks = []
    for i in range(0, len(words), chunk_size):
            content = " ".join(words[i:i+chunk_size])
            chunks.append({
                "chunk_index": len(chunks),
                "content": content
            })
    return chunks

def build_chunk_text(chunk: dict) -> str:
    return chunk['content']

def qdrant_client(host, port):
    client = QdrantClient(host='localhost', port=6333)
    return client

def create_collection(client, collection_name, dimension):
    client.recreate_collection(
        collection_name = collection_name,
        vectors_config = VectorParams(
            size = DIM,
            distance = Distance.COSINE
        )
    )

def create_points(chunks, embeddings):
    points=[
        PointStruct(
            id = i,
            vector = embedding,
            payload = {
                "chunk_index": chunk['chunk_index'],
                "content": chunk['content']
            }
        )
        for i, (chunk,embedding) in enumerate(zip(chunks, embeddings))
    ]
    return points

def retrive(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed the query and return the top-k most similar chunks.

    Args:
        query          : User's question.
        top_k          : Number of chunks to return.
        section_filter : Optional H2 heading to restrict the search scope.
    """
    query_vector = model.encode(query).tolist()
    hits = client.query_points(
        collection_name = collection_name,
        query = query_vector,
        limit = top_k,
        with_payload = True,
    )
    return [{**hit.payload, "score" : round(hit.score, 4)} for hit in hits.points]

def build_context(retrived_chunks: list[dict]) -> str:
        parts = []
        for i, chunk in enumerate(retrived_chunks,1):
            parts.append(f"Source {i}:\n{chunk['content']}")
        return "\n\n----\n\n".join(parts)
def rag(query: str, top_k: int = 5) -> str:
    """
    End-to-end RAG pipeline:
      1. Retrieve relevant chunks from Qdrant
      2. Format them as a context block
      3. Send context + query to Groq and return the answer
    """
    #Step 1: Retrieve relevant chunks from Qdrant
    chunks = retrive(query, top_k=3)
    if not chunks:
        return "No relevant content in the document"

    context = build_context(chunks) 
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    response = groq_client.chat.completions.create(
         model = os.getenv("GROQ_MODEL"),
         messages =[
              {"role": "system", "content": SYSTEM_PROMPT},
              {"role": "user", "content": user_message}
         ],
         temperature = 0.2, 
             
    )
    return response.choices[0].message.content, context

def main():
     global model, DIM, client, groq_client
     model = SentenceTransformer(EMBEDDING_MODEL)
     DIM = model.get_embedding_dimension()
     groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
     raw_text = load_document(GITHUB_RAW_URL)
     chunks = parse_word_chunks(raw_text,CHUNK_SIZE)
     chunk_text = [build_chunk_text(c) for c in chunks]
     embeddings = model.encode(chunk_text).tolist()
     client = qdrant_client('localhost', 6333)
     create_collection(client, collection_name, DIM)
     points = create_points(chunks, embeddings)
     results = client.upsert(
         collection_name = collection_name,
         points = points,
         wait = True
         )
     print(f"result status: {results.status}")
     info = client.get_collection(collection_name)
     
     query = input("\nAsk a Question: ")
     
     retrive_results = retrive(query, top_k=3)

     for r in retrive_results:
         print(f"[score = {r['score']: .4f}]")
         print(f"Content: {r['content'][:200]}...")

     answer,context = rag(query, top_k=3)
     print(f"\nAnswer: {answer}")
     print(f"\nContext: {context}")

if __name__ == "__main__":
    main()

    

     


    





    
    


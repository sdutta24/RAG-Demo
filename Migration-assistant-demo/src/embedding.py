from sentence_transformers import SentenceTransformer
import numpy as np


EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def load_embedding_model():
    model = SentenceTransformer(EMBEDDING_MODEL)
    return model

def create_embeddings(model,chunks):
    chunk_content= [cc['content'] for cc in chunks]
    embeddings = model.encode(chunk_content, show_progress_bar = True)
    return embeddings

def domain_embedding(model):
    domain_description = """
Oracle to Snowflake database migration,
Oracle SQL and PL/SQL conversion,
Snowflake architecture,
data migration,
ETL modernization,
and migration best practices.
"""
    dmn_embd = model.encode(domain_description.strip(), show_progress_bar = True)
    return dmn_embd

def query_embedding(model,query):
    q_embd = model.encode(query)
    return q_embd

def filter_by_similarity(chunks,embeddings,domain_embedding,model,threshold):
    scores = model.similarity(domain_embedding,embeddings)
    selected_chunks = []
    for chunk,score in zip(chunks,scores[0]):
        print(f"Chunk_ID: {chunk['chunk_id']} |"
              f"Relevance Score: {float(score):.4f} |"
              f"Content: {chunk['content'][:80]}")
        if score >= threshold:
            selected_chunks.append({
                **chunk,
                "relevance_score": float(score)
            })
    return selected_chunks








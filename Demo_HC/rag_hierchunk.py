import os
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)
import docling
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import HierarchicalChunker
from hierarchical.postprocessor import ResultPostprocessor
from pathlib import Path

SYSTEM_PROMPT="""You are a helpful HR assistant.
Answer the user's question using ONLY the context provided below.
If the context does not contain enough information, say so — do not make things up.
Always cite the section name when referencing specific information."""
    
load_dotenv(Path(__file__).with_name(".env"))
def load_document(url: str):
    converter = DocumentConverter()
    response = converter.convert(url)
    ResultPostprocessor(response).process()
    return response.document

def create_chunk(document):
    chunker = HierarchicalChunker()
    doc_chunks = list(chunker.chunk(document))
    return doc_chunks

def convert_chunk(doc_chunks):
    """
    Convert a Docling DocChunk into a plain dict.

    headings   → list preserved as-is
    content    → paragraph text
    chunk_text → breadcrumb + content  (what gets embedded)
    """
    heading = doc_chunks.meta.headings or []
    content = doc_chunks.text.strip()
    breadcrumb = ">".join(heading)
    chunk_text = f"{breadcrumb}\n\n{content}" if breadcrumb else content
    return {
        "heading":heading,
        "content":content,
        "chunk_text":chunk_text,
    }
def qdrant_client(host='localhost',port=6333):
    client = QdrantClient(host=host,port=port)
    return client
def create_collection(client,collection_name,dimension):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=dimension,
            distance=Distance.COSINE
        )
    )
def create_points(chunks,embeddings):
    points=[
        PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                'heading' : chunk['heading'],
                'content' : chunk['content'],
                'chunk_text' : chunk['chunk_text']
            },
        )
    for i, (chunk,embedding) in enumerate(zip(chunks,embeddings))
        ]   
    return points
    
def retrieve(query,top_k=5):
    query_vector=embedder.encode(query).tolist()
    hits=client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    hits=getattr(hits,"points",hits)
    return[{**hit.payload,'score' : round(hit.score,4)} for hit in hits]
def build_context(results : list[dict]):
    parts=[]
    for i,chunk in enumerate(results,1):
        parts.append(f"Source {i} : \n {chunk['content']}")
    return "\n\n --- \n\n".join(parts)
def rag(query : str,top_k : int = 5):
    """
    End-to-end RAG pipeline:
      1. Retrieve relevant chunks from Qdrant
      2. Format them as a context block
      3. Send context + query to Groq and return the answer
    """
    result= retrieve(query, top_k)
    context=build_context(result)
    user_message=f"Context : {context}\n\nQuery : {query}"
    response=groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[
        {"role" : "system", "content" : "SYSTEM_PROMPT"},
        {"role" : "user", "content" : user_message},
        ],
        temperature=0.2,      
    )
    return response.choices[0].message.content, context

def main():
    global embedder,collection_name,client,groq_client
    groq_client=Groq(api_key=os.getenv("GROQ_API_KEY"))
    URL = "https://github.com/sdutta24/RAG-Demo/raw/main/Demo_HC/TechCorp_HR_Policies.pdf"
    EMBEDDING_MODEL="all-MiniLM-L6-v2"
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    collection_name='docs'
    DIM=embedder.get_embedding_dimension()
    query=input("\nAsk a question : ")
    document = load_document(URL)
    #markdown_doc = document.export_to_markdown()
    #print(markdown_doc)
    doc_chunks = create_chunk(document)
    chunks = [convert_chunk(c) for c in doc_chunks]
    chunk_text_for_embedding = [c['chunk_text'] for c in chunks]
    embeddings=embedder.encode(chunk_text_for_embedding, show_progress_bar=True)
    client=qdrant_client('localhost',6333)
    create_collection(client,collection_name,DIM)
    points=create_points(chunks,embeddings)
    store_points=client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )
    results=retrieve(query,top_k=5)
    answer,context=rag(query,top_k=3)
    print(f"LLM Answer : {answer}")
    print(f"Source : {context}")
    #for chunk in chunks:
        #print(f"heading : {chunk['heading']}")
        #print(f"content : {chunk['content'][:200]}...")
        #print(f"chunk_text : {chunk['chunk_text']}")
    #sample = doc_chunks[3]
    #print(f"Doc Chunks : {len(doc_chunks)}")
    #print(f"Heading : {sample.meta.headings}")
    #print(f"Content : {sample.text[:200]}...")


if __name__ == "__main__":
    main()




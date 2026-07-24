import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_docling import DoclingLoader 
from langchain_docling.loader import ExportType
from docling_core.transforms.chunker import HierarchicalChunker
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


load_dotenv(Path(__file__).with_name(".env"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
URL = "https://github.com/sdutta24/RAG-Demo/raw/main/Demo_HC/TechCorp_HR_Policies.pdf"
#creation of langchain chat-model object and store it in llm variable
#it is only configuring groq language model not calling Groq. it is creating a model client.
#ChatGroq is Langchain's wrapper around the Groq API
llm=ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)

documents=DoclingLoader(
    file_path=URL,
    export_type=ExportType.DOC_CHUNKS,
    chunker=HierarchicalChunker(),
).load()
print(f"Total number of chunks: {len(documents)}")
print(type(documents))
#print(documents[1])
for i, doc in enumerate(documents,1):
    print(f"Chunk {i} : {doc}")
EMBED_MODEL_ID="sentence-transformers/all-MiniLM-L6-v2"
embeddings=HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
vectorstore=QdrantVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    path="/tmp/qdrant_storage",
    collection_name="hr_docs"

)
retriever=vectorstore.as_retriever(
    search_kwargs={"k": 5}
)
RAG_PROMPT=ChatPromptTemplate.from_messages([
    ("system","Answer using ONLY the context below. Cite section names. Say 'I don't know' if unsure."),
    ("human","Context: {context}\n\nQuestion: {question}")
]
)
def format_docs(documents):
    parts=[]
    for i,doc in enumerate(documents,1):
        dl_meta=doc.metadata.get("dl_meta",{})
        heading=dl_meta.get("headings",[])
        source=">".join(heading) if heading else "Unknown"
        parts.append(f"[{i}] {source}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)

def rag(query):
    docs = retriever.invoke(query)
    context= format_docs(docs)
    prompt_value=RAG_PROMPT.invoke({"context":context,"question":query})
    response=llm.invoke(prompt_value)
    return response.content

for q in [ "How many casual leaves am I entitled to?",
        "What is the notice period for Band 4 employees?",
        "How long is the probation period?",]:
    print(f"\nQ : {q}\n\n A : {rag(q)}\n")

vectorstore.client.close()
    




# Hierarchical Chunking RAG — Two Approaches

A Document QA RAG pipeline built with hierarchical chunking — implemented **two ways**:

1. **Raw Python** — every step wired manually, full visibility
2. **LangChain** — same pipeline using LangChain abstractions, fewer lines

Both produce the same result. The raw version teaches you what's happening. The LangChain version shows you how to build it cleanly for production.

---

## The Problem

Large documents like HR policies are hard to search through manually. Word-level chunking loses context. This pipeline uses **hierarchical chunking** — splitting the document along its heading structure so each chunk carries a breadcrumb like:

```
TechCorp HR Policies > Leave Policy > Casual Leave
```

That breadcrumb travels with the vector into Qdrant, so the LLM always knows the structural context of the content it's citing.

---

## Two Implementations

### Implementation 1 — Raw Python (`rag_hierarchical.py`)

Every step is explicit:

```
DocumentConverter → HierarchicalChunker → SentenceTransformer
→ QdrantClient → Groq API → Answer
```

Good for: learning, debugging, full control over each step.

### Implementation 2 — LangChain (`rag_langchain.py`)

Same pipeline using LangChain abstractions:

```
DoclingLoader → HuggingFaceEmbeddings → QdrantVectorStore
→ ChatGroq → ChatPromptTemplate → Answer
```

Good for: cleaner code, easier to swap components, production maintainability.

---

## Side-by-Side Comparison

| Step | Raw Python | LangChain |
|---|---|---|
| Load + Chunk | `DocumentConverter` + `HierarchicalChunker` (manual) | `DoclingLoader` (one call) |
| Embed | `SentenceTransformer.encode()` | `HuggingFaceEmbeddings` |
| Store | `QdrantClient.upsert()` | `QdrantVectorStore.from_documents()` |
| Retrieve | `client.query_points()` | `vectorstore.as_retriever()` |
| Prompt | Manual f-string | `ChatPromptTemplate` |
| Generate | `groq.chat.completions.create()` | `llm.invoke(prompt_value)` |

---

## Tech Stack

| Component | Tool |
|---|---|
| Document parsing | Docling |
| Chunking | HierarchicalChunker (Docling) |
| Embeddings | `all-MiniLM-L6-v2` (SentenceTransformers / HuggingFace) |
| Vector DB | Qdrant |
| LLM | Llama3 via Groq API |
| Orchestration | LangChain (Implementation 2 only) |
| Language | Python 3.10+ |

---

## Project Structure

```
Demo_HC/
│
├── rag_hierarchical.py          # Raw Python implementation
├── rag_langchain.py             # LangChain implementation
├── TechCorp_HR_Policies.pdf     # Sample document
├── requirements.txt
└── .env                         # API keys (not committed)
```

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for Qdrant — raw Python version only)
- Groq API key — free at [console.groq.com](https://console.groq.com)

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/sdutta24/RAG-Demo.git
cd RAG-Demo/Demo_HC
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
```

### 4. Start Qdrant (raw Python version only)

```bash
docker-compose up -d
```

### 5. Run

**Raw Python:**
```bash
python rag_hierarchical.py
```

**LangChain:**
```bash
python rag_langchain.py
```

---

## Example

**Question:** `What is the notice period for Band 4 employees?`

**Answer:**
```
According to the "Separation & Exit > Resignation Process" section,
the notice period for employees in Band 4 and above is 60 days.
```

---

## Chunking Strategy

Both implementations use **hierarchical chunking** via Docling's `HierarchicalChunker`.

Each chunk is split along the document's heading structure:

```
H1: TechCorp HR Policies
  H2: Leave Policy
    H3: Casual Leave → chunk with breadcrumb "TechCorp HR Policies > Leave Policy > Casual Leave"
    H3: Sick Leave   → chunk with breadcrumb "TechCorp HR Policies > Leave Policy > Sick Leave"
  H2: Separation & Exit
    H3: Resignation Process → chunk with breadcrumb "... > Separation & Exit > Resignation Process"
```

This is significantly better than word-level or fixed-size chunking because:
- Each chunk maps to one coherent section
- The breadcrumb gives the LLM structural context for citations
- Retrieval is section-aware — a question about leave returns leave sections, not random sentences


## Production Roadmap

- [ ] Incremental ingestion — hash-based upsert, only re-index changed documents
- [ ] Re-ranking — cross-encoder after retrieval to improve precision
- [ ] Hybrid chunking — sentence-level windows within each hierarchical section
- [ ] Metadata filtering — filter by section before semantic search
- [ ] LLM abstraction layer — swap Groq for AWS Bedrock with a config change
- [ ] Streaming responses — return answer tokens as they generate
- [ ] Evaluation layer — RAGAS or similar to measure retrieval and answer quality

---


This is a Readme file

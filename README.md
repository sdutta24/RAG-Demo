# document-qa-rag

A proof-of-concept RAG pipeline that answers plain English questions from a document — with source citations. Built entirely with a local/lightweight stack. No OpenAI. Minimal cost.

---

## The Problem

Large documents like HR policies, compliance manuals, or contracts are hard to search through manually. This pipeline lets you ask a plain English question and get a direct answer back — with the source section cited.

---

## How It Works

The pipeline has two phases:

**Ingestion (done once)**
Load the document → clean and split into chunks → embed each chunk → store in Qdrant

**Query (every time)**
User asks a question → embed the question → semantic search against stored chunks → top 3 chunks passed as context to LLM → answer returned with citation

---

## Tech Stack

| Component | Tool |
|---|---|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Vector DB | Qdrant (Docker) |
| LLM | Llama3 via Groq API |
| Language | Python 3.10+ |
| Infra | Docker Compose |

---

## Project Structure

```
document-qa-rag/
│
├── main.py                              # Entry point — full pipeline
├── techcorp_leave_attendance_policies.txt  # Sample document
├── docker-compose.yml                   # Qdrant vector DB
├── requirements.txt
└── .env                                 # API keys (not committed)
```

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Groq API key — free at [console.groq.com](https://console.groq.com)

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/sdutta24/AI_Demo.git
cd AI_Demo
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
```

### 4. Start Qdrant

```bash
docker-compose up -d
```

### 5. Run the pipeline

```bash
python main.py
```

You will be prompted to ask a question:

```
Ask a Question: What is the casual leave entitlement per year?
```

The pipeline will print the top 3 retrieved chunks with similarity scores, then return a cited answer.

---

## Example

**Input:**
```
Ask a Question: What is the casual leave entitlement per year?
```

**Output:**
```
[score = 0.8923]
Content: Every confirmed employee is entitled to 12 casual leaves per calendar year...

Answer:
According to the "Casual Leave" section, every confirmed employee is entitled to
12 casual leaves per calendar year, credited at the rate of 1 day per month.
```

---

## Changing the Document

To use a different document, update `GITHUB_RAW_URL` in `main.py`:

```python
GITHUB_RAW_URL = "https://raw.githubusercontent.com/your-username/your-repo/main/your-document.txt"
```

Then re-run `main.py` — the pipeline will re-ingest the new document automatically.

---

## Chunking Strategy

This POC uses **word-level chunking** — every 50 words becomes one chunk.

Simple and fast, but has known limitations — it can split sentences mid-way, losing context at chunk boundaries.

**Better strategies for production:**
- Sentence-level chunking
- Paragraph / section-level chunking
- Hierarchical chunking (document → section → paragraph)
- Semantic chunking (split where meaning shifts)

---

## Limitations (POC)

- Word-level chunking loses context at boundaries
- No re-ranking after retrieval
- No streaming — answer returns all at once
- Qdrant runs locally via Docker — needs managed cloud for production

---

## Roadmap

- [ ] Upgrade to section-level or semantic chunking
- [ ] Add LLM abstraction layer (swap Groq → AWS Bedrock easily)
- [ ] Add re-ranking step after retrieval
- [ ] Support multiple documents in one collection
- [ ] Add a simple web UI

---

## License

MIT

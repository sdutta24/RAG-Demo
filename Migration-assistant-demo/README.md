# Oracle → Snowflake Migration Intelligence Assistant

A **Retrieval-Augmented Generation (RAG)** application designed to help users explore Oracle-to-Snowflake migration knowledge using natural language.

The application retrieves relevant migration knowledge from PDF and JSON documents, constructs context, and generates answers using an LLM. Users can also inspect the retrieved source chunks behind each response.

## Project Overview

Oracle-to-Snowflake migration involves understanding migration rules, SQL conversions, platform capabilities, and technical best practices.

This project explores how a data-centric RAG pipeline can make migration knowledge more accessible, searchable, and actionable.

**Key objective:** Build a knowledge assistant that combines Data Engineering principles with Generative AI.

## Architecture

### 1. Knowledge Ingestion Pipeline

PDF / JSON Documents  
↓  
Parsing & Cleaning  
↓  
Chunking & Normalization  
↓  
Metadata Extraction  
↓  
Embedding Generation  
↓  
Domain Relevance Filtering  
↓  
PostgreSQL + pgvector

### 2. Query & Answer Pipeline

User Question (Streamlit UI)  
↓  
Query Embedding  
↓  
Vector Similarity Search (Top-K Retrieval)  
↓  
Context Builder  
↓  
Prompt Builder  
↓  
Groq LLM  
↓  
Generated Answer + Retrieved Sources

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| User Interface | Streamlit |
| Embedding Model | SentenceTransformers – `all-MiniLM-L6-v2` |
| Embedding Dimension | 384 |
| Vector Database | PostgreSQL + pgvector |
| LLM Inference | Groq |
| Input Sources | PDF, JSON |
| Environment | Local development |

## Key Features

- Ingest migration knowledge from PDF and JSON sources.
- Parse, clean, chunk, and normalize source content.
- Generate semantic embeddings.
- Apply similarity-based domain relevance filtering.
- Store chunks, metadata, and embeddings in PostgreSQL with pgvector.
- Retrieve relevant knowledge using vector similarity search.
- Construct context and generate LLM responses.
- Display retrieved source references in the Streamlit interface.

## Project Structure

```text
Prj1_Mig_Asst/
├── src/
│   ├── __init__.py
│   ├── ingest.py
│   ├── rag_pipeline.py
│   ├── streamlit_app.py
│   ├── ingestion.py
│   ├── cleaning.py
│   ├── embedding.py
│   ├── vector_store.py
│   ├── prompt_builder.py
│   └── llm.py
├── .env
├── pyproject.toml
├── uv.lock
└── README.md
```

*Note: Update this structure if your repository contains additional modules, data directories, tests, or configuration files.*

## Getting Started

### Prerequisites

- Python 3.10+ (use a version compatible with your dependencies)
- uv
- Docker
- PostgreSQL with pgvector
- Groq API key

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Prj1_Mig_Asst
```

### 2. Install Dependencies

```bash
uv sync
```

Ensure Streamlit, psycopg2-binary, sentence-transformers, pgvector-related dependencies, Groq SDK, and other required packages are declared in your project configuration.

### 3. Configure PostgreSQL

Start your PostgreSQL instance with the pgvector extension installed.

Create the application database and configure a dedicated database user.

Enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Create the knowledge table:

```sql
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT,
    content TEXT NOT NULL,
    source TEXT,
    source_type TEXT,
    metadata JSONB,
    embedding VECTOR(384)
);
```

Configure the database connection in your application.

**Security note:** Use environment variables for credentials. Do not commit database passwords.

### 4. Configure Environment Variables

Create the environment file at the location expected by your application.

Example:

```env
GROQ_API_KEY=your_groq_api_key
```

If your PostgreSQL connection settings are currently hardcoded, move them to environment variables before publishing the repository.

Never commit `.env`.

### 5. Prepare Knowledge Sources

Place your sample migration knowledge files in the locations expected by the ingestion module.

Supported source types in the current implementation:

- JSON migration rules
- PDF migration documentation

Use public, synthetic, or sanitized sample documents.

### 6. Run the Ingestion Pipeline

From the project root:

```bash
uv run python -m src.ingest
```

The ingestion workflow:

1. Loads source documents.
2. Parses and cleans the content.
3. Creates standardized chunks.
4. Generates embeddings.
5. Applies domain relevance filtering.
6. Stores selected chunks and embeddings in PostgreSQL.

Run ingestion whenever you want to populate or refresh your knowledge base.

### 7. Launch the Application

```bash
PYTHONPATH=. uv run streamlit run src/streamlit_app.py
```

Open the local URL displayed by Streamlit.

Ask migration questions and explore the retrieved source chunks.

## Example Use Cases

- How do I migrate Oracle NVL to Snowflake?
- How do I migrate Oracle sequences?
- What are the benefits of Snowflake migration?
- What migration rules are available for a particular SQL construct?

The quality of responses depends on the knowledge available in the indexed documents and the relevance of the retrieved context.

## Engineering Learnings

One key observation during development:

**Semantic similarity does not always equal answer relevance.**

For broad migration questions, a highly relevant document may rank below less relevant chunks.

This highlights several important engineering considerations:

- Chunking strategy and document structure
- Metadata-driven retrieval
- Similarity thresholds and retrieval ranking
- Context selection
- Grounded generation
- Evaluation of retrieval and answer quality

This project treats RAG as a Data Engineering problem as much as an LLM integration problem.

## Current Limitations

This is a working local prototype, not a production-ready migration platform.

Current areas for improvement:

- Retrieval evaluation using a representative question set
- Better ranking and relevance measurement
- Document versioning and stale chunk cleanup
- Improved ingestion validation and error handling
- Prompt injection and untrusted document safeguards
- Authentication, authorization, and observability
- Automated testing and deployment

Generated answers must be validated against authoritative migration documentation before being used for implementation decisions.

## Security & Responsible Use

- Do not commit API keys or database credentials.
- Avoid uploading confidential business, customer, or patient information.
- Retrieved content is passed to the configured LLM provider.
- Validate generated SQL and migration guidance before execution.
- Treat source documents as untrusted input.

## Future Enhancements

- Metadata-aware retrieval
- Retrieval evaluation and ranking improvements
- Support for Excel, DOCX, and additional knowledge sources
- Better source traceability
- Automated ingestion and refresh workflows
- Migration case studies and SQL conversion examples

## Project Status

**Working local prototype**

The ingestion pipeline, vector retrieval, LLM answer generation, and Streamlit application are implemented. Retrieval quality, evaluation, and production safeguards are ongoing improvement areas.

---

Built as a hands-on exploration of Data Engineering, RAG architecture, and Generative AI.


from .ingestion import (load_migration_rules, load_pdf_document)
from docling_core.transforms.chunker import HierarchicalChunker
def standardize_migration_format(rule,chunk_id):
    standard_format = {
        "chunk_id": chunk_id,
        "document_id": str(rule["id"]),
        "content": rule["rule"].strip(),
        "source": "migration_rules.json",
        "source_type": "json",
        "metadata": {
            "title": rule["title"].strip(),
            "source_db": rule["source_db"],
            "target_db": rule["target_db"],
            "artifact_type": rule["artifact_type"],
            "category": rule["category"],
            "complexity": rule["complexity"]
        }

    }
    return standard_format

def normalize_migration_rules(rules):
    normalize_rules = []
    for index,rule in enumerate(rules, start=1):
        chunk_id = f"migration_rules.json_{index:03d}"
        standard_format = standardize_migration_format(rule,chunk_id)
        normalize_rules.append(standard_format)
    return normalize_rules

def standardize_pdf_format(document,source):
    standard_pdf_format = {
        "document_id": source,
        "content": document.export_to_markdown(),
        "source": source,
        "source_type": "pdf",
        "metadata": {}
    }
    return standard_pdf_format

def create_chunks(document):
    chunker = HierarchicalChunker()
    chunks = list(chunker.chunk(document))
    return chunks

def clean_text(text):
    cleaned_text=text.replace("\x07","")
    cleaned_text=cleaned_text.strip()
    return cleaned_text

def is_page_number(text):
    return text.isdigit()

def clean_chunk(chunk_id,chunk):
    clean_text1 = clean_text(chunk.text)
    clean_heading = [clean_text(h) for h in chunk.meta.headings]
    if not clean_text1:
        return None
    if is_page_number(clean_text1):
        return None
    chunk_id= f"offering-oracle-to-snowflake-migration.pdf_{chunk_id:03d}"
    cleaned_chunk = {
        "chunk_id": chunk_id,
        "document_id": chunk.meta.origin.filename,
        "content": clean_text1,
        "source": chunk.meta.origin.filename,
        "source_type": "pdf",
        "metadata":{
            "title": "Oracle to Snowflake Migration",
            "headings": clean_heading,
            "page": chunk.meta.doc_items[0].prov[0].page_no    
        }
    }
    return cleaned_chunk

def is_noise(cleaned_chunk):
    content_cc = cleaned_chunk['content'].lower()
    if "all rights reserved" in content_cc:
        return True
    if "tel:" in content_cc and "email:" in content_cc:
        return True
    return False
                

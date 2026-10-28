import json
from pathlib import Path
from docling.document_converter import DocumentConverter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "migration_rules.json"

print(f"Loading migration rules from {DATA_FILE}")
def load_migration_rules():
    with open(DATA_FILE, "r") as f:
        rules = json.load(f)
    return rules

def load_pdf_document():
    converter = DocumentConverter()
    pdf_file = BASE_DIR / "data" / "offering-oracle-to-snowflake-migration.pdf"
    response = converter.convert(pdf_file)
    return response
def main():
    response = load_pdf_document()
    print(f"Response type: {type(response)}")
    print(f"Document type: {type(response.document)}")
    document = response.document
    markdown_text = document.export_to_markdown()
    print(f"Markdown text: {markdown_text[:3000]}")

if __name__ == "__main__":
    main()




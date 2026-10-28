from src.ingestion import (load_pdf_document,load_migration_rules)
from src.embedding import (load_embedding_model,
                           create_embeddings,
                           domain_embedding,
                           filter_by_similarity)
from src.cleaning import (create_chunks,
                          normalize_migration_rules,
                          standardize_pdf_format,
                          clean_chunk,
                          is_noise
                          

)
from src.vector_store import insert_chunks

def run_ingestion():
    print("Starting Ingestion.......")
    rules = load_migration_rules()
    response = load_pdf_document()
    document = response.document

#parse and clean PDF chunks
    chunks = create_chunks(document)
    cleaned_chunk=[clean_chunk(index,chunk) for index,chunk in enumerate(chunks,start=1)]
    cleaned_chunk = [cc for cc in cleaned_chunk if cc is not None]
    filtered_chunk = [fc for fc in cleaned_chunk if not is_noise(fc)]
#Standardize JSON rules
    json_chunks=normalize_migration_rules(rules)
#combine jason & PDF chunks
    all_chunks = json_chunks + filtered_chunk
#Generate embedding
    model = load_embedding_model()
    all_embeddings = create_embeddings(model,all_chunks)
#Filter chunks based on domain
    d_embedding = domain_embedding(model)
    selected_chunks = filter_by_similarity(all_chunks,all_embeddings,d_embedding,model,threshold=0.4)
#generate embedding for selected chunks
    selected_embeddings = create_embeddings(model,selected_chunks)
#Insert selected chunks into vector store
    insert_chunks(selected_chunks, selected_embeddings)

    print(f"Ingestion completed.")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Selected chunks: {len(selected_chunks)}")

if __name__ == "__main__":
    run_ingestion()



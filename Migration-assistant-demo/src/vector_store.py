import psycopg2
import json

def get_connection():
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="ragdb",
        user="raguser",
        password="ragpassword"
    )
    return connection
def insert_chunks(chunks,embeddings):
    connection = get_connection()
    cursor = connection.cursor()
    insert_query = """
        INSERT INTO knowledge_chunks (
            chunk_id,
            document_id,
            content,
            source,
            source_type,
            metadata,
            embedding
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (chunk_id)
        DO UPDATE SET
            document_id = EXCLUDED.document_id,
            content = EXCLUDED.content,
            source = EXCLUDED.source,
            source_type = EXCLUDED.source_type,
            metadata = EXCLUDED.metadata,
            embedding = EXCLUDED.embedding;
    """
    for chunk, embedding in zip(chunks, embeddings):
        cursor.execute(insert_query,
            (
                chunk["chunk_id"],
                chunk["document_id"],
                chunk["content"],
                chunk["source"],
                chunk["source_type"],
                json.dumps(chunk["metadata"]),
                embedding.tolist()
            )
            )
    connection.commit()
    cursor.close()
    connection.close()

def search_similar_chunks(query_embedding, top_k=5):
    connection = get_connection()
    cursor = connection.cursor()
    search_query = """
        SELECT
            chunk_id,
            content,
            metadata,
            source,
            source_type,
            1 - (embedding <=> %s::vector) AS similarity
        FROM knowledge_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """
    query_vector = query_embedding.tolist()
    cursor.execute(search_query,(query_vector,query_vector,top_k))
    rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append({
            "chunk_id": row[0],
            "content": row[1],
            "metadata": row[2],
            "source": row[3],
            "source_type": row[4],
            "similarity": float(row[5])
        })
    cursor.close()
    connection.close()
    return results

def build_context(results):
    context_result = []
    for result in results:
        context_result.append(
            f"""
Source: {result['source']}
Chunk ID: {result['chunk_id']}
Content: {result['content']}
"""
        )
    return "\n\n".join(context_result)
    
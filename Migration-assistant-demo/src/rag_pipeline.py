from src.embedding import query_embedding
from src.vector_store import (search_similar_chunks,build_context)
from src.prompt_builder import build_prompt
from src.llm import generate_answer
def answer_question(model,question):
    #create query embedding
    q_embd = query_embedding(model,question)
    #retrive top 5 chunks
    result = search_similar_chunks(q_embd,top_k=5)
    #keep top 3 result
    top_results = result
    #build context from top 3 result
    context_result = build_context(top_results)
    #build prompt
    prompt = build_prompt(context_result,question)
    #generate answer
    answer = generate_answer(prompt)
    return answer, top_results
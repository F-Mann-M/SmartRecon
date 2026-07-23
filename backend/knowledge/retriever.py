import ollama
from knowledge.vector_store import similarity_search

def answer_question_with_rag(user_query: str):
    # Retrieve chunks
    context_chunks = similarity_search(user_query, n_results=3)
    print(f"Chunk count: {len(context_chunks)}")

    # Combine chunk contents
    context_text = "\n\n---\n\n".join([content["content"][0] for content in context_chunks])
   
    # Construct prompt
    prompt = f"""Use the following context to answer the user's question.
    
            Context:
            {context_text}

            Question: {user_query}
            Answer:"""

    # Query local Gemma 4 model
    response = ollama.chat(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["message"]["content"]
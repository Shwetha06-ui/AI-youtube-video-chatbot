from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(api_key: str, temperature: float = 0.2):
    """
    Helper function to initialize ChatGoogleGenerativeAI with model fallback.
    """
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("A valid Google Gemini API Key is required.")
        
    models_to_try = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-pro",
        "models/gemini-1.5-pro",
        "gemini-2.0-flash"
    ]
    
    for model_name in models_to_try:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature
            )
            return llm
        except Exception:
            continue
            
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=temperature
    )

def generate_summary_and_key_points(transcript_text: str, api_key: str) -> tuple[str, list[str]]:
    """
    Generates a concise video summary and key bullet points using Gemini LLM.
    
    Args:
        transcript_text (str): Full video transcript.
        api_key (str): Gemini API Key.
        
    Returns:
        tuple[str, list[str]]: (summary_text, list_of_key_points)
    """
    if not transcript_text:
        return "No transcript text provided.", []
        
    llm = get_llm(api_key, temperature=0.3)
    
    # Truncate transcript to first ~12,000 characters if extremely long to stay within standard context limits
    sample_transcript = transcript_text[:12000]
    
    prompt = f"""You are an expert educational content analyzer.
Analyze the following YouTube video transcript and generate:
1. A concise overview/summary (2 to 3 paragraphs).
2. Exactly 5 to 7 key bullet point takeaways.

Transcript Context:
{sample_transcript}

Please structure your response EXACTLY as follows:
SUMMARY:
<Write summary here>

KEY POINTS:
- <Key point 1>
- <Key point 2>
- <Key point 3>
- <Key point 4>
- <Key point 5>
"""

    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        summary = ""
        key_points = []
        
        if "SUMMARY:" in content and "KEY POINTS:" in content:
            parts = content.split("KEY POINTS:")
            summary = parts[0].replace("SUMMARY:", "").strip()
            raw_points = parts[1].strip().split("\n")
            key_points = [p.lstrip("-* ").strip() for p in raw_points if p.strip()]
        else:
            summary = content.strip()
            key_points = ["Refer to the video transcript summary above."]
            
        return summary, key_points

    except Exception as e:
        return f"Could not generate summary: {str(e)}", ["Summary unavailable."]

def answer_question(vector_store, question: str, chat_history: list, api_key: str) -> tuple[str, list[str]]:
    """
    Performs similarity search on FAISS vector store and generates an answer strictly
    grounded in the retrieved transcript context.
    
    Args:
        vector_store (FAISS): FAISS vector store instance.
        question (str): User question.
        chat_history (list[dict]): List of past conversation turns.
        api_key (str): Google Gemini API Key.
        
    Returns:
        tuple[str, list[str]]: (answer_text, list_of_retrieved_source_chunks)
    """
    if not vector_store:
        raise ValueError("Vector store is not initialized. Please process a video first.")
        
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")
        
    # Similarity search: Retrieve top 4 most relevant transcript chunks
    docs = vector_store.similarity_search(question.strip(), k=4)
    source_chunks = [doc.page_content for doc in docs]
    
    # Format retrieved context
    context = "\n\n---\n\n".join(source_chunks)
    
    # Format recent chat history (up to last 4 messages)
    formatted_history = ""
    if chat_history:
        recent = chat_history[-4:]
        formatted_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent])
        
    prompt = f"""You are an AI assistant helping users understand YouTube videos based strictly on their transcripts.

Context from Video Transcript:
{context}

Recent Conversation History:
{formatted_history}

User Question: {question}

STRICT INSTRUCTIONS:
1. Answer the question based ONLY on the video transcript context provided above.
2. If the answer cannot be found in or directly inferred from the transcript context, respond with EXACTLY:
   "The requested information is not available in the video transcript."
3. Do NOT invent, assume, or bring in outside knowledge not mentioned in the transcript.
4. Keep your answer clear, accurate, and easy to understand.

Answer:"""

    llm = get_llm(api_key, temperature=0.1)
    
    try:
        response = llm.invoke(prompt)
        answer_text = response.content if hasattr(response, 'content') else str(response)
        return answer_text.strip(), source_chunks
    except Exception as e:
        raise Exception(f"Failed to generate answer from Gemini: {str(e)}")

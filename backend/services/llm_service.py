from config import llm
from typing import List, AsyncIterator

async def summarize(text: str) -> str:
    prompt   = f"Summarize the following content in exactly 3 concise bullet points:\n\n{text[:4000]}"
    response = await llm.ainvoke(prompt)
    return response.content

async def answer_question(context_chunks: List[str], question: str) -> str:
    context  = "\n\n".join(context_chunks)
    prompt   = (
        f"You are a helpful assistant. Use the context below to answer the question.\n\n"
        f"Context:\n{context[:4000]}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    response = await llm.ainvoke(prompt)
    return response.content

async def stream_answer(context_chunks: List[str], question: str) -> AsyncIterator[str]:
    context = "\n\n".join(context_chunks)
    prompt  = (
        f"You are a helpful assistant. Use the context below to answer the question.\n\n"
        f"Context:\n{context[:4000]}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    async for chunk in llm.astream(prompt):
        yield chunk.content

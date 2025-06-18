from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
import numpy as np
import requests
import re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

token = os.getenv("AI_PIPE_TOKEN")

chat_url = "https://aipipe.org/openai/v1/chat/completions"
embed_url = "https://aipipe.org/openai/v1/embeddings"
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

data = np.load("embeddingsss.npz", allow_pickle=True)
chunks = data["chunks"]
embeddings = data["embeddings"]
chunk_data = [
    {"chunk": chunk, "embedding": embedding}
    for chunk, embedding in zip(chunks, embeddings)
]

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(a_norm, b_norm.T)

def get_question_embedding(text: str, model="text-embedding-3-small") -> list:
    data = {"model": model, "input": text}
    response = requests.post(embed_url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Embedding failed: {response.text}")
    return response.json()["data"][0]["embedding"]

def match_question_embedding(question_embedding: list, chunk_data: list, top_k: int = 3):
    query_emb = np.array(question_embedding).reshape(1, -1)
    stored_embeddings = np.array([np.array(item["embedding"]) for item in chunk_data])
    similarities = cosine_similarity(query_emb, stored_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [chunk_data[i]["chunk"] for i in top_indices]

def generate_answer_from_chunks(query: str, context_chunks: List[str]) -> str:
    context_text = "\n\n".join(context_chunks)
    print(context_chunks)
    prompt = (
        f"{query} - Answer ONLY from these notes with utmost accuracy. Cite verbatim from notes if possible.\n\n{context_text}"
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant answering only from provided documentation. You respond with I don't know if you do not know the answer to the question, but before doing so check context again to be sure that you really do not know"},
        {"role": "user", "content": prompt}
    ]
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 512
    }
    response = requests.post(chat_url, headers=headers, json=payload, timeout=30.0)
    if response.status_code != 200:
        raise Exception(f"Chat failed: {response.text}")
    return response.json()["choices"][0]["message"]["content"].strip()

def extract_chunk_info(chunks):
    result = []
    for chunk in chunks:
        chunk_str = str(chunk)
        entry = {"text": "", "url": ""}

        post_url_match = re.search(r"\[Post URL\]\((.*?)\)", chunk_str)
        if post_url_match:
            entry["url"] = post_url_match.group(1)
            entry["text"] = chunk_str.replace("\n", " ").split("[Post URL]")[0].strip()

        result.append(entry)
    return result

@app.post("/api/", response_model=AnswerResponse)
async def receive_question(data: RequestData):
    question = data.question
    image_data = data.image
    print(question)
    print(image_data)
    context = ""

    if image_data:
        image_payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        }
        response = httpx.post(chat_url, headers=headers, json=image_payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Image description failed: {response.text}")
        img_description = response.json()["choices"][0]["message"]["content"]
        context += f"Image Description: {img_description}\n"
        print(context)

    full_query = context + question
    question_embedding = get_question_embedding(full_query)
    top_chunks = match_question_embedding(question_embedding, chunk_data, top_k=3)
    answer = generate_answer_from_chunks(full_query, top_chunks)
    print(answer)
    links = extract_chunk_info(top_chunks)
    return AnswerResponse(answer=answer, links=links)

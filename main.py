from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import requests
import re
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
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

url = "https://aipipe.org/openai/v1/chat/completions"
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

data = np.load("embeddings.npz", allow_pickle=True)

chunks = data["chunks"]
embeddings = data["embeddings"]
chunk_data = [
    {"chunk": chunk, "embedding": embedding}
    for chunk, embedding in zip(chunks, embeddings)
]

def get_question_embedding(text: str, model="text-embedding-3-small") -> list:
    url = "https://aipipe.org/openai/v1/embeddings"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    data = {
            "model": model,
            "input": text
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Embedding failed: {response.text}")
    resp_json = response.json()
    return resp_json["data"][0]["embedding"]

def match_question_embedding(question_embedding: list, chunk_data: list, top_k: int = 3):
    query_emb = np.array(question_embedding).reshape(1, -1)
    stored_embeddings = np.array([np.array(item["embedding"]) for item in chunk_data])
    similarities = cosine_similarity(query_emb, stored_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [chunk_data[i]["chunk"] for i in top_indices]

def generate_answer_from_chunks(query: str, context_chunks: List[str]) -> str:
    context_text = "\n\n".join(context_chunks)
    prompt = (
        f"{query} - Answer ONLY from these notes. Cite verbatim from notes if possible.\n\n{context_text}"
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant answering only from provided documentation. You respond with I don't know if you do not know the answer to the question"},
        {"role": "user", "content": prompt}
    ]
    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 512
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    if response.status_code != 200:
        raise Exception(f"Chat failed with status {response.status_code}: {response.text}")
    return response.json()["choices"][0]["message"]["content"].strip()

def extract_chunk_info(chunks, sidebar_path):
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        sidebar_content = f.read()

    result = []
    url_base = "https://tds.s-anand.net/#/"

    for chunk in chunks:
        chunk_str = str(chunk)
        entry = {"text": "", "url": ""}

        # Case 1: [Post URL](...)
        post_url_match = re.search(r"\[Post URL\]\((.*?)\)", chunk_str)
        if post_url_match:
            entry["url"] = post_url_match.group(1)
            entry["text"] = chunk_str.replace("\n", " ").split("[Post URL]")[0].strip()

        else:
            # Case 2: Markdown heading like ## Containers: Docker, Podman
            heading_match = re.search(r"^##\s+(.+)", chunk_str)
            if heading_match:
                heading_text = heading_match.group(1).strip()
                # Search sidebar for [Heading Text](somefile.md)
                pattern = re.escape(f"[{heading_text}]") + r"\(([^)]+\.md)\)"
                sidebar_match = re.search(pattern, sidebar_content)
                if sidebar_match:
                    md_file = sidebar_match.group(1).strip()
                    url_path = md_file.replace(".md", "")
                    entry["url"] = f"{url_base}{url_path}"
            entry["text"] = chunk_str.replace("\n", " ").strip()

        result.append(entry)

    return result

sidebar_path = "_sidebar.md"

@app.post("/api/", response_model=AnswerResponse)
async def receive_question(data: RequestData):
    question = data.question
    image_data = data.image
    context=""
    print("Checking token", token)
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
        response = httpx.post(url, headers=headers, json=image_payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Image description failed: {response.text}")
        
        img_description = response.json()["choices"][0]["message"]["content"]
        context += f"Image Description: {img_description}\n"
    
    full_query = context + question
    question_embedding = get_question_embedding(full_query, model="text-embedding-3-small")
    top_k_chunks = match_question_embedding(question_embedding=question_embedding, chunk_data=chunk_data, top_k=3)
    answer = generate_answer_from_chunks(full_query, top_k_chunks)
    print(top_k_chunks)
    output = extract_chunk_info(top_k_chunks, sidebar_path)
    return AnswerResponse(
        answer=answer,
        links= output
    )

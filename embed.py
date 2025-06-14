import os
import re
import requests
import numpy as np
from pathlib import Path
from tqdm import tqdm
from semantic_text_splitter import MarkdownSplitter

def get_chunks(file_path: str, chunk_size: int = 1000):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    splitter = MarkdownSplitter(chunk_size)
    chunks = splitter.chunks(content)
    return chunks

def get_embedding(text: str, model="text-embedding-3-small") -> list:
    url = "https://aipipe.org/openai/v1/embeddings"
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjEwMDAyNDJAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.3vmzvsqUwc07G3-vsltLc2I5GiKrzp-3OFG8yEwMauY",
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
    print(resp_json["data"][0]["embedding"])
    return resp_json["data"][0]["embedding"]

markdown_dir = Path(r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\markdowns")
files = [*markdown_dir.glob("*.md"), *markdown_dir.rglob("*.md")]
all_chunks = []
all_embeddings = []
total_chunks = 0
file_chunks = {}

for file_path in files:
    chunks = get_chunks(file_path)
    file_chunks[file_path] = chunks
    total_chunks += len(chunks)

with tqdm(total=total_chunks, desc="Processing embeddings") as pbar:
    for file_path, chunks in file_chunks.items():
        for chunk in chunks:
            try:
                embedding = get_embedding(chunk)
                all_chunks.append(chunk)
                all_embeddings.append(embedding)
                pbar.set_postfix({"file": file_path.name, "chunks": len(all_chunks)})
                pbar.update(1)
            except Exception as e:
                print(f"Skipping chunk from {file_path.name} due to error: {e}")
                pbar.update(1)
                continue

np.savez_compressed("embeddings.npz", chunks=all_chunks, embeddings=all_embeddings)


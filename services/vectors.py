import os
import json
import numpy as np
import aiofiles
from filelock import FileLock
import tiktoken

CHUNK_SIZE=600
CHUNK_OVERLAP=120

# Cosine similarity (common in NLP)
def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

# Euclidean distance (common for spatial vectors)
def euclidean_distance(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.linalg.norm(v1 - v2))

# Main vector DB search
async def ai_search(query_embedding):
    db_path = os.getenv("DB_PATH")
    lock_path = db_path + ".lock"
    lock = FileLock(lock_path)

    with lock:  # Ensure read is safe while another process might be writing
        async with aiofiles.open(db_path, "r", encoding="utf-8") as f:
            db = json.loads(await f.read())

    scored = []
    for record in db:
        embedding = record["embedding"]
        score = cosine_similarity(query_embedding, embedding)
        if score < 0.2:
            continue
        scored.append({
            "article": record["article"],
            "score": score
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:5]

def chunk_text_by_tokens(text):
    enc = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks
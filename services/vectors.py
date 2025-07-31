import os
import json
import numpy as np
import aiofiles

# Most NLP embeddings
def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
# Non-normalized, spatial data
def euclidean_distance(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.linalg.norm(v1 - v2))

async def ai_search(query_embedding):
    # Get Vector DB
    db_path = os.getenv("DB_PATH")
    async with aiofiles.open(db_path, "r", encoding="utf-8") as f:
        db = json.loads(await f.read())
    scored = []
    for record in db:
        embedding = record["embedding"]
        score = cosine_similarity(query_embedding, embedding)
        # Delete low score results (remove trashhold)
        if score < 0.2:
            continue
        scored.append({
            "article": record["article"],
            "score": score
        })
    # Sort by score and return top 3
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]

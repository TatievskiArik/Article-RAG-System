import os
import json
import numpy as np

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

def ai_search(query_embedding):
    db_path = os.getenv("DB_PATH")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
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
    return scored[:3]

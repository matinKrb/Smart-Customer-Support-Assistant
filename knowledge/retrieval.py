import numpy as np
from .models import KnowledgeItem
from .embedding_model import embed_text

MIN_SIMILARITY_THRESHOLD = 0.1


def cosine_similarity(a: list, b: list) -> float:
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_knowledge(query: str, top_k: int = 3) -> list:
    query_embedding = embed_text(query)
    items = KnowledgeItem.objects.filter(is_active=True)

    scored_items = []
    for item in items:
        score = cosine_similarity(query_embedding, item.embedding)
        scored_items.append((score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, item in scored_items[:top_k]:
        if score >= MIN_SIMILARITY_THRESHOLD:
            results.append({
                "title": item.title,
                "content": item.content,
                "score": round(float(score), 3),
            })

    if not results:
        return [{"message": "هیچ اطلاعات مرتبطی در پایگاه دانش یافت نشد."}]

    return results

import difflib
from typing import List

from fastapi import Depends

from core.infrastructure.clients.mongodb import get_history_collection

# from sentence_transformers import SentenceTransformer

HISTORY_COLL = "history"
# model = SentenceTransformer('all-MiniLM-L6-v2')

async def texts_for(uid: int, mongo_db) -> List[str]:
    """Возвращает список всех текстов, ранее сгенерированных пользователем."""
    doc = await mongo_db.find_one({"_id": uid})
    texts = doc.get("texts", []) if doc else []
    return texts if isinstance(texts, list) else []

async def remember_text(uid: int, text: str, max_items: int = 10_000) -> None:
    """
    Добавляет текст в историю пользователя, если его там ещё нет.
    Хранит не более max_items уникальных записей для пользователя.
    """
    col = db[HISTORY_COLL]
    doc = await col.find_one({"_id": uid})
    if not doc:
        await col.insert_one({"_id": uid, "texts": [text]})
        return

    texts = doc.get("texts", [])
    if text in texts:
        return

    texts.append(text)
    if len(texts) > max_items:
        texts = texts[-max_items:]
    await col.update_one({"_id": uid}, {"$set": {"texts": texts}})

# async def remember_text_with_embedding(uid: int, text: str, max_items: int = 10_000):
#     """
#     Сохраняет текст и его эмбеддинг, если такого ещё нет у пользователя.
#     """
#     col = db[HISTORY_COLL]
#     doc = await col.find_one({"_id": uid})
#
#     emb = model.encode(text, convert_to_numpy=True).tolist()
#
#     if not doc:
#         await col.insert_one({"_id": uid, "texts": [{"text": text, "embedding": emb}]})
#         return
#
#     texts = doc.get("texts", [])
#     if any(t["text"] == text for t in texts):
#         return
#
#     texts.append({"text": text, "embedding": emb})
#     if len(texts) > max_items:
#         texts = texts[-max_items:]
#     await col.update_one({"_id": uid}, {"$set": {"texts": texts}})


# async def text_is_semantically_similar_annoy(uid: int, new_text: str, threshold: float = 0.8) -> bool:
#     """
#     Проверяет, похож ли новый текст по смыслу на любой из сохранённых у пользователя.
#     Использует сохранённые эмбеддинги + Annoy.
#     """
#     doc = await db[HISTORY_COLL].find_one({"_id": uid})
#     if not doc or not doc.get("texts"):
#         return False
#
#     texts_data = doc["texts"]
#     embeddings = [t["embedding"] for t in texts_data if "embedding" in t]
#     if not embeddings:
#         return False
#
#     dim = len(embeddings[0])
#     annoy_index = AnnoyIndex(dim, "angular")
#     for idx, emb in enumerate(embeddings):
#         annoy_index.add_item(idx, emb)
#     annoy_index.build(10)
#
#     # Новый эмбеддинг
#     new_emb = model.encode(new_text, convert_to_numpy=True)
#
#     # Получаем индекс самого похожего и расстояние
#     idxs, dists = annoy_index.get_nns_by_vector(new_emb, 1, include_distances=True)
#     if dists:
#         angular_dist = dists[0]
#         cos_sim = 1 - (angular_dist ** 2) / 2
#     else:
#         cos_sim = 0.0

    # return cos_sim >= threshold

async def text_is_semantically_similar(uid: int, new_text: str, threshold: float = 0.75) -> bool:
    """
    Проверяет, есть ли среди сохранённых пользователем текстов текст, похожий на new_text.
    """
    mongo_db = Depends(get_history_collection)
    for old in await texts_for(uid, mongo_db):
        if difflib.SequenceMatcher(None, new_text, old).ratio() >= threshold:
            return True
    return False

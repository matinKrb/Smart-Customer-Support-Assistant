import os
os.environ['HF_HUB_OFFLINE'] = '1'

from sentence_transformers import SentenceTransformer

_model = None

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str) -> list:
    model = get_model()
    vector = model.encode(text)
    return vector.tolist()

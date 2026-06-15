import os
import hashlib
import json
from app.config import UPLOAD_DIR

CACHE_FILE = os.path.join(os.path.dirname(UPLOAD_DIR), ".vqa_cache.json")

def _hash_key(question: str, image_id: str) -> str:
    key_str = f"{question.strip().lower()}:{image_id.strip()}"
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

def get_cached_answer(question: str, image_id: str) -> str | None:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        key = _hash_key(question, image_id)
        return cache.get(key)
    except Exception as e:
        print(f"Error reading VQA cache: {e}")
        return None

def store_cached_answer(question: str, image_id: str, answer: str):
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
        except Exception as e:
            print(f"Error reading VQA cache for write: {e}")
    try:
        key = _hash_key(question, image_id)
        cache[key] = answer
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        print(f"Error writing to VQA cache: {e}")

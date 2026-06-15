import os
import easyocr
import uuid
import numpy as np
from datetime import datetime
from PIL import Image
from app.embedding.clip_embedder import embed_image, classify_image_category
from app.database import db

# Singleton reader instance
_ocr_reader = None

def get_ocr_reader() -> easyocr.Reader:
    global _ocr_reader
    if _ocr_reader is None:
        # Load English reader on CPU for maximum compatibility
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _ocr_reader

def extract_image_text(file_path: str) -> dict:
    """
    Extracts text from an image file (.png, .jpg, .jpeg) using EasyOCR.
    
    Args:
        file_path (str): The physical path of the image file.
        
    Returns:
        dict: A dictionary containing:
            - "text": The combined text extracted from the image.
            - "confidence": The average confidence score of the extracted text detections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
        
    try:
        reader = get_ocr_reader()
        results = reader.readtext(file_path)
        
        if not results:
            return {
                "text": "",
                "confidence": 0.0
            }
            
        texts = []
        confidences = []
        
        for bbox, text, conf in results:
            clean_text = text.strip()
            if clean_text:
                texts.append(clean_text)
                confidences.append(float(conf))
                
        if not texts:
            return {
                "text": "",
                "confidence": 0.0
            }
            
        full_text = " ".join(texts)
        avg_conf = sum(confidences) / len(confidences)
        
        return {
            "text": full_text,
            "confidence": avg_conf
        }
    except Exception as e:
        print(f"Error during EasyOCR extraction: {e}")
        raise e

def check_if_blank(image_path: str, threshold: float = 1.0) -> bool:
    """
    Returns True if the image is nearly blank/solid color (low pixel variance).
    """
    try:
        img = Image.open(image_path).convert("L")
        var = float(np.var(np.array(img)))
        return var < threshold
    except Exception as e:
        print(f"Error checking blank image: {e}")
        return False

def process_clip_image(file_path: str, filename: str, ocr_confidence: float) -> dict:
    """
    Generates a CLIP visual embedding for the image and indexes it in ChromaDB image_collection.
    
    Args:
        file_path (str): The physical path of the image file.
        filename (str): The name of the file.
        ocr_confidence (float): The OCR confidence score to store in metadata.
        
    Returns:
        dict: A status dictionary containing:
            - "status": "success" or "error"
            - "clip_id": The generated unique ID of the clip document (if successful)
            - "message": An error message (if failed)
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
            
        # 1. Blank image check
        is_blank = check_if_blank(file_path)
        
        # 2. Category auto-classification via Zero-Shot CLIP
        visual_category = classify_image_category(file_path)
        
        # 3. Generate descriptive caption via VLM (LLaVA) if not blank
        if is_blank:
            caption = "Blank image."
        else:
            try:
                from app.llm.vision_client import generate_image_caption
                caption = generate_image_caption(file_path)
            except Exception as e:
                print(f"Error generating caption: {e}")
                caption = "A visual document."
        
        # 4. Compute visual embedding
        embedding = embed_image(file_path)
        
        # 5. Generate unique clip ID
        clip_id = f"clip_{uuid.uuid4().hex}"
        
        # 6. Measure dimensions
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except Exception:
            width, height = 0, 0
            
        # Build enriched metadata dictionary with timestamp
        metadata = {
            "source": filename,
            "source_type": "image",
            "ocr_confidence": ocr_confidence,
            "file_path": os.path.abspath(file_path),
            "ingested_at": datetime.utcnow().isoformat(),
            "image_width": width,
            "image_height": height,
            "is_blank": is_blank,
            "visual_category": visual_category,
            "caption": caption
        }
        
        # Persist in database
        db.add_image_document(id=clip_id, embedding=embedding, metadata=metadata)
        
        return {
            "status": "success",
            "clip_id": clip_id,
            "is_blank": is_blank,
            "visual_category": visual_category,
            "caption": caption
        }
    except Exception as e:
        print(f"Error during CLIP visual indexing: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


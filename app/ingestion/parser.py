import os
import uuid
from app.database import db
from app.ingestion.pdf_handler import extract_pdf
from app.ingestion.docx_handler import extract_docx_text
from app.ingestion.audio_handler import transcribe_audio, merge_transcript_segments
from app.ingestion.image_handler import extract_image_text, process_clip_image
from app.utils.chunker import chunk_text

def ingest_file(file_path: str, filename: str) -> dict:
    """
    Ingests a file based on extension. In Milestone 1, this only processes PDFs.
    
    Args:
        file_path (str): The physical path on disk.
        filename (str): The logical name of the file.
        
    Returns:
        dict: Ingestion status and summary statistics.
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        return ingest_pdf(file_path, filename)
    elif ext == ".docx":
        return ingest_docx(file_path, filename)
    elif ext in [".wav", ".mp3", ".m4a"]:
        return ingest_audio(file_path, filename)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return ingest_image(file_path, filename)
    elif ext == ".csv":
        return ingest_csv(file_path, filename)
    elif ext in [".md", ".txt"]:
        return ingest_markdown(file_path, filename)
    elif ext == ".json":
        return ingest_json(file_path, filename)
    else:
        return {
            "status": "warning",
            "message": f"Unsupported format: {ext}."
        }

def ingest_pdf(file_path: str, filename: str) -> dict:
    """
    Orchestrates PDF text extraction, chunking, and database storage.
    """
    try:
        # 1. Extract text page-by-page
        pages = extract_pdf(file_path)
        if not pages:
            return {"status": "warning", "message": f"No text extracted from PDF: {filename}"}
            
        ids = []
        documents = []
        metadatas = []
        
        # 2. Chunk text and prepare database entries
        for p in pages:
            page_num = p["page"]
            page_text = p["text"]
            
            chunks = chunk_text(page_text)
            for idx, chunk in enumerate(chunks):
                chunk_id = f"pdf_{uuid.uuid4().hex}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "source": filename,
                    "page": page_num,
                    "chunk_index": idx,
                    "source_type": "pdf"
                })
                
        # 3. Add to persistent ChromaDB collection
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids)
        }
    except Exception as e:
        print(f"Error during PDF ingestion orchestration: {e}")
        return {
            "status": "error",
            "message": f"PDF ingestion failed: {str(e)}"
        }

def ingest_docx(file_path: str, filename: str) -> dict:
    """
    Orchestrates DOCX text extraction, chunking, and database storage.
    """
    try:
        # 1. Extract text paragraphs
        pages = extract_docx_text(file_path)
        if not pages:
            return {"status": "warning", "message": f"No text extracted from DOCX: {filename}"}
            
        ids = []
        documents = []
        metadatas = []
        
        # 2. Chunk text and prepare database entries
        for p in pages:
            page_num = p["page"]
            page_text = p["text"]
            
            chunks = chunk_text(page_text)
            for idx, chunk in enumerate(chunks):
                chunk_id = f"docx_{uuid.uuid4().hex}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "source": filename,
                    "page": page_num,
                    "chunk_index": idx,
                    "source_type": "docx"
                })
                
        # 3. Add to persistent ChromaDB collection
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids)
        }
    except Exception as e:
        print(f"Error during DOCX ingestion orchestration: {e}")
        return {
            "status": "error",
            "message": f"DOCX ingestion failed: {str(e)}"
        }

def ingest_audio(file_path: str, filename: str) -> dict:
    """
    Orchestrates audio transcription, segment merging, embedding, and storage.
    """
    try:
        # 1. Transcribe audio locally
        segments = transcribe_audio(file_path)
        if not segments:
            return {"status": "warning", "message": f"No speech segments transcribed from: {filename}"}
            
        # 2. Merge segments into semantic chunks
        merged_chunks = merge_transcript_segments(segments, target_words=150)
        
        ids = []
        documents = []
        metadatas = []
        
        # 3. Prepare database entries
        for idx, chunk in enumerate(merged_chunks):
            chunk_id = f"audio_{uuid.uuid4().hex}"
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append({
                "source": filename,
                "source_type": "audio",
                "timestamp_start": float(chunk["timestamp_start"]),
                "timestamp_end": float(chunk["timestamp_end"]),
                "chunk_index": idx
            })
            
        # 4. Add to persistent ChromaDB collection
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids)
        }
    except Exception as e:
        print(f"Error during audio ingestion orchestration: {e}")
        return {
            "status": "error",
            "message": f"Audio ingestion failed: {str(e)}"
        }

def ingest_image(file_path: str, filename: str) -> dict:
    """
    Orchestrates image OCR text extraction, chunking, database storage,
    and CLIP visual semantic indexing.
    """
    try:
        # 1. Extract text via EasyOCR
        res_ocr = extract_image_text(file_path)
        extracted_text = res_ocr["text"]
        confidence = res_ocr["confidence"]
        
        # 2. Trigger CLIP visual ingestion
        clip_status = "skipped"
        clip_id = None
        try:
            res_clip = process_clip_image(file_path, filename, ocr_confidence=confidence)
            if res_clip["status"] == "success":
                clip_status = "success"
                clip_id = res_clip["clip_id"]
            else:
                clip_status = "error"
        except Exception as e:
            print(f"Error during CLIP processing in parser: {e}")
            clip_status = "error"
        
        # Handle empty OCR text check as suggested by user
        if not extracted_text.strip():
            return {
                "status": "warning",
                "message": "No OCR text detected",
                "chunks_added": 0,
                "clip_status": clip_status,
                "clip_id": clip_id,
                "is_blank": res_clip.get("is_blank", False) if clip_status == "success" else False,
                "visual_category": res_clip.get("visual_category", "document") if clip_status == "success" else "document",
                "caption": res_clip.get("caption", "") if clip_status == "success" else ""
            }
            
        # 3. Chunk text
        chunks = chunk_text(extracted_text)
        
        ids = []
        documents = []
        metadatas = []
        
        # 4. Prepare database entries
        for idx, chunk in enumerate(chunks):
            chunk_id = f"image_{uuid.uuid4().hex}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": filename,
                "source_type": "image",
                "chunk_index": idx,
                "ocr_confidence": confidence
            })
            
        # 5. Add to persistent ChromaDB collection
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids),
            "clip_status": clip_status,
            "clip_id": clip_id,
            "is_blank": res_clip.get("is_blank", False) if clip_status == "success" else False,
            "visual_category": res_clip.get("visual_category", "document") if clip_status == "success" else "document",
            "caption": res_clip.get("caption", "") if clip_status == "success" else ""
        }

    except Exception as e:
        print(f"Error during image ingestion orchestration: {e}")
        return {
            "status": "error",
            "message": f"Image Ingestion failed: {str(e)}"
        }

def ingest_csv(file_path: str, filename: str) -> dict:
    import csv
    try:
        ids = []
        documents = []
        metadatas = []
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return {"status": "warning", "message": f"Empty CSV: {filename}"}
                
            header = rows[0]
            for idx, row in enumerate(rows[1:]):
                row_str = ", ".join([f"{h}: {val}" for h, val in zip(header, row)])
                chunk_id = f"csv_{uuid.uuid4().hex}"
                ids.append(chunk_id)
                documents.append(row_str)
                metadatas.append({
                    "source": filename,
                    "row_index": idx,
                    "source_type": "csv"
                })
                
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids)
        }
    except Exception as e:
        print(f"Error during CSV ingestion: {e}")
        return {
            "status": "error",
            "message": f"CSV ingestion failed: {str(e)}"
        }

def ingest_markdown(file_path: str, filename: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if not text.strip():
            return {"status": "warning", "message": f"Empty markdown file: {filename}"}
            
        chunks = chunk_text(text)
        ids = []
        documents = []
        metadatas = []
        for idx, chunk in enumerate(chunks):
            chunk_id = f"md_{uuid.uuid4().hex}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": filename,
                "chunk_index": idx,
                "source_type": "markdown"
            })
            
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids)
        }
    except Exception as e:
        print(f"Error during Markdown ingestion: {e}")
        return {
            "status": "error",
            "message": f"Markdown ingestion failed: {str(e)}"
        }

def ingest_json(file_path: str, filename: str) -> dict:
    import json
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            
        text = json.dumps(data, indent=2)
        chunks = chunk_text(text)
        ids = []
        documents = []
        metadatas = []
        for idx, chunk in enumerate(chunks):
            chunk_id = f"json_{uuid.uuid4().hex}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": filename,
                "chunk_index": idx,
                "source_type": "json"
            })
            
        db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        return {
            "status": "success",
            "chunks_added": len(ids)
        }
    except Exception as e:
        print(f"Error during JSON ingestion: {e}")
        return {
            "status": "error",
            "message": f"JSON ingestion failed: {str(e)}"
        }

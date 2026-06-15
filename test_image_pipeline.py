import os
from PIL import Image, ImageDraw, ImageFont
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.text_retriever import retrieve_text

# TODO: Implement CLIP-based visual embeddings for rich multi-modal semantics
# TODO: Implement image-to-image similarity search and retrieval
# TODO: Implement metadata mapping for OCR bounding boxes to support front-end highlight overlays

def create_text_image(file_path: str):
    """
    Generates a PNG image containing clear text.
    """
    img = Image.new('RGB', (800, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=24)
    except Exception:
        font = ImageFont.load_default()
    d.text((20, 35), "The budget for Project Alpha is 450,000 dollars.", fill=(0, 0, 0), font=font)
    img.save(file_path)
    print(f"Created text image at: {file_path}")

def create_blank_image(file_path: str):
    """
    Generates a blank PNG image.
    """
    img = Image.new('RGB', (400, 100), color=(255, 255, 255))
    img.save(file_path)
    print(f"Created blank image at: {file_path}")

def run_test():
    text_img_path = os.path.abspath("test_budget.png")
    blank_img_path = os.path.abspath("test_blank.png")
    
    create_text_image(text_img_path)
    create_blank_image(blank_img_path)
    
    try:
        print("\nResetting database...")
        db.reset_db()
        
        # Test 1: Ingesting text image
        print(f"\nIngesting text image: {text_img_path}...")
        res_text = ingest_file(text_img_path, "test_budget.png")
        print(f"Ingestion result: {res_text}")
        
        assert res_text.get("status") == "success", "Ingestion failed for text image"
        assert res_text.get("chunks_added", 0) > 0, "No chunks were added for text image"
        
        # Test 2: Ingesting blank image
        print(f"\nIngesting blank image: {blank_img_path}...")
        res_blank = ingest_file(blank_img_path, "test_blank.png")
        print(f"Ingestion result: {res_blank}")
        
        assert res_blank.get("status") == "warning", "Expected warning status for blank image"
        assert res_blank.get("message") == "No OCR text detected", f"Expected 'No OCR text detected', got '{res_blank.get('message')}'"
        
        # Test 3: Retrieve and verify query
        query = "What is the budget of Project Alpha?"
        print(f"\nRunning semantic retrieval with query: '{query}'")
        retrieved = retrieve_text(query, n_results=3)
        
        print("\n--- Retrieved Chunks ---")
        for idx, chunk in enumerate(retrieved):
            print(f"\nChunk {idx + 1}:")
            print(f"  ID: {chunk['id']}")
            print(f"  Score: {chunk['score']}")
            print(f"  Source: {chunk['source']}")
            print(f"  Source Type: {chunk['source_type']}")
            print(f"  OCR Confidence: {chunk['ocr_confidence']}")
            print(f"  Text: '{chunk['text']}'")
            print(f"  Metadata: {chunk['metadata']}")
            
        assert len(retrieved) > 0, "No chunks retrieved"
        
        best_chunk = retrieved[0]
        assert "450" in best_chunk["text"], "Expected budget value in text"
        assert best_chunk["source_type"] == "image", f"Expected source_type 'image', got '{best_chunk['source_type']}'"
        assert best_chunk["source"] == "test_budget.png", f"Expected source 'test_budget.png', got '{best_chunk['source']}'"
        assert best_chunk["ocr_confidence"] is not None and best_chunk["ocr_confidence"] > 0.0, "OCR confidence should be positive"
        
        # Test 4: Local LLM generation
        context = "\n".join([c["text"] for c in retrieved])
        print("\nGenerating grounded response from local LLM...")
        from app.llm.ollama_client import ollama_client
        answer = ollama_client.generate_response(query=query, context=context)
        print(f"LLM Answer:\n{answer}")
        
        assert "450" in answer or "450,000" in answer or "450000" in answer, "Expected LLM answer to mention the budget"
        
        print("\nTest Status: PASSED (Successfully verified OCR RAG ingestion, empty checks, and retrieval!)")
        
    finally:
        # Cleanup files
        for p in [text_img_path, blank_img_path]:
            if os.path.exists(p):
                os.remove(p)
                print(f"Cleaned up temporary file: {p}")

if __name__ == "__main__":
    run_test()

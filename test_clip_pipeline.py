import os
from PIL import Image, ImageDraw, ImageFont
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.image_retriever import retrieve_images

# TODO: Implement cross-modal reranking validation tests
# TODO: Implement image-to-image similarity verification tests
# TODO: Implement hybrid retriever test scenarios

def create_flowchart_image(file_path: str):
    """
    Generates a mock flowchart image using shapes and text.
    """
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=14)
    except Exception:
        font = ImageFont.load_default()
        
    # Draw flowchart boxes
    # 1. Start Box (rounded rectangle style or oval)
    d.ellipse([140, 20, 260, 70], fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    d.text((180, 35), "Start", fill=(0, 0, 0), font=font)
    
    # Arrow 1
    d.line([200, 70, 200, 120], fill=(0, 0, 0), width=2)
    
    # 2. Decision Diamond
    d.polygon([200, 120, 260, 170, 200, 220, 140, 170], fill=(255, 230, 200), outline=(0, 0, 0), width=2)
    d.text((170, 160), "Decision?", fill=(0, 0, 0), font=font)
    
    # Arrow 2
    d.line([200, 220, 200, 270], fill=(0, 0, 0), width=2)
    
    # 3. Process Box (Rectangle)
    d.rectangle([130, 270, 270, 320], fill=(200, 255, 200), outline=(0, 0, 0), width=2)
    d.text((170, 285), "Process", fill=(0, 0, 0), font=font)
    
    # Arrow 3
    d.line([200, 320, 200, 360], fill=(0, 0, 0), width=2)
    
    # 4. End Box
    d.ellipse([140, 360, 260, 395], fill=(255, 200, 200), outline=(0, 0, 0), width=2)
    d.text((185, 370), "End", fill=(0, 0, 0), font=font)
    
    img.save(file_path)
    print(f"Created flowchart image at: {file_path}")

def create_dashboard_image(file_path: str):
    """
    Generates a mock dashboard style image with colored chart bars and labels.
    """
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=14)
        title_font = ImageFont.load_default(size=18)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    # Title
    d.text((20, 20), "KPI Analytics Dashboard", fill=(0, 0, 0), font=title_font)
    
    # Draw grid line
    d.line([40, 300, 360, 300], fill=(150, 150, 150), width=2)
    d.line([40, 100, 40, 300], fill=(150, 150, 150), width=2)
    
    # Draw chart bars
    # Bar 1 (Red)
    d.rectangle([60, 150, 110, 300], fill=(255, 100, 100), outline=(0, 0, 0), width=1)
    d.text((65, 310), "Sales", fill=(0, 0, 0), font=font)
    
    # Bar 2 (Blue)
    d.rectangle([140, 110, 190, 300], fill=(100, 150, 255), outline=(0, 0, 0), width=1)
    d.text((145, 310), "Clicks", fill=(0, 0, 0), font=font)
    
    # Bar 3 (Green)
    d.rectangle([220, 180, 270, 300], fill=(100, 255, 100), outline=(0, 0, 0), width=1)
    d.text((225, 310), "Users", fill=(0, 0, 0), font=font)
    
    # Draw pie chart representation
    d.pieslice([280, 100, 380, 200], start=0, end=120, fill=(255, 200, 100), outline=(0, 0, 0))
    d.pieslice([280, 100, 380, 200], start=120, end=360, fill=(200, 100, 255), outline=(0, 0, 0))
    
    img.save(file_path)
    print(f"Created dashboard image at: {file_path}")

def create_architecture_image(file_path: str):
    """
    Generates a mock architectural module flow diagram using Pillow.
    """
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=12)
        title_font = ImageFont.load_default(size=16)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    # Title
    d.text((10, 10), "System Architecture Diagram", fill=(0, 0, 0), font=title_font)
    
    # Box 1: FastAPI
    d.rectangle([30, 80, 150, 140], fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    d.text((40, 105), "FastAPI Web App", fill=(0, 0, 0), font=font)
    
    # Arrow to ChromaDB
    d.line([150, 110, 230, 110], fill=(0, 0, 0), width=2)
    
    # Box 2: ChromaDB
    d.rectangle([230, 80, 370, 140], fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    d.text((245, 105), "ChromaDB Client", fill=(0, 0, 0), font=font)
    
    # Arrow down to Ollama
    d.line([90, 140, 90, 220], fill=(0, 0, 0), width=2)
    
    # Box 3: Ollama
    d.rectangle([30, 220, 150, 280], fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    d.text((40, 245), "Ollama Local LLM", fill=(0, 0, 0), font=font)
    
    # Arrow to CLIP
    d.line([150, 250, 230, 250], fill=(0, 0, 0), width=2)
    
    # Box 4: CLIP
    d.rectangle([230, 220, 370, 280], fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    d.text((245, 245), "CLIP Embedder", fill=(0, 0, 0), font=font)
    
    img.save(file_path)
    print(f"Created architecture image at: {file_path}")

def run_test():
    flowchart_path = os.path.abspath("test_flowchart.png")
    dashboard_path = os.path.abspath("test_dashboard.png")
    arch_path = os.path.abspath("test_architecture.png")
    blank_path = os.path.abspath("test_blank_clip.png")
    
    create_flowchart_image(flowchart_path)
    create_dashboard_image(dashboard_path)
    create_architecture_image(arch_path)
    
    # Create a blank image to verify OCR empty check and CLIP index coexistence
    blank_img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    blank_img.save(blank_path)
    print(f"Created blank image at: {blank_path}")
    
    try:
        print("\nResetting database...")
        db.reset_db()
        
        # 1. Ingest flowchart
        print(f"\nIngesting flowchart: {flowchart_path}...")
        res_flow = ingest_file(flowchart_path, "test_flowchart.png")
        print(f"Ingestion result: {res_flow}")
        assert res_flow.get("status") == "success"
        
        # 2. Ingest dashboard
        print(f"\nIngesting dashboard: {dashboard_path}...")
        res_dash = ingest_file(dashboard_path, "test_dashboard.png")
        print(f"Ingestion result: {res_dash}")
        assert res_dash.get("status") == "success"
        
        # 3. Ingest architecture
        print(f"\nIngesting architecture: {arch_path}...")
        res_arch = ingest_file(arch_path, "test_architecture.png")
        print(f"Ingestion result: {res_arch}")
        assert res_arch.get("status") == "success"
        
        # 4. Ingest blank image (Verify backward compatibility with empty OCR warning)
        print(f"\nIngesting blank image: {blank_path}...")
        res_blank = ingest_file(blank_path, "test_blank_clip.png")
        print(f"Ingestion result: {res_blank}")
        assert res_blank.get("status") == "warning"
        assert res_blank.get("message") == "No OCR text detected"
        assert res_blank.get("clip_status") == "success"
        
        # 5. Run visual queries with soft assertions
        test_scenarios = [
            {"query": "flowchart", "expected": "test_flowchart.png"},
            {"query": "dashboard", "expected": "test_dashboard.png"},
            {"query": "architecture diagram", "expected": "test_architecture.png"}
        ]
        
        for scenario in test_scenarios:
            query = scenario["query"]
            expected = scenario["expected"]
            print(f"\nRunning visual retrieval for query: '{query}'")
            results = retrieve_images(query, limit=3)
            
            print(f"--- Top Results for '{query}' ---")
            top_filenames = []
            for idx, res in enumerate(results):
                print(f"  {idx + 1}. Source: {res['source']}, Score: {res['score']:.4f}, Path: {res['file_path']}, Ingested At: {res['metadata'].get('ingested_at')}")
                top_filenames.append(res["source"])
                
            # Soft assertion: expected image must be in the top 3 retrieved results
            assert expected in top_filenames, f"Expected '{expected}' to be in top 3 results for '{query}', got: {top_filenames}"
            
        print("\nTest Status: PASSED (Successfully verified CLIP Visual Semantic Retrieval with soft assertions!)")
        
    finally:
        # Cleanup files
        for p in [flowchart_path, dashboard_path, arch_path, blank_path]:
            if os.path.exists(p):
                os.remove(p)
                print(f"Cleaned up temporary file: {p}")

if __name__ == "__main__":
    run_test()

import os
import sys
import requests
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Ensure the app folder is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.image_retriever import retrieve_images
from app.retrieval.query_router import route_query
from app.retrieval.visual_qa_pipeline import answer_visual_question
from app.retrieval.intent_detector import detect_query_type

def draw_centered_text(draw, box, text, font, fill=(0, 0, 0)):
    x0, y0, x1, y1 = box
    box_w = x1 - x0
    box_h = y1 - y0
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = x0 + (box_w - text_w) / 2
    y = y0 + (box_h - text_h) / 2 - 2
    draw.text((x, y), text, fill=fill, font=font)

def create_architecture_image(file_path: str):
    """
    Generates a mock architectural module flow diagram using Pillow.
    Specifically labels the Ollama box as "Ollama (Llama3.1)".
    """
    img = Image.new("RGB", (600, 450), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 18)
        title_font = ImageFont.truetype("Arial", 24)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    # Title
    d.text((40, 40), "System Architecture Diagram", fill=(0, 0, 0), font=title_font)
    
    # Box 1: FastAPI
    box1 = [40, 100, 240, 180]
    d.rectangle(box1, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box1, "FastAPI Web App", font)
    
    # Arrow to ChromaDB
    d.line([240, 140, 360, 140], fill=(0, 0, 0), width=3)
    
    # Box 2: ChromaDB
    box2 = [360, 100, 560, 180]
    d.rectangle(box2, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box2, "ChromaDB Client", font)
    
    # Arrow down to Ollama
    d.line([140, 180, 140, 280], fill=(0, 0, 0), width=3)
    
    # Box 3: Ollama (Llama3.1)
    box3 = [40, 280, 240, 360]
    d.rectangle(box3, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box3, "Ollama (Llama3.1)", font)
    
    # Arrow to CLIP
    d.line([240, 320, 360, 320], fill=(0, 0, 0), width=3)
    
    # Box 4: CLIP
    box4 = [360, 280, 560, 360]
    d.rectangle(box4, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box4, "CLIP Embedder", font)
    
    img.save(file_path)
    print(f"Created architecture image at: {file_path}")

def create_flowchart_image(file_path: str):
    """
    Generates a flowchart with exactly 5 circular nodes using Pillow.
    """
    img = Image.new("RGB", (600, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 16)
        title_font = ImageFont.truetype("Arial", 22)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    d.text((40, 40), "Flowchart with 5 circular nodes", fill=(0, 0, 0), font=title_font)
    
    # Circle 1: Node A
    c1 = [50, 100, 150, 200]
    d.ellipse(c1, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c1, "Node A", font)
    
    # Arrow A -> B
    d.line([150, 150, 250, 150], fill=(0, 0, 0), width=3)
    
    # Circle 2: Node B
    c2 = [250, 100, 350, 200]
    d.ellipse(c2, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c2, "Node B", font)
    
    # Arrow B -> C
    d.line([350, 150, 450, 150], fill=(0, 0, 0), width=3)
    
    # Circle 3: Node C
    c3 = [450, 100, 550, 200]
    d.ellipse(c3, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c3, "Node C", font)
    
    # Arrow B -> D (down)
    d.line([300, 200, 300, 300], fill=(0, 0, 0), width=3)
    
    # Circle 4: Node D
    c4 = [250, 300, 350, 400]
    d.ellipse(c4, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c4, "Node D", font)
    
    # Arrow D -> E
    d.line([300, 400, 300, 450], fill=(0, 0, 0), width=3)
    
    # Circle 5: Node E
    c5 = [250, 450, 350, 550]
    d.ellipse(c5, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c5, "Node E", font)
    
    img.save(file_path)
    print(f"Created flowchart image at: {file_path}")

def create_dashboard_image(file_path: str):
    """
    Generates a dashboard with exactly 3 vertical bar charts (rectangles).
    """
    img = Image.new("RGB", (600, 450), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 18)
        title_font = ImageFont.truetype("Arial", 24)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    # Title
    d.text((40, 40), "Dashboard showing 3 vertical bars", fill=(0, 0, 0), font=title_font)
    
    # Grid line
    d.line([60, 350, 540, 350], fill=(180, 180, 180), width=3)
    
    # Bar 1 (Sales)
    d.rectangle([100, 150, 180, 350], fill=(255, 100, 100), outline=(0, 0, 0), width=1)
    d.text((100, 370), "Sales Bar", fill=(0, 0, 0), font=font)
    
    # Bar 2 (Clicks)
    d.rectangle([260, 80, 340, 350], fill=(100, 150, 255), outline=(0, 0, 0), width=1)
    d.text((260, 370), "Clicks Bar", fill=(0, 0, 0), font=font)
    
    # Bar 3 (Users)
    d.rectangle([420, 200, 500, 350], fill=(100, 255, 100), outline=(0, 0, 0), width=1)
    d.text((420, 370), "Users Bar", fill=(0, 0, 0), font=font)
    
    img.save(file_path)
    print(f"Created dashboard image at: {file_path}")

def create_screenshot_image(file_path: str):
    """
    Generates a mock screenshot containing the text "Connection Timeout Error".
    """
    img = Image.new("RGB", (600, 350), color=(50, 50, 50))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 18)
        title_font = ImageFont.truetype("Arial", 22)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    d.rectangle([0, 0, 600, 40], fill=(30, 30, 30))
    d.ellipse([15, 12, 27, 24], fill=(255, 95, 87))
    d.ellipse([35, 12, 47, 24], fill=(255, 189, 46))
    d.ellipse([55, 12, 67, 24], fill=(39, 201, 63))
    
    alert_box = [80, 80, 520, 280]
    d.rectangle(alert_box, fill=(70, 70, 70), outline=(255, 100, 100), width=3)
    
    # Centered texts
    draw_centered_text(d, [80, 95, 520, 150], "SYSTEM CRITICAL ALERT", title_font, fill=(255, 100, 100))
    draw_centered_text(d, [80, 160, 520, 240], "Error: Connection Timeout Error", font, fill=(255, 255, 255))
    
    img.save(file_path)
    print(f"Created screenshot image at: {file_path}")

def create_blank_image(file_path: str):
    """
    Generates a completely blank white canvas image.
    """
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(file_path)
    print(f"Created blank image at: {file_path}")

def create_table_image(file_path: str):
    """
    Generates a table image with grid lines and data cells.
    """
    img = Image.new("RGB", (600, 350), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 16)
        title_font = ImageFont.truetype("Arial", 20)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    d.text((40, 30), "Data Summary Table", fill=(0, 0, 0), font=title_font)
    
    x_start = 50
    y_start = 80
    col_width = 166
    row_height = 50
    
    # Draw horizontal lines
    for i in range(5):
        y = y_start + i * row_height
        d.line([x_start, y, x_start + 3 * col_width, y], fill=(0, 0, 0), width=2 if i == 0 or i == 1 else 1)
        
    # Draw vertical lines
    for j in range(4):
        x = x_start + j * col_width
        d.line([x, y_start, x, y_start + 4 * row_height], fill=(0, 0, 0), width=1)
        
    headers = ["Header A", "Header B", "Header C"]
    rows = [
        ["Value A1", "Value B1", "Value C1"],
        ["Value A2", "Value B2", "Value C2"],
        ["Value A3", "Value B3", "Value C3"]
    ]
    
    # Header cells
    for j, h in enumerate(headers):
        cell_box = [x_start + j * col_width, y_start, x_start + (j + 1) * col_width, y_start + row_height]
        draw_centered_text(d, cell_box, h, font)
        
    # Data cells
    for r_idx, row_vals in enumerate(rows):
        for c_idx, val in enumerate(row_vals):
            cell_box = [
                x_start + c_idx * col_width,
                y_start + (r_idx + 1) * row_height,
                x_start + (c_idx + 1) * col_width,
                y_start + (r_idx + 2) * row_height
            ]
            draw_centered_text(d, cell_box, val, font)
            
    img.save(file_path)
    print(f"Created table image at: {file_path}")

def run_tests():
    # Setup test file paths
    arch_path = os.path.abspath("test_architecture.png")
    flowchart_path = os.path.abspath("test_flowchart.png")
    dashboard_path = os.path.abspath("test_dashboard.png")
    screenshot_path = os.path.abspath("test_screenshot.png")
    blank_path = os.path.abspath("test_blank.png")
    table_path = os.path.abspath("test_table.png")
    
    try:
        # Create all mock files
        create_architecture_image(arch_path)
        create_flowchart_image(flowchart_path)
        create_dashboard_image(dashboard_path)
        create_screenshot_image(screenshot_path)
        create_blank_image(blank_path)
        create_table_image(table_path)
        
        # Reset DB
        print("\n--- Resetting database ---")
        db.reset_db()
        print("Database reset successful.")
        
        # Ingest mock files and record results
        ingestion_results = {}
        for label, path, expected_status in [
            ("architecture", arch_path, "success"),
            ("flowchart", flowchart_path, "success"),
            ("dashboard", dashboard_path, "success"),
            ("screenshot", screenshot_path, "success"),
            ("blank", blank_path, "warning"),
            ("table", table_path, "success")
        ]:
            print(f"\nIngesting {label} from {path}...")
            res = ingest_file(path, os.path.basename(path))
            print(f"Result for {label}: {res}")
            assert res["status"] == expected_status, f"Expected {expected_status}, got {res['status']}"
            ingestion_results[label] = res
            
            # Verify ingestion-time caption was cached in metadata for non-blank images
            if label != "blank":
                caption = res.get("caption")
                print(f"Cached Caption: '{caption}'")
                assert caption is not None and len(caption) > 0, f"Expected non-empty caption for {label}"
        
        print("\n--- Running Direct VQA & Intent Routing Tests in Python ---")
        
        # Query 1: Architecture
        q1 = "What model is shown inside Ollama in the diagram?"
        intent1 = detect_query_type(q1)
        print(f"Q: '{q1}' -> Detected Intent: {intent1}")
        assert intent1 == "VISUAL"
        
        print(f"Answering visual question: '{q1}'...")
        res1 = answer_visual_question(q1)
        print(f"Answer details: {res1}")
        assert "test_architecture.png" in res1["source_image"], f"Expected test_architecture.png as source, got {res1['source_image']}"
        assert res1["visual_category"] == "architecture diagram", f"Expected category 'architecture diagram', got {res1['visual_category']}"
        assert res1["clip_score"] >= 0.25, f"Expected clip_score >= 0.25, got {res1['clip_score']}"
        assert res1["confidence"] in ["High", "Medium", "Low"], f"Expected valid confidence label, got {res1['confidence']}"
        assert res1["model_used"] == "llava:7b", f"Expected model llava:7b, got {res1['model_used']}"
        
        print(f"VQA Answer: {res1['answer']}")
        # LLaVA answer assertion: should contain "llama"
        assert "llama" in res1["answer"].lower(), f"Expected answer to refer to llama, got: {res1['answer']}"
        
        # Query 2: Flowchart
        q2 = "How many circular nodes are in the flowchart?"
        intent2 = detect_query_type(q2)
        print(f"Q: '{q2}' -> Detected Intent: {intent2}")
        assert intent2 == "VISUAL"
        
        res2 = answer_visual_question(q2)
        print(f"Answer details: {res2}")
        assert "test_flowchart.png" in res2["source_image"]
        assert res2["visual_category"] == "flowchart"
        print(f"VQA Answer: {res2['answer']}")
        assert any(x in res2["answer"].lower() for x in ["5", "five"]), f"Expected answer to contain 5 or five, got: {res2['answer']}"
        
        # Query 3: Dashboard
        q3 = "How many vertical bars/rectangles are in the dashboard?"
        intent3 = detect_query_type(q3)
        print(f"Q: '{q3}' -> Detected Intent: {intent3}")
        assert intent3 == "VISUAL"
        
        res3 = answer_visual_question(q3)
        print(f"Answer details: {res3}")
        assert "test_dashboard.png" in res3["source_image"]
        assert res3["visual_category"] == "dashboard"
        print(f"VQA Answer: {res3['answer']}")
        assert any(x in res3["answer"].lower() for x in ["3", "three"]), f"Expected answer to contain 3 or three, got: {res3['answer']}"
        
        # Query 4: Screenshot
        q4 = "What error is shown in the screenshot?"
        intent4 = detect_query_type(q4)
        print(f"Q: '{q4}' -> Detected Intent: {intent4}")
        assert intent4 == "VISUAL"
        
        res4 = answer_visual_question(q4)
        print(f"Answer details: {res4}")
        assert "test_screenshot.png" in res4["source_image"]
        assert res4["visual_category"] == "screenshot"
        print(f"VQA Answer: {res4['answer']}")
        assert "timeout" in res4["answer"].lower(), f"Expected answer to refer to timeout, got: {res4['answer']}"
        
        # Query 5: Table
        q5 = "Which columns are in the table?"
        intent5 = detect_query_type(q5)
        print(f"Q: '{q5}' -> Detected Intent: {intent5}")
        assert intent5 == "VISUAL"
        
        res5 = answer_visual_question(q5)
        print(f"Answer details: {res5}")
        assert "test_table.png" in res5["source_image"]
        assert res5["visual_category"] == "table"
        print(f"VQA Answer: {res5['answer']}")
        assert any(x in res5["answer"].lower() for x in ["header a", "header b", "header c"]), f"Expected column names in answer, got: {res5['answer']}"
        
        # Query 6: Routing check for Multimodal and Text
        q_text = "What is ChromaDB?"
        route_res_text = route_query(q_text)
        print(f"Q: '{q_text}' -> Route Result: {route_res_text['intent']}")
        assert route_res_text["intent"] == "TEXT"
        
        q_multi = "Tell me about the system architecture and list its components"
        route_res_multi = route_query(q_multi)
        print(f"Q: '{q_multi}' -> Route Result: {route_res_multi['intent']}")
        assert route_res_multi["intent"] in ["MULTIMODAL", "VISUAL"]
        
        print("\n--- Local Python Tests Passed Successfully! ---")
        
        # Now let's try querying via FastAPI REST backend
        print("\n--- Querying API Server ---")
        base_url = "http://localhost:8000"
        
        # Call VQA endpoint
        resp_vqa = requests.post(f"{base_url}/visual-qa", json={"question": q1}, timeout=30)
        print(f"FASTAPI /visual-qa response: {resp_vqa.status_code}")
        print(resp_vqa.json())
        assert resp_vqa.status_code == 200
        
        # Call Router endpoint
        resp_route = requests.post(f"{base_url}/query-route", json={"query": q_text}, timeout=15)
        print(f"FASTAPI /query-route text response: {resp_route.status_code}")
        print(resp_route.json())
        assert resp_route.status_code == 200
        assert resp_route.json()["intent"] == "TEXT"
        
        print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")
        
    except Exception as e:
        print(f"\n!!! TEST FAILED !!!")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup mock files
        print("\nCleaning up mock images...")
        for p in [arch_path, flowchart_path, dashboard_path, screenshot_path, blank_path, table_path]:
            if os.path.exists(p):
                os.remove(p)
                print(f"Removed temporary test file: {p}")

if __name__ == "__main__":
    run_tests()

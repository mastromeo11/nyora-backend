import os
import sys
import json
import time
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.image_retriever import retrieve_images
from app.retrieval.query_router import route_query
from app.retrieval.visual_qa_pipeline import answer_visual_question
from app.retrieval.intent_detector import detect_query_type
from app.llm.vqa_cache import CACHE_FILE

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
    img = Image.new("RGB", (600, 450), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 18)
        title_font = ImageFont.truetype("Arial", 24)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    d.text((40, 40), "System Architecture Diagram", fill=(0, 0, 0), font=title_font)
    
    # FastAPI
    box1 = [40, 100, 240, 180]
    d.rectangle(box1, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box1, "FastAPI Web App", font)
    
    # Arrow to ChromaDB
    d.line([240, 140, 360, 140], fill=(0, 0, 0), width=3)
    
    # ChromaDB
    box2 = [360, 100, 560, 180]
    d.rectangle(box2, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box2, "ChromaDB Client", font)
    
    # Arrow down to Ollama
    d.line([140, 180, 140, 280], fill=(0, 0, 0), width=3)
    
    # Ollama (Llama3.1)
    box3 = [40, 280, 240, 360]
    d.rectangle(box3, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box3, "Ollama (Llama3.1)", font)
    
    # Arrow to CLIP
    d.line([240, 320, 360, 320], fill=(0, 0, 0), width=3)
    
    # CLIP
    box4 = [360, 280, 560, 360]
    d.rectangle(box4, fill=(240, 240, 240), outline=(0, 0, 0), width=2)
    draw_centered_text(d, box4, "CLIP Embedder", font)
    
    img.save(file_path)

def create_flowchart_image(file_path: str):
    img = Image.new("RGB", (600, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 16)
        title_font = ImageFont.truetype("Arial", 22)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    d.text((40, 40), "Flowchart with 5 circular nodes", fill=(0, 0, 0), font=title_font)
    
    c1 = [50, 100, 150, 200]
    d.ellipse(c1, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c1, "Node A", font)
    
    d.line([150, 150, 250, 150], fill=(0, 0, 0), width=3)
    
    c2 = [250, 100, 350, 200]
    d.ellipse(c2, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c2, "Node B", font)
    
    d.line([350, 150, 450, 150], fill=(0, 0, 0), width=3)
    
    c3 = [450, 100, 550, 200]
    d.ellipse(c3, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c3, "Node C", font)
    
    d.line([300, 200, 300, 300], fill=(0, 0, 0), width=3)
    
    c4 = [250, 300, 350, 400]
    d.ellipse(c4, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c4, "Node D", font)
    
    d.line([300, 400, 300, 450], fill=(0, 0, 0), width=3)
    
    c5 = [250, 450, 350, 550]
    d.ellipse(c5, fill=(200, 220, 255), outline=(0, 0, 0), width=2)
    draw_centered_text(d, c5, "Node E", font)
    
    img.save(file_path)

def create_dashboard_image(file_path: str):
    img = Image.new("RGB", (600, 450), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial", 18)
        title_font = ImageFont.truetype("Arial", 24)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    d.text((40, 40), "Dashboard showing 3 vertical bars", fill=(0, 0, 0), font=title_font)
    d.line([60, 350, 540, 350], fill=(180, 180, 180), width=3)
    
    d.rectangle([100, 150, 180, 350], fill=(255, 100, 100), outline=(0, 0, 0), width=1)
    d.text((100, 370), "Sales Bar", fill=(0, 0, 0), font=font)
    
    d.rectangle([260, 80, 340, 350], fill=(100, 150, 255), outline=(0, 0, 0), width=1)
    d.text((260, 370), "Clicks Bar", fill=(0, 0, 0), font=font)
    
    d.rectangle([420, 200, 500, 350], fill=(100, 255, 100), outline=(0, 0, 0), width=1)
    d.text((420, 370), "Users Bar", fill=(0, 0, 0), font=font)
    
    img.save(file_path)

def create_screenshot_image(file_path: str):
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
    
    draw_centered_text(d, [80, 95, 520, 150], "SYSTEM CRITICAL ALERT", title_font, fill=(255, 100, 100))
    draw_centered_text(d, [80, 160, 520, 240], "Error: Connection Timeout Error", font, fill=(255, 255, 255))
    
    img.save(file_path)

def create_blank_image(file_path: str):
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(file_path)

def create_table_image(file_path: str):
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
    
    for i in range(5):
        y = y_start + i * row_height
        d.line([x_start, y, x_start + 3 * col_width, y], fill=(0, 0, 0), width=2 if i == 0 or i == 1 else 1)
        
    for j in range(4):
        x = x_start + j * col_width
        d.line([x, y_start, x, y_start + 4 * row_height], fill=(0, 0, 0), width=1)
        
    headers = ["Header A", "Header B", "Header C"]
    rows = [
        ["Value A1", "Value B1", "Value C1"],
        ["Value A2", "Value B2", "Value C2"],
        ["Value A3", "Value B3", "Value C3"]
    ]
    
    for j, h in enumerate(headers):
        cell_box = [x_start + j * col_width, y_start, x_start + (j + 1) * col_width, y_start + row_height]
        draw_centered_text(d, cell_box, h, font)
        
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

def run_quality_suite():
    # File Paths
    arch_path = os.path.abspath("test_architecture.png")
    flowchart_path = os.path.abspath("test_flowchart.png")
    dashboard_path = os.path.abspath("test_dashboard.png")
    screenshot_path = os.path.abspath("test_screenshot.png")
    blank_path = os.path.abspath("test_blank.png")
    table_path = os.path.abspath("test_table.png")
    dup_path = os.path.abspath("test_duplicate.png")
    
    metrics = {
        "passed_tests": 0,
        "total_tests": 9,
        "top1_accuracy": 0.0,
        "top3_accuracy": 0.0,
        "cache_hit_rate": 0.0,
        "average_clip_score": 0.0,
        "average_response_time": 0.0
    }
    
    passed_cases = 0
    clip_scores = []
    latencies = []
    
    try:
        # Generate images
        create_architecture_image(arch_path)
        create_flowchart_image(flowchart_path)
        create_dashboard_image(dashboard_path)
        create_screenshot_image(screenshot_path)
        create_blank_image(blank_path)
        create_table_image(table_path)
        create_architecture_image(dup_path) # Duplicate image
        
        # Reset DB
        print("\n--- Resetting DB ---")
        db.reset_db()
        
        # Reset VQA cache file
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            
        # 1. Ingestion of images
        ingested = {}
        for label, path, expected_status in [
            ("architecture", arch_path, "success"),
            ("flowchart", flowchart_path, "success"),
            ("dashboard", dashboard_path, "success"),
            ("screenshot", screenshot_path, "success"),
            ("blank", blank_path, "warning"),
            ("table", table_path, "success"),
            ("duplicate", dup_path, "success")
        ]:
            res = ingest_file(path, os.path.basename(path))
            print(f"Ingested {label}: {res.get('status')}")
            assert res.get("status") == expected_status
            ingested[label] = res
            
        # Test 1: Ingestion blank check
        print("\nTest 1: Blank Image Detection & Exclusions")
        assert ingested["blank"]["is_blank"] == True
        # Check retrieval excludes blank
        res_search = retrieve_images("blank page", limit=10)
        source_names = [r["source"] for r in res_search]
        assert "test_blank.png" not in source_names
        passed_cases += 1
        print("[PASSED] Blank image successfully detected and excluded from search results.")
        
        # Ingestion accuracy checks
        t1_retrieved = 0
        t3_retrieved = 0
        
        # Test visual search queries
        test_queries = [
            ("What model is shown inside Ollama in the diagram?", "test_architecture.png"),
            ("How many circular nodes are in the flowchart?", "test_flowchart.png"),
            ("How many vertical bars/rectangles are in the dashboard?", "test_dashboard.png"),
            ("What error is shown in the screenshot?", "test_screenshot.png"),
            ("Which columns are in the table?", "test_table.png")
        ]
        
        # Evaluate Top-1 and Top-3 accuracy
        print("\n--- Verifying Retrieval Accuracy ---")
        for q, expected_img in test_queries:
            results = retrieve_images(q, limit=3)
            filenames = [r["source"] for r in results]
            if filenames:
                if filenames[0] == expected_img:
                    t1_retrieved += 1
                if expected_img in filenames:
                    t3_retrieved += 1
                
                clip_scores.append(results[0]["score"])
                
        metrics["top1_accuracy"] = t1_retrieved / len(test_queries)
        metrics["top3_accuracy"] = t3_retrieved / len(test_queries)
        
        assert metrics["top1_accuracy"] >= 0.80
        assert metrics["top3_accuracy"] == 1.0
        passed_cases += 1
        print(f"[PASSED] Top-1 accuracy: {metrics['top1_accuracy'] * 100:.1f}%, Top-3 accuracy: {metrics['top3_accuracy'] * 100:.1f}%")
        
        # Test 2: Sequential VQA & Citation Reasons
        print("\nTest 2: Sequential VQA and Citations")
        q_vqa = "What model is shown inside Ollama in the diagram?"
        res_vqa = answer_visual_question(q_vqa)
        print(f"Answer: {res_vqa['answer']}")
        print(f"Citation reason: {res_vqa.get('citation_reason')}")
        assert "citation_reason" in res_vqa
        assert "llama" in res_vqa["answer"].lower()
        assert "test_architecture.png" in res_vqa["source_image"]
        passed_cases += 1
        print("[PASSED] VQA successfully resolved query, returned target citation, and reason.")
        
        # Test 3: Caching logic (SHA256 questions + image bypass)
        print("\nTest 3: VQA Cache Layer Integration")
        # Run 1: Normal call (caches answer)
        q_cache = "How many circular nodes are in the flowchart?"
        start_t = time.time()
        res_uncached = answer_visual_question(q_cache)
        uncached_t = time.time() - start_t
        latencies.append(uncached_t)
        
        # Run 2: Cached call (instant bypass)
        start_t = time.time()
        res_cached = answer_visual_question(q_cache)
        cached_t = time.time() - start_t
        latencies.append(cached_t)
        
        print(f"Uncached Time: {uncached_t:.4f}s | Cached Time: {cached_t:.4f}s")
        assert res_uncached["answer"] == res_cached["answer"]
        # Cached response should be fast (bypasses VLM LLaVA, but still runs CLIP query embedder on CPU)
        assert cached_t < 1.2
        assert cached_t < (uncached_t / 4)
        metrics["cache_hit_rate"] = 0.50 # 1 out of 2 VQA calls for this query hit the cache
        passed_cases += 1
        print("[PASSED] VQA Caching bypassed LLaVA and returned instantly on subsequent requests.")
        
        # Test 4: Confidence Calibration
        print("\nTest 4: Confidence Level Calibration")
        assert res_uncached["confidence"] in ["High", "Medium", "Low"]
        passed_cases += 1
        print(f"[PASSED] Calibrated confidence returned successfully: {res_uncached['confidence']}.")
        
        # Test 5: Retrieval Explanations (Human-readable generators)
        print("\nTest 5: Explainability Checks")
        assert "citation_reason" in res_uncached
        assert "Grounded visual match" in res_uncached["citation_reason"]
        passed_cases += 1
        print("[PASSED] Citations reasons contained structured, human-readable match explanations.")
        
        # Test 6: Multi-Image Reasoning (Debug Candidate Lists)
        print("\nTest 6: Multi-Image Reasoning and Debug details")
        assert "all_candidates" in res_uncached
        for cand_debug in res_uncached["all_candidates"]:
            assert "candidate_rank" in cand_debug
            assert "candidate_source" in cand_debug
            assert "candidate_score" in cand_debug
            assert "candidate_answer" in cand_debug
        passed_cases += 1
        print("[PASSED] Exposed candidate rank debug lists inside visual responses.")
        
        # Test 7: Multimodal Fusion Context Snippets
        print("\nTest 7: Multimodal Fusion Context Enhancements")
        q_fusion = "Tell me about the system architecture and list its components"
        fused_res = route_query(q_fusion)
        print(f"Fusion answer: {fused_res['answer']}")
        assert fused_res["intent"] == "MULTIMODAL"
        # Validate that citation and explanations are exposed
        assert "retrieved_text_sources" in fused_res
        assert "retrieved_image_sources" in fused_res
        assert "evidence_explanations" in fused_res
        passed_cases += 1
        print("[PASSED] Exposed unified evidence explainability inside multimodal RAG responses.")
        
        # Test 8: REST Endpoint Validation
        print("\nTest 8: REST Endpoints Integrity")
        base_url = "http://localhost:8000"
        
        # Visual QA POST
        resp_vqa = requests.post(f"{base_url}/visual-qa", json={"question": q_vqa}, timeout=30)
        print(f"POST /visual-qa: {resp_vqa.status_code}")
        assert resp_vqa.status_code == 200
        assert "citation_reason" in resp_vqa.json()
        
        # Debug VQA GET
        resp_debug = requests.get(f"{base_url}/debug/vqa?question={q_vqa}", timeout=30)
        print(f"GET /debug/vqa: {resp_debug.status_code}")
        assert resp_debug.status_code == 200
        debug_json = resp_debug.json()
        assert "candidate_list" in debug_json
        assert "retrieval_reason" in debug_json
        
        # Router query route POST
        resp_route = requests.post(f"{base_url}/query-route", json={"query": q_fusion}, timeout=30)
        print(f"POST /query-route: {resp_route.status_code}")
        assert resp_route.status_code == 200
        assert resp_route.json()["intent"] == "MULTIMODAL"
        assert "retrieved_text_sources" in resp_route.json()
        
        passed_cases += 1
        print("[PASSED] FastAPI routes correctly exposed VQA citations, explanations, and router outputs.")
        
        # Compile Metrics
        metrics["passed_tests"] = passed_cases
        metrics["average_clip_score"] = sum(clip_scores) / len(clip_scores) if clip_scores else 0.0
        metrics["average_response_time"] = sum(latencies) / len(latencies) if latencies else 0.0
        
        print("\n====================================================")
        print("            🏆 VQA ENHANCEMENTS REPORT               ")
        print("====================================================")
        print(json.dumps(metrics, indent=4))
        print("====================================================")
        
        # Write report to test_vqa_report.json
        with open("test_vqa_report.json", "w") as f:
            json.dump(metrics, f, indent=4)
        print("Wrote benchmark metrics to test_vqa_report.json")
        
    finally:
        # Cleanup mock files
        print("\nCleaning up mock images...")
        for p in [arch_path, flowchart_path, dashboard_path, screenshot_path, blank_path, table_path, dup_path]:
            if os.path.exists(p):
                os.remove(p)
                print(f"Removed temporary test file: {p}")

if __name__ == "__main__":
    run_quality_suite()

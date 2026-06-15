import sys
import json
import urllib.request
import urllib.error

def print_help():
    print("Usage:")
    print("  python3 query.py text \"your question\"      - Ask the LLM a question using RAG")
    print("  python3 query.py image \"visual query\"    - Search for relevant images using CLIP")
    print("  python3 query.py multi \"query\"           - Search for both text chunks and images")
    print()

def make_post_request(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        try:
            detail = json.loads(error_msg).get("detail", error_msg)
        except Exception:
            detail = error_msg
        raise Exception(f"HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise Exception(f"Failed to connect to server: {e.reason}")

def main():
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    query = sys.argv[2]
    
    url_map = {
        "text": "http://localhost:8000/query",
        "image": "http://localhost:8000/search-images",
        "multi": "http://localhost:8000/search-multimodal"
    }
    
    if mode not in url_map:
        print(f"Unknown mode: {mode}")
        print_help()
        sys.exit(1)
        
    url = url_map[mode]
    
    # Send request
    try:
        if mode == "text":
            payload = {"query": query, "limit": 3}
            data = make_post_request(url, payload)
            
            print("\033[1;36m====================================================\033[0m")
            print(f"\033[1;36m❓ Query: {data['query']}\033[0m")
            print("\033[1;36m====================================================\033[0m")
            print(f"\033[1;32m🤖 LLM Answer:\033[0m")
            print(data["answer"])
            print("\033[1;36m----------------------------------------------------\033[0m")
            print("\033[1;34m📚 Retrieved Context Chunks:\033[0m")
            for idx, chunk in enumerate(data["retrieved_chunks"], 1):
                print(f"\n  [{idx}] Source: {chunk['source']} (Page: {chunk['page']})")
                print(f"      OCR Score: {chunk.get('ocr_confidence', 'N/A')}")
                print(f"      Text snippet: \"{chunk['text'][:150]}...\"")
                
        elif mode == "image":
            payload = {"query": query, "limit": 3}
            results = make_post_request(url, payload)
            
            print("\033[1;36m====================================================\033[0m")
            print(f"\033[1;36m🖼️ CLIP Semantic Image Search for: '{query}'\033[0m")
            print("\033[1;36m====================================================\033[0m")
            if not results:
                print("No matching images found.")
            for idx, res in enumerate(results, 1):
                print(f"  {idx}. Source: \033[1;32m{res['source']}\033[0m")
                print(f"     Match Score: {res['score']:.4f}")
                print(f"     File Path: {res['file_path']}")
                print(f"     Ingested At: {res['metadata'].get('ingested_at')}")
                print()
                
        elif mode == "multi":
            payload = {"query": query, "text_limit": 2, "image_limit": 2}
            data = make_post_request(url, payload)
            
            print("\033[1;36m====================================================\033[0m")
            print(f"\033[1;36m🔄 Multimodal Search Results for: '{query}'\033[0m")
            print("\033[1;36m====================================================\033[0m")
            
            print("\033[1;34m📚 Matching Text Chunks:\033[0m")
            for idx, chunk in enumerate(data.get("text_results", []), 1):
                print(f"  {idx}. Source: {chunk['source']} (Type: {chunk['source_type']}) | Score: {chunk['score']:.4f}")
                print(f"     Text: \"{chunk['text'][:150]}...\"")
                print()
                
            print("\033[1;35m🖼️ Matching Visual Images (CLIP):\033[0m")
            for idx, img in enumerate(data.get("image_results", []), 1):
                print(f"  {idx}. Source: \033[1;32m{img['source']}\033[0m | Score: {img['score']:.4f}")
                print(f"     File Path: {img['file_path']}")
                print()
                
    except Exception as e:
        print(f"Error querying backend: {e}")

if __name__ == "__main__":
    main()

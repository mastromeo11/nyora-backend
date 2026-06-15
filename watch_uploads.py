import os
import time
import json
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import UPLOAD_DIR
from app.ingestion.parser import ingest_file

STATE_FILE = os.path.join(os.path.dirname(UPLOAD_DIR), ".processed_files.json")

def load_processed_files():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_processed_files(processed):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(list(processed), f, indent=4)
    except Exception as e:
        print(f"Error saving state file: {e}")

def main():
    print("\033[1;36m====================================================\033[0m")
    print("\033[1;36m       📂 Directory Watcher for RAG PRO Ingestion   \033[0m")
    print("\033[1;36m====================================================\033[0m")
    print(f"Watching directory: \033[1;33m{UPLOAD_DIR}\033[0m")
    print(f"State file: \033[1;33m{STATE_FILE}\033[0m")
    print("Press Ctrl+C to stop.\n")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    processed = load_processed_files()
    
    print(f"Loaded {len(processed)} previously processed files.")
    
    # List current files
    initial_files = os.listdir(UPLOAD_DIR)
    unprocessed_initial = [f for f in initial_files if f not in processed and not f.startswith(".")]
    if unprocessed_initial:
        print(f"Found {len(unprocessed_initial)} unprocessed files already in the directory:")
        for f in unprocessed_initial:
            print(f"  - {f}")
        print("Starting ingestion for these files...\n")
    else:
        print("No new files found. Waiting for files to be added...\n")

    try:
        while True:
            files = os.listdir(UPLOAD_DIR)
            
            for filename in files:
                if filename.startswith(".") or filename in processed:
                    continue
                
                file_path = os.path.join(UPLOAD_DIR, filename)
                if not os.path.isfile(file_path):
                    continue
                
                # Check if file size is stable (fully copied)
                try:
                    initial_size = os.path.getsize(file_path)
                    time.sleep(0.5)
                    if os.path.getsize(file_path) != initial_size:
                        continue
                except OSError:
                    continue
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] \033[1;32m[NEW FILE]\033[0m Detected: {filename}")
                print(f"[{timestamp}] \033[1;34m[INGESTING]\033[0m Processing {filename}...")
                
                try:
                    res = ingest_file(file_path, filename)
                    status = res.get("status", "error")
                    if status == "success":
                        print(f"[{timestamp}] \033[1;32m[SUCCESS]\033[0m Ingested {filename}. Result: {res}")
                        processed.add(filename)
                        save_processed_files(processed)
                    elif status == "warning":
                        print(f"[{timestamp}] \033[1;33m[WARNING]\033[0m Ingested {filename} with warnings. Result: {res}")
                        processed.add(filename)
                        save_processed_files(processed)
                    else:
                        print(f"[{timestamp}] \033[1;31m[ERROR]\033[0m Failed to ingest {filename}. Message: {res.get('message')}")
                except Exception as e:
                    print(f"[{timestamp}] \033[1;31m[EXCEPT]\033[0m Exception during ingestion: {e}")
            
            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n\033[1;33m[STOPPED]\033[0m Directory watcher stopped by user.")

if __name__ == "__main__":
    main()

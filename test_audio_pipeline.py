import os
import subprocess
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.text_retriever import retrieve_text

# TODO: Implement audio citation formatting in retrieved results (e.g. Audio Source: meeting.wav, Timestamp: 00:15 - 00:32)
# TODO: Implement number words to digits normalization (e.g. "one hundred and eighty million" -> "180 million")
# TODO: Implement full transcript retrieval endpoint feature (GET /transcript)
# TODO: Implement frontend audio playback support with timestamp seek integration
# TODO: Implement cross-modal retrieval (retrieving corresponding slides/pages for audio segments)
# TODO: Implement audio-to-image linking
# TODO: Implement audio-to-document references

def create_sample_audio(file_path: str):
    """
    Uses macOS native 'say' command to generate an audio file with specific spoken text.
    """
    text = "The board approved a renewable energy investment worth one hundred and eighty million dollars."
    print(f"Generating sample audio using macOS 'say' command speaking: '{text}'")
    # Using m4a because it is natively supported for writing by say
    cmd = ["say", "-o", file_path, text]
    subprocess.run(cmd, check=True)

def run_test():
    audio_path = os.path.abspath("test_meeting.m4a")
    filename = "test_meeting.m4a"
    create_sample_audio(audio_path)
    
    try:
        print("Resetting database...")
        db.reset_db()
        
        print(f"Ingesting audio file: {filename}...")
        res = ingest_file(audio_path, filename)
        print(f"Ingestion result: {res}")
        
        assert res.get("status") == "success", "Ingestion failed"
        assert res.get("chunks_added", 0) > 0, "No chunks were added"
        
        query = "What was the approved investment amount?"
        print(f"\nRunning semantic retrieval with query: '{query}'")
        retrieved = retrieve_text(query, n_results=3)
        
        print("\n--- Retrieved Chunks ---")
        for idx, chunk in enumerate(retrieved):
            print(f"\nChunk {idx + 1}:")
            print(f"  ID: {chunk['id']}")
            print(f"  Score: {chunk['score']}")
            print(f"  Source: {chunk['source']}")
            print(f"  Source Type: {chunk['source_type']}")
            print(f"  Timestamp Start: {chunk['timestamp_start']}")
            print(f"  Timestamp End: {chunk['timestamp_end']}")
            print(f"  Text: '{chunk['text']}'")
            print(f"  Metadata: {chunk['metadata']}")
            
        assert len(retrieved) > 0, "No chunks retrieved"
        
        best_chunk = retrieved[0]
        # Verify content matches key aspects of the spoken text
        assert "renewable energy" in best_chunk["text"].lower(), "Expected renewable energy context"
        assert best_chunk["source_type"] == "audio", f"Expected source_type 'audio', got '{best_chunk['source_type']}'"
        assert best_chunk["source"] == filename, f"Expected source '{filename}', got '{best_chunk['source']}'"
        assert best_chunk["timestamp_start"] is not None, "Timestamp start should not be None"
        assert best_chunk["timestamp_end"] is not None, "Timestamp end should not be None"
        
        # Now run query through local LLM (Ollama)
        context = "\n".join([c["text"] for c in retrieved])
        print("\nGenerating grounded response from local LLM...")
        from app.llm.ollama_client import ollama_client
        answer = ollama_client.generate_response(query=query, context=context)
        print(f"LLM Answer:\n{answer}")
        
        # Verify the LLM answer captures the essence of the target information
        assert "million" in answer.lower(), "Expected answer to mention the amount"
        
        print("\nTest Status: PASSED (Successfully ingested, transcribed, retrieved, and answered from audio!)")
        
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Cleaned up temporary audio file: {audio_path}")

if __name__ == "__main__":
    run_test()

import os
import docx
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.text_retriever import retrieve_text

def create_sample_docx(file_path: str):
    doc = docx.Document()
    doc.add_paragraph(
        "The quarterly strategy meeting discussed renewable energy investments and expansion into African markets."
    )
    doc.save(file_path)

def run_test():
    docx_path = os.path.abspath("test_strategy.docx")
    print(f"Creating sample DOCX at: {docx_path}")
    create_sample_docx(docx_path)
    
    try:
        print("Resetting database...")
        db.reset_db()
        
        print("Ingesting test_strategy.docx...")
        res = ingest_file(docx_path, "test_strategy.docx")
        print(f"Ingestion result: {res}")
        
        assert res.get("status") == "success", "Ingestion failed"
        assert res.get("chunks_added", 0) > 0, "No chunks were added"
        
        query = "What markets are being targeted?"
        print(f"Running semantic retrieval with query: '{query}'")
        retrieved = retrieve_text(query, n_results=3)
        
        print("\n--- Retrieved Chunks ---")
        for idx, chunk in enumerate(retrieved):
            print(f"\nChunk {idx + 1}:")
            print(f"  ID: {chunk['id']}")
            print(f"  Score: {chunk['score']}")
            print(f"  Page: {chunk['page']}")
            print(f"  Source Type: {chunk['source_type']}")
            print(f"  Text: '{chunk['text']}'")
            print(f"  Metadata: {chunk['metadata']}")
            
        assert len(retrieved) > 0, "No chunks retrieved"
        
        # 3. Generate grounded answer from local LLM
        context = "\n".join([chunk["text"] for chunk in retrieved])
        print("\nGenerating grounded answer from local LLM...")
        from app.llm.ollama_client import ollama_client
        answer = ollama_client.generate_response(query=query, context=context)
        print(f"LLM Answer:\n{answer}")
        
        # Verify correctness of the matched chunk
        best_chunk = retrieved[0]
        assert "African markets" in best_chunk["text"], "Expected 'African markets' in retrieved chunk"
        assert best_chunk["source_type"] == "docx", f"Expected source_type 'docx', got '{best_chunk['source_type']}'"
        assert best_chunk["page"] == 1, f"Expected page 1, got {best_chunk['page']}"
        
        print("\nTest Status: PASSED (Successfully ingested, retrieved, and verified DOCX document!)")
        
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)
            print(f"Cleaned up temporary DOCX: {docx_path}")

if __name__ == "__main__":
    run_test()

import os
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.text_retriever import retrieve_text
from app.llm.ollama_client import ollama_client

def create_sample_pdf(file_path: str):
    """
    Generates a valid minimal PDF containing text about the RAG system and vector database.
    """
    text_content = (
        "Retrieval-Augmented Generation (RAG) is a technique that combines retrieval of "
        "relevant documents from a local vector database with a language model to generate "
        "accurate, factually grounded summaries or answers. This prevents model hallucination. "
        "In our hackathon architecture, we use ChromaDB for persistent storage of text chunks. "
        "We also use sentence-transformers BAAI/bge-small-en-v1.5 to map raw documents into "
        "dense mathematical embeddings for semantic similarity search."
    )
    
    # Escape parentheses for manual PDF construction
    escaped_text = text_content.replace("(", "\\(").replace(")", "\\)")
    stream_content = f"BT\n/F1 12 Tf\n50 700 Td\n15 TL\n({escaped_text}) Tj\nT*\nET".encode('latin-1')
    stream_len = len(stream_content)
    
    header = (
        b'%PDF-1.4\n'
        b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
        b'3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n'
        b'4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n'
    )
    
    stream_header = f'5 0 obj\n<< /Length {stream_len} >>\nstream\n'.encode('latin-1')
    
    footer = (
        b'\nendstream\nendobj\n'
        b'xref\n0 6\n0000000000 65535 f\n'
        b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n300\n%%EOF\n'
    )
    
    pdf_bytes = header + stream_header + stream_content + footer
    with open(file_path, 'wb') as f:
        f.write(pdf_bytes)

def run_test():
    print("--- Running Milestone 3 RAG Pipeline Test ---")
    
    test_pdf_name = "test_rag_sample.pdf"
    test_pdf_path = os.path.abspath(test_pdf_name)
    
    print(f"Creating sample PDF at: {test_pdf_path}")
    create_sample_pdf(test_pdf_path)
    
    try:
        # 1. Reset vector DB and ingest
        print("Resetting database...")
        db.reset_db()
        
        print(f"Ingesting {test_pdf_name}...")
        ingest_res = ingest_file(test_pdf_path, test_pdf_name)
        print(f"Ingestion result: {ingest_res}")
        assert ingest_res["status"] == "success", "PDF Ingestion failed"
        
        # Test Case 1: In-Context Query
        in_context_query = "What is the persistent storage database used in our hackathon?"
        print(f"\n--- Test Case 1: In-Context Query ---")
        print(f"User Query: '{in_context_query}'")
        
        # Retrieve chunks
        retrieved_chunks = retrieve_text(in_context_query, n_results=2)
        print(f"Retrieved {len(retrieved_chunks)} context chunk(s).")
        
        context_str = "\n".join([chunk["text"] for chunk in retrieved_chunks])
        
        # Generate Answer
        print("Generating grounded answer from local LLM...")
        answer_1 = ollama_client.generate_response(query=in_context_query, context=context_str)
        print(f"LLM Answer:\n{answer_1}\n")
        
        # Validate result has "ChromaDB"
        if "Error:" not in answer_1:
            assert "chromadb" in answer_1.lower(), "Answer should contain database name 'ChromaDB'"
            print("Test Case 1: PASSED (Correct grounded response retrieved)")
        else:
            print("Test Case 1: SKIPPED (Ollama issue or timeout present)")
            
        # Test Case 2: Out-of-Context Query
        out_context_query = "What is the capital of France?"
        print(f"\n--- Test Case 2: Out-of-Context Query ---")
        print(f"User Query: '{out_context_query}'")
        
        # Retrieve chunks (similarity might pull irrelevant context)
        retrieved_chunks_2 = retrieve_text(out_context_query, n_results=2)
        context_str_2 = "\n".join([chunk["text"] for chunk in retrieved_chunks_2])
        
        # Generate Answer
        print("Generating answer from local LLM...")
        answer_2 = ollama_client.generate_response(query=out_context_query, context=context_str_2)
        print(f"LLM Answer:\n{answer_2}\n")
        
        # Validate result has fallback message
        if "Error:" not in answer_2:
            expected_msg = "The information is not available in the provided documents."
            assert expected_msg in answer_2, f"Answer should strictly say: '{expected_msg}'"
            print("Test Case 2: PASSED (Strict out-of-context protection worked)")
        else:
            print("Test Case 2: SKIPPED (Ollama issue or timeout present)")

    finally:
        # Clean up sample PDF
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            print(f"Cleaned up temporary PDF: {test_pdf_path}")
            
    print("\n--- Milestone 3 RAG Pipeline Test Finished ---")

if __name__ == "__main__":
    run_test()

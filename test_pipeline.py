import os
from app.database import db
from app.ingestion.parser import ingest_file
from app.retrieval.text_retriever import retrieve_text

def create_sample_pdf(file_path: str):
    """
    Generates a valid minimal PDF containing text about RAG and vector databases.
    """
    text_content = (
        "Retrieval-Augmented Generation (RAG) is a technique that combines retrieval of "
        "relevant documents from a local vector database with a language model to generate "
        "accurate, factually grounded summaries or answers. This prevents model hallucination. "
        "In our hackathon architecture, we use ChromaDB for persistent storage of text chunks. "
        "We also use sentence-transformers BAAI/bge-small-en-v1.5 to map raw documents into "
        "dense mathematical embeddings for semantic similarity search."
    )
    
    # Manually escape parentheses for the PDF string syntax
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
    print("--- Running Milestone 1 Pipeline Test ---")
    
    test_pdf_name = "test_sample.pdf"
    test_pdf_path = os.path.abspath(test_pdf_name)
    
    print(f"Creating sample PDF at: {test_pdf_path}")
    create_sample_pdf(test_pdf_path)
    
    try:
        # 1. Reset vector DB
        print("Resetting database...")
        db.reset_db()
        
        # 2. Ingest the sample PDF
        print(f"Ingesting {test_pdf_name}...")
        ingest_res = ingest_file(test_pdf_path, test_pdf_name)
        print(f"Ingestion result: {ingest_res}")
        assert ingest_res["status"] == "success", "PDF ingestion failed"
        
        # 3. Perform semantic query search
        test_query = "What vector database is used in the hackathon?"
        print(f"\nExecuting semantic query: '{test_query}'...")
        results = retrieve_text(test_query, n_results=2)
        
        print(f"\nRetrieved Chunks ({len(results)} matches found):")
        for rank, res in enumerate(results, 1):
            print(f"Rank {rank}:")
            print(f"  - Chunk ID: {res['id']}")
            print(f"  - Score: {res['score']:.4f}")
            print(f"  - Source: {res['metadata'].get('source')}")
            print(f"  - Page: {res['metadata'].get('page')}")
            print(f"  - Text: {res['text']}")
            
        assert len(results) > 0, "No chunks retrieved"
        assert "ChromaDB" in results[0]["text"], "Retrieved text does not contain correct content"
        print("\n--- Milestone 1 Pipeline Test Passed Successfully! ---")
        
    finally:
        # Clean up temporary test file
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            print(f"Cleaned up temporary PDF: {test_pdf_path}")

if __name__ == "__main__":
    run_test()

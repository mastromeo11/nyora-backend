from pypdf import PdfReader

def extract_pdf(file_path: str) -> list[dict]:
    """
    Extracts text page-by-page from a PDF file.
    
    Args:
        file_path (str): The path to the PDF file.
        
    Returns:
        list[dict]: A list of dictionaries containing 'page' (1-based index) and 'text'.
    """
    pages_data = []
    try:
        reader = PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            text = page.extract_text()
            if text:
                pages_data.append({
                    "page": page_num,
                    "text": text
                })
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        raise e
    return pages_data

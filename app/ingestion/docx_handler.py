import docx

def extract_docx_text(file_path: str) -> list[dict]:
    """
    Extracts text from a DOCX file, filtering out empty paragraphs.
    Groups all paragraph text into a single page entry with page number 1.
    
    Args:
        file_path (str): The physical path of the DOCX file on disk.
        
    Returns:
        list[dict]: A list containing a single dictionary with 'page' and 'text' keys.
    """
    try:
        doc = docx.Document(file_path)
        paragraphs_text = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs_text.append(text)
                
        if not paragraphs_text:
            return []
            
        full_text = "\n".join(paragraphs_text)
        return [{
            "page": 1,
            "text": full_text
        }]
    except Exception as e:
        print(f"Error reading DOCX file '{file_path}': {e}")
        raise e

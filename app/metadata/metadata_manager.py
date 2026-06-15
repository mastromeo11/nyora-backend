from typing import Optional

def build_metadata(
    chunk_id: str,
    source_file: str,
    modality: str,  # 'pdf', 'docx', 'audio', 'image'
    page_number: Optional[int] = None,
    section: Optional[str] = None,
    timestamp_start: Optional[str] = None,
    timestamp_end: Optional[str] = None,
    image_path: Optional[str] = None,
    chunk_text: Optional[str] = None
) -> dict:
    """
    Constructs a consistent metadata dictionary for ChromaDB.
    ChromaDB metadata values must be simple types: str, int, float, or bool.
    """
    metadata = {
        "chunk_id": chunk_id,
        "source_file": source_file,
        "modality": modality,
    }
    
    if page_number is not None:
        metadata["page_number"] = page_number
    if section is not None:
        metadata["section"] = section
    if timestamp_start is not None:
        metadata["timestamp_start"] = timestamp_start
    if timestamp_end is not None:
        metadata["timestamp_end"] = timestamp_end
    if image_path is not None:
        metadata["image_path"] = image_path
    if chunk_text is not None:
        metadata["chunk_text"] = chunk_text
        
    return metadata

def format_citation(metadata: dict) -> str:
    """
    Generates a citation string based on the metadata modality.
    Examples:
      - [annual_report.pdf, Page 12]
      - [meeting.docx, Section 3]
      - [call_audio.wav, 00:15-00:30]
      - [screenshot.png]
    """
    modality = metadata.get("modality", "text")
    source = metadata.get("source_file", "Unknown Source")
    
    if modality == "pdf":
        page = metadata.get("page_number")
        if page is not None:
            return f"[{source}, Page {page}]"
        return f"[{source}]"
        
    elif modality == "docx":
        section = metadata.get("section")
        page = metadata.get("page_number")
        if section:
            return f"[{source}, {section}]"
        elif page is not None:
            return f"[{source}, Page {page}]"
        return f"[{source}]"
        
    elif modality == "audio":
        start = metadata.get("timestamp_start")
        end = metadata.get("timestamp_end")
        if start and end:
            return f"[{source}, {start}-{end}]"
        return f"[{source}]"
        
    elif modality == "image":
        return f"[{source}]"
        
    return f"[{source}]"

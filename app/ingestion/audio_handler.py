import os
from faster_whisper import WhisperModel

# Singleton model instance
_whisper_model = None

def get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        # small model on CPU with float32 is robust and avoids macOS deadlocks/hangs
        _whisper_model = WhisperModel("small", device="cpu", compute_type="float32", cpu_threads=1, local_files_only=True)
    return _whisper_model

def transcribe_audio(file_path: str) -> list[dict]:
    """
    Transcribes an audio file locally using faster-whisper.
    
    Args:
        file_path (str): The physical path of the audio file.
        
    Returns:
        list[dict]: A list of dictionaries representing transcription segments with timestamps.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    try:
        model = get_whisper_model()
        segments, info = model.transcribe(file_path, beam_size=5)
        
        result = []
        for seg in segments:
            result.append({
                "timestamp_start": float(seg.start),
                "timestamp_end": float(seg.end),
                "text": seg.text.strip()
            })
        return result
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        raise e

def merge_transcript_segments(segments: list[dict], target_words: int = 150) -> list[dict]:
    """
    Merges smaller transcript segments into larger semantic chunks,
    preserving start and end timestamps.
    
    Args:
        segments (list[dict]): The list of raw transcript segments.
        target_words (int): Target number of words per merged chunk.
        
    Returns:
        list[dict]: A list of merged chunks.
    """
    if not segments:
        return []
        
    merged_chunks = []
    current_group = []
    current_words_count = 0
    
    # Track start of current group
    group_start = None
    
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
            
        words = text.split()
        if not current_group:
            group_start = seg["timestamp_start"]
            
        current_group.append(seg)
        current_words_count += len(words)
        group_end = seg["timestamp_end"]
        
        if current_words_count >= target_words:
            merged_text = " ".join([s["text"].strip() for s in current_group])
            merged_chunks.append({
                "timestamp_start": group_start,
                "timestamp_end": group_end,
                "text": merged_text
            })
            current_group = []
            current_words_count = 0
            
    # Merge any leftover segments
    if current_group:
        merged_text = " ".join([s["text"].strip() for s in current_group])
        merged_chunks.append({
            "timestamp_start": group_start,
            "timestamp_end": current_group[-1]["timestamp_end"],
            "text": merged_text
        })
        
    return merged_chunks

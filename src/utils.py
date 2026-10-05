import re
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

def extract_video_id(url: str) -> str:
    """
    Extracts and validates the 11-character YouTube video ID from any valid YouTube URL format.
    
    Supported Formats:
    - Standard: https://www.youtube.com/watch?v=VIDEO_ID
    - Mobile: https://m.youtube.com/watch?v=VIDEO_ID
    - Shortened: https://youtu.be/VIDEO_ID
    - Shorts: https://www.youtube.com/shorts/VIDEO_ID
    - Embed: https://www.youtube.com/embed/VIDEO_ID
    - Legacy / V: https://www.youtube.com/v/VIDEO_ID
    - URLs containing additional parameters (&t=30s, &list=..., ?si=..., etc.)
    - Direct 11-char Video ID: VIDEO_ID
    """
    if not url or not isinstance(url, str):
        raise ValueError("Please enter a valid YouTube video URL.")
        
    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("Please enter a valid YouTube video URL.")
        
    # Case 1: Direct 11-character Video ID
    if len(cleaned_url) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", cleaned_url):
        return cleaned_url

    # Case 2: Parse standard watch URL with query parameters (?v=...)
    try:
        parsed_url = urlparse(cleaned_url)
        hostname = parsed_url.hostname or ""
        if any(h in hostname for h in ["youtube.com", "youtu.be"]):
            query_params = parse_qs(parsed_url.query)
            if "v" in query_params and query_params["v"]:
                v_id = query_params["v"][0].strip()
                if len(v_id) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", v_id):
                    return v_id
    except Exception:
        pass

    # Case 3: Regex match for shorts, embed, youtu.be, /v/, /watch?v=
    patterns = [
        r"(?:v=|\/embed\/|\/shorts\/|\/v\/|youtu\.be\/|\/watch\?v=)([0-9A-Za-z_-]{11})",
        r"([0-9A-Za-z_-]{11})"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cleaned_url)
        if match:
            v_id = match.group(1).strip()
            if len(v_id) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", v_id):
                return v_id
                
    raise ValueError("Invalid YouTube URL. Could not extract a valid 11-character YouTube video ID.")

def validate_youtube_url(url: str) -> bool:
    """
    Validates if a given string contains a valid YouTube video URL or ID.
    """
    try:
        extract_video_id(url)
        return True
    except ValueError:
        return False

def load_api_key() -> str:
    """
    Loads Google Gemini API Key from environment variables, .env file, or Streamlit secrets.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Fallback check for Streamlit Cloud secrets
    if not api_key or api_key == "your_gemini_api_key_here":
        try:
            import streamlit as st
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass
            
    return api_key or ""

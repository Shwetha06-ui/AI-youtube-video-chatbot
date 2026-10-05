import re
import os
from dotenv import load_dotenv

def extract_video_id(url: str) -> str:
    """
    Extracts the 11-character YouTube video ID from various YouTube URL formats.
    
    Supported Formats:
    - Standard: https://www.youtube.com/watch?v=VIDEO_ID
    - Shortened: https://youtu.be/VIDEO_ID
    - Shorts: https://www.youtube.com/shorts/VIDEO_ID
    - Embed: https://www.youtube.com/embed/VIDEO_ID
    - Direct ID: VIDEO_ID (11 chars)
    """
    if not url or not url.strip():
        raise ValueError("Please enter a valid YouTube video URL.")
        
    url = url.strip()
    
    # Check if direct 11-character Video ID was entered
    if len(url) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", url):
        return url
        
    # Regex patterns for matching common YouTube URL structures
    patterns = [
        r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"^([0-9A-Za-z_-]{11})$"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    raise ValueError("Invalid YouTube URL. Could not extract a valid 11-character video ID.")

def validate_youtube_url(url: str) -> bool:
    """
    Validates if a given string is a valid YouTube URL format.
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

import re
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

def get_youtube_transcript(video_id: str) -> str:
    """
    Retrieves the transcript for a given YouTube video ID using YouTube Transcript API.
    
    Tries:
    1. Direct English transcripts ('en', 'en-US', 'en-GB').
    2. Auto-generated or translated transcripts into English.
    3. Any available transcript track as fallback.
    
    Args:
        video_id (str): The 11-character YouTube video ID.
        
    Returns:
        str: Cleaned full transcript text.
    """
    if not video_id:
        raise ValueError("Video ID cannot be empty.")
        
    try:
        # Fetch available transcripts list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Priority 1: Try finding explicit English transcript
        try:
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        except NoTranscriptFound:
            # Priority 2: Translate the first available transcript to English if translatable
            first_transcript = next(iter(transcript_list))
            if first_transcript.is_translatable:
                transcript = first_transcript.translate('en')
            else:
                transcript = first_transcript

        # Fetch transcript content list of entries
        transcript_data = transcript.fetch()
        
        # Combine text segments into a single string
        full_text = " ".join([entry['text'] for entry in transcript_data])
        
        # Clean the extracted transcript
        cleaned_text = clean_transcript_text(full_text)
        
        if not cleaned_text:
            raise Exception("Retrieved transcript is empty.")
            
        return cleaned_text

    except TranscriptsDisabled:
        raise Exception("Subtitles / Transcripts are disabled for this YouTube video.")
    except NoTranscriptFound:
        raise Exception("No transcript found for this video in the requested language.")
    except VideoUnavailable:
        raise Exception("The YouTube video is unavailable, private, or does not exist.")
    except Exception as e:
        # Final fallback: direct get_transcript call
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript_data])
            return clean_transcript_text(full_text)
        except Exception:
            raise Exception(f"Failed to extract transcript: {str(e)}")

def clean_transcript_text(text: str) -> str:
    """
    Cleans transcript text by removing bracketed sound indicators (e.g. [Music], (Laughter)),
    newline characters, and normalizing excessive whitespaces.
    
    Args:
        text (str): Raw transcript text.
        
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""
        
    # Remove bracketed markers like [Music], [Applause], (laughter)
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", " ", text)
    
    # Replace multiple whitespaces and newlines with a single space
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    return cleaned

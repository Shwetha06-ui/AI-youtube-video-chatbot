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
    Supports both youtube-transcript-api v1.x+ and legacy v0.x API versions.
    
    Args:
        video_id (str): The 11-character YouTube video ID.
        
    Returns:
        str: Cleaned full transcript text.
    """
    if not video_id:
        raise ValueError("Video ID cannot be empty.")
        
    try:
        # Instantiate or reference YouTubeTranscriptApi
        try:
            ytt = YouTubeTranscriptApi()
        except TypeError:
            ytt = YouTubeTranscriptApi

        transcript_data = None

        # Method 1: Try transcript listing & English translation
        if hasattr(ytt, "list") or hasattr(YouTubeTranscriptApi, "list_transcripts"):
            try:
                if hasattr(ytt, "list"):
                    transcript_list = ytt.list(video_id)
                else:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                try:
                    transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                except Exception:
                    first_transcript = next(iter(transcript_list))
                    if hasattr(first_transcript, "is_translatable") and first_transcript.is_translatable:
                        transcript = first_transcript.translate('en')
                    else:
                        transcript = first_transcript

                transcript_data = transcript.fetch()
            except Exception:
                transcript_data = None

        # Method 2: Direct fetch or get_transcript fallback
        if transcript_data is None:
            if hasattr(ytt, "fetch"):
                transcript_data = ytt.fetch(video_id)
            elif hasattr(YouTubeTranscriptApi, "get_transcript"):
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            elif hasattr(YouTubeTranscriptApi, "fetch"):
                transcript_data = YouTubeTranscriptApi.fetch(video_id)
            else:
                raise Exception("No transcript fetching method available.")

        # Extract text strings from transcript entries
        text_segments = []
        for entry in transcript_data:
            if isinstance(entry, dict) and 'text' in entry:
                text_segments.append(entry['text'])
            elif hasattr(entry, 'text'):
                text_segments.append(getattr(entry, 'text'))
            else:
                text_segments.append(str(entry))

        full_text = " ".join(text_segments)
        cleaned_text = clean_transcript_text(full_text)
        
        if not cleaned_text:
            raise Exception("Retrieved transcript is empty.")
            
        return cleaned_text

    except TranscriptsDisabled:
        raise Exception("Subtitles / Transcripts are disabled for this YouTube video.")
    except NoTranscriptFound:
        raise Exception("No transcript found for this video.")
    except VideoUnavailable:
        raise Exception("The YouTube video is unavailable, private, or does not exist.")
    except Exception as e:
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

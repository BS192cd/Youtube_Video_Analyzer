import streamlit as st
from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi

# Read API key from environment (or sing, show a friendly Streamlit message
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.warning("`GOOGLE_API_KEY` not found. Create a `.env` file or set the environment variable with your Google API key.")
else:
    genai.configure(api_key=api_key)

prompt="""You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


def fetch_best_transcript(video_id: str) -> list[dict]:
    """
    Fetch the best available English transcript for a YouTube video.
    
    Priority order for manually created transcripts:
    1. en-IN (Indian English)
    2. en-US (American English)
    3. en-GB (British English)
    4. en (Generic English)
    
    Falls back to auto-generated transcripts:
    1. en (English)
    2. hi (Hindi)
    
    Returns:
        list[dict]: Transcript as list of {"text": str, "start": float, "duration": float}
    
    Raises:
        ValueError: If no transcript is available
        Exception: For API errors
    """
    api = YouTubeTranscriptApi()
    
    try:
        transcripts = api.list(video_id)
    except Exception as e:
        raise Exception(f"Failed to list transcripts for video {video_id}: {str(e)}")
    
    # Priority list for manually created English transcripts
    manual_language_priority = ["en-IN", "en-US", "en-GB", "en"]
    
    # Try to find a manually created English transcript
    for lang in manual_language_priority:
        try:
            transcript = transcripts.find_manually_created_transcript(lang).fetch()
            return transcript
        except:
            continue
    
    # Fall back to auto-generated transcripts
    auto_language_priority = ["en", "hi"]
    
    for lang in auto_language_priority:
        try:
            transcript = transcripts.find_generated_transcript(lang).fetch()
            return transcript
        except:
            continue
    
    # If we get here, try any available transcript (for robustness)
    try:
        transcript = transcripts.find_transcript(["en", "en-IN", "en-US", "en-GB", "hi"])
        return transcript.fetch()
    except:
        pass
    
    # No transcript available - raise with helpful error message
    raise ValueError(
        f"No English transcript available for video {video_id}. "
        "The video either has no captions or only has transcripts in other languages."
    )


## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url: str) -> str:
    """
    Extract and concatenate transcript from a YouTube URL.
    
    Args:
        youtube_video_url: Full YouTube URL (https://www.youtube.com/watch?v=VIDEO_ID)
    
    Returns:
        str: Concatenated transcript text
    
    Raises:
        ValueError: If URL is invalid or no transcript available
        Exception: For API errors
    """
    try:
        video_id = youtube_video_url.split("=")[1]
    except IndexError:
        raise ValueError("Invalid YouTube URL format. Use: https://www.youtube.com/watch?v=VIDEO_ID")
    
    try:
        transcript_data = fetch_best_transcript(video_id)
        transcript = " ".join(entry.text for entry in transcript_data)
        return transcript
    except Exception as e:
        raise e
    
## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):
    if not api_key:
        return "Missing `GOOGLE_API_KEY`: cannot call Gemini API. Add your key to `.env` or set the environment variable and restart."

    import time
    max_retries = 3
    retry_delay = 6  # Start with 6 seconds
    
    for attempt in range(max_retries):
        try:
            model=genai.GenerativeModel("gemini-2.5-flash")
            response=model.generate_content(prompt+transcript_text)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Rate limit hit. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return f"⚠️ Quota exceeded after {max_retries} retries. Free tier limit reached. Please:\n\n1. Wait a minute and try again\n2. Upgrade to a paid Google Cloud plan for higher limits\n3. Use a different API key\n\nError: {error_msg}"
            else:
                return f"Error: {error_msg}"
    
    return "Unexpected error generating summary."

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = youtube_link.split("=")[1]
        print(video_id)
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width=400)
    except:
        st.error("Invalid YouTube URL. Please use the format: https://www.youtube.com/watch?v=VIDEO_ID")

if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.error("Please enter a YouTube URL first.")
    else:
        try:
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                st.markdown("## Detailed Notes:")
                st.write(summary)
        except ValueError as e:
            st.error(f"Transcript unavailable: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                st.error("Video not found. Please check the YouTube URL.")
            else:
                st.error(f"Error extracting transcript: {error_msg}")






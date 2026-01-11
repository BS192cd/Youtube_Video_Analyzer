import streamlit as st
from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai
import json
import time

from youtube_transcript_api import YouTubeTranscriptApi

# Read API key from environment (or sing, show a friendly Streamlit message
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.warning("`GOOGLE_API_KEY` not found. Create a `.env` file or set the environment variable with your Google API key.")
else:
    genai.configure(api_key=api_key)

prompt="""You are YouTube video summarizer. Return a strict JSON object (no markdown, no extra text) with this exact schema:
{
  "title": "Brief title of the video content",
  "overview": "2-3 sentence overview of the video",
  "key_points": ["point 1", "point 2", "point 3", "..."],
  "conclusion": "Brief conclusion or takeaway"
}

Summarize the given transcript within 250 words total. Return ONLY valid JSON, nothing else.

Transcript: """


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
    
## JSON parsing and validation helpers
def parse_json_response(response_text: str) -> dict:
    """
    Parse and validate JSON response from Gemini.
    
    Schema:
    {
      "title": string,
      "overview": string,
      "key_points": [string],
      "conclusion": string
    }
    
    Args:
        response_text: Raw response from Gemini
    
    Returns:
        dict: Validated JSON with required fields
    
    Raises:
        ValueError: If JSON is invalid or missing required fields
    """
    required_fields = ["title", "overview", "key_points", "conclusion"]
    
    try:
        # Parse JSON (handle potential markdown code blocks)
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        json_data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from Gemini: {str(e)}\n\nRaw response:\n{response_text[:200]}")
    
    # Validate required fields
    missing_fields = [field for field in required_fields if field not in json_data]
    if missing_fields:
        raise ValueError(f"Missing required JSON fields: {', '.join(missing_fields)}")
    
    # Validate key_points is a list
    if not isinstance(json_data.get("key_points"), list):
        raise ValueError("'key_points' must be a list of strings")
    
    return json_data


def format_json_summary(json_data: dict) -> str:
    """
    Convert structured JSON summary to readable text format.
    Maintains backward compatibility with text-based display.
    
    Args:
        json_data: Validated JSON summary dictionary
    
    Returns:
        str: Formatted readable summary
    """
    output = []
    
    # Title
    if json_data.get("title"):
        output.append(f"**{json_data['title']}**\n")
    
    # Overview
    if json_data.get("overview"):
        output.append(f"{json_data['overview']}\n")
    
    # Key Points
    if json_data.get("key_points") and isinstance(json_data["key_points"], list):
        output.append("**Key Points:**")
        for point in json_data["key_points"]:
            output.append(f"• {point}")
        output.append("")
    
    # Conclusion
    if json_data.get("conclusion"):
        output.append(f"**Conclusion:**\n{json_data['conclusion']}")
    
    return "\n".join(output)
    
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

## Hierarchical summarization with quota-aware batching
def chunk_and_summarize(text: str) -> str:
    """
    Hierarchical batch summarization to minimize API calls.
    
    Strategy:
    1. Split transcript into ~30,000 character chunks
    2. Group chunks into batches (computed to stay within 8 API call limit)
    3. Summarize each batch with ONE API call per batch
    4. Final pass: consolidate all batch summaries into one
    5. Track and abort early if quota would be exceeded
    
    Quota-aware: Limits total Gemini calls to <= 8 per run.
    
    Stores metadata in st.session_state for UI display.
    
    Args:
        text: Full transcript text
    
    Returns:
        dict: Final JSON summary or None if error
    """
    start_time = time.time()
    chunk_size = 30000  # Increased from 8k to 30k for fewer chunks
    max_api_calls = 8
    
    # Step 1: Split into chunks while preserving sentence boundaries
    chunks = []
    current_chunk = ""
    sentences = text.split(". ")
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # If only one chunk, summarize directly
    if len(chunks) <= 1:
        response = generate_gemini_content(text, prompt)
        try:
            result = parse_json_response(response)
            # Store metadata
            elapsed = time.time() - start_time
            st.session_state.processing_metadata = {
                "transcript_chars": len(text),
                "num_chunks": len(chunks),
                "num_batches": 1,
                "api_calls_used": 1,
                "api_calls_max": max_api_calls,
                "elapsed_seconds": round(elapsed, 2)
            }
            return result
        except ValueError as e:
            st.error(f"Failed to parse summary: {str(e)}")
            return None
    
    # Step 2: Calculate batching strategy to stay within quota
    # Reserve 1 call for final pass, rest for batch summarization
    max_batches = max_api_calls - 1
    
    # Calculate chunks per batch needed to fit within max_batches
    num_chunks = len(chunks)
    chunks_per_batch = max(1, (num_chunks + max_batches - 1) // max_batches)
    
    # Calculate actual number of batches and estimated API calls
    num_batches = (num_chunks + chunks_per_batch - 1) // chunks_per_batch
    estimated_calls = num_batches + 1  # batches + 1 final call
    
    # Step 3: Quota-aware guard - abort if we'd exceed limit
    if estimated_calls > max_api_calls:
        error_msg = f"⚠️ Quota Alert: This transcript ({len(text):,} chars) would require {estimated_calls} API calls, but limit is {max_api_calls}. Transcript too long for free tier."
        st.error(error_msg)
        return None
    
    # Step 4: Create batches from chunks
    batches = []
    for i in range(0, num_chunks, chunks_per_batch):
        batch = chunks[i:i+chunks_per_batch]
        batches.append(batch)
    
    # Step 5: Summarize each batch with ONE API call per batch
    batch_summaries = []
    for i, batch in enumerate(batches):
        batch_text = "\n\n".join(batch)
        st.info(f"📝 Summarizing batch {i+1}/{len(batches)} — API call {i+1}/{estimated_calls}")
        batch_response = generate_gemini_content(batch_text, prompt)
        try:
            batch_json = parse_json_response(batch_response)
            batch_summaries.append(batch_json)
        except ValueError as e:
            st.error(f"Failed to parse batch {i+1} summary: {str(e)}")
            return None
    
    # Step 6: Final consolidation pass
    # Convert batch JSONs back to text for final consolidation
    batch_texts = []
    for batch_json in batch_summaries:
        batch_text = f"Title: {batch_json.get('title', '')}\nOverview: {batch_json.get('overview', '')}\nKey Points: {', '.join(batch_json.get('key_points', []))}"
        batch_texts.append(batch_text)
    
    combined_summaries = "\n\n".join(batch_texts)
    final_prompt = """You are a YouTube video summarizer. You will be taking multiple batch summaries
and creating one final, coherent summary of the entire video. Consolidate the key points,
eliminate redundancy, and maintain a logical flow. 

Return a strict JSON object (no markdown, no extra text) with this exact schema:
{
  "title": "Brief title of the entire video",
  "overview": "2-3 sentence overview of the whole video",
  "key_points": ["point 1", "point 2", "point 3", "..."],
  "conclusion": "Brief conclusion or main takeaway"
}

Keep the summary within 250 words total. Return ONLY valid JSON, nothing else.

Consolidated batch summaries: """
    
    st.info(f"🔄 Generating final consolidated summary — API call {num_batches+1}/{estimated_calls}")
    final_response = generate_gemini_content(combined_summaries, final_prompt)
    
    try:
        final_json = parse_json_response(final_response)
    except ValueError as e:
        st.error(f"Failed to parse final summary: {str(e)}")
        return None
    
    elapsed = time.time() - start_time
    st.success(f"✅ Summary complete! Used {estimated_calls}/{max_api_calls} API calls.")
    
    # Store metadata for UI display
    st.session_state.processing_metadata = {
        "transcript_chars": len(text),
        "num_chunks": num_chunks,
        "num_batches": num_batches,
        "api_calls_used": estimated_calls,
        "api_calls_max": max_api_calls,
        "elapsed_seconds": round(elapsed, 2)
    }
    
    return final_json

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
                summary_result = chunk_and_summarize(transcript_text)
                if summary_result:
                    # Format JSON summary for display
                    if isinstance(summary_result, dict):
                        formatted_summary = format_json_summary(summary_result)
                    else:
                        formatted_summary = str(summary_result)
                    
                    st.markdown("## Detailed Notes:")
                    st.markdown(formatted_summary)
                    
                    # Export options
                    st.markdown("---")
                    st.subheader("📥 Export Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        json_str = json.dumps(summary_result, indent=2)
                        st.download_button(
                            label="📋 Download JSON",
                            data=json_str,
                            file_name="summary.json",
                            mime="application/json",
                            key="download_json"
                        )
                    
                    with col2:
                        markdown_str = formatted_summary
                        st.download_button(
                            label="📄 Download Markdown",
                            data=markdown_str,
                            file_name="summary.md",
                            mime="text/markdown",
                            key="download_markdown"
                        )
                    
                    # Processing metadata
                    if hasattr(st.session_state, 'processing_metadata'):
                        st.markdown("---")
                        st.subheader("⚙️ Processing Metadata")
                        meta = st.session_state.processing_metadata
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Transcript Length", f"{meta['transcript_chars']:,} chars")
                        with col2:
                            st.metric("Chunks Created", meta['num_chunks'])
                        with col3:
                            st.metric("Batches", meta['num_batches'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("API Calls Used", f"{meta['api_calls_used']}/{meta['api_calls_max']}")
                        with col2:
                            st.metric("Processing Time", f"{meta['elapsed_seconds']}s")
                        with col3:
                            st.metric("Status", "✅ Complete")
        except ValueError as e:
            st.error(f"Transcript unavailable: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                st.error("Video not found. Please check the YouTube URL.")
            else:
                st.error(f"Error extracting transcript: {error_msg}")






# YouTube Transcript to Detailed Notes Converter

A Streamlit web application that extracts transcripts from YouTube videos and generates concise, AI-powered summaries using Google's Gemini API.

## Features

✨ **Core Functionality**
- 🎥 Extract transcripts from any YouTube video with captions
- 📝 Automatic transcript fetching via YouTube Transcript API
- 🤖 AI-powered summarization using Google Gemini 2.5 Flash
- ⚡ Fast and lightweight processing
- 🎨 Clean, intuitive web interface built with Streamlit

**Advanced Features**
- 🔄 Automatic retry with exponential backoff for rate limiting
- ⚠️ Graceful error handling with user-friendly messages
- 🌍 Support for multiple languages (English and auto-detection)
- 📊 Real-time processing feedback

## Prerequisites

- **Python 3.8+** installed
- **Google API Key** with Gemini API access (free tier available)
- **YouTube Video** with available captions/transcripts

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/BS192cd/Youtube_Video_Analyzer.git
cd YTtanscriber
```

### 2. Create Virtual Environment (Recommended)
```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Set Up Your Google API Key

**Get your API key:**
1. Go to [Google AI Studio](https://ai.google.dev)
2. Click "Get API Key" and create a new API key
3. Enable the **Generative Language API** in Google Cloud Console

**Add the key to your project:**

Option A: Create a `.env` file (Recommended)
```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

Option B: Set environment variable in PowerShell
```powershell
$env:GOOGLE_API_KEY = "your_google_api_key_here"
```

**Important:** Never commit `.env` with real API keys to git. It's already in `.gitignore`.

## Usage

### Start the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### How to Use

1. **Enter YouTube URL** – Paste a YouTube video link in the input field
   - Accepted format: `https://www.youtube.com/watch?v=VIDEO_ID`

2. **View Video Thumbnail** – The video's thumbnail displays automatically

3. **Click "Get Detailed Notes"** – The app will:
   - Extract the video transcript
   - Send it to Google Gemini for summarization
   - Display a concise summary in bullet points

4. **View Results** – Read the AI-generated summary under "Detailed Notes"

### Example

```
Input: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Output: 
## Detailed Notes:
- The video features a classic 80s music video
- Notable for its iconic music and production
- Became a famous internet meme...
```

## API & Models

### YouTube Transcript API
- Extracts captions/transcripts from YouTube videos
- Supports multiple languages with fallback to available transcripts
- No API key required

### Google Gemini API
- **Model:** `gemini-2.5-flash` (latest, fast, cost-effective)
- **Free Tier Quota:** 10 requests per minute
- **Paid Plans:** Higher limits available with Google Cloud Billing

## Rate Limiting & Quotas

### Free Tier Limits
- **10 requests per minute** for text generation
- Resets each minute automatically

### Handling Rate Limits
The app includes automatic retry logic:
- 3 automatic retries with exponential backoff
- Waits 6-24 seconds between retries
- Clear user messaging during retries

### Solutions for Exceeded Quotas

**Option 1: Wait for Reset**
- Free tier limit resets every minute
- Wait ~60 seconds and try again

**Option 2: Upgrade to Paid Plan**
- Access [Google Cloud Console](https://console.cloud.google.com)
- Enable billing for significantly higher limits
- Pay-as-you-go pricing (~$0.01-0.05 per request depending on model)

**Option 3: Use Multiple API Keys**
- Rotate between different API keys to distribute requests
- Each key has its own quota

**Option 4: Implement Caching**
- Store previously summarized videos locally
- Avoid re-processing the same content

## Project Structure

```
YTtanscriber/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your actual API keys (in .gitignore)
├── .gitignore           # Excludes sensitive files from git
├── .venv/               # Virtual environment (local only)
└── README.md            # This file
```

## File Descriptions

### `app.py`
Main application file containing:
- YouTube transcript extraction function
- Gemini API integration with retry logic
- Streamlit UI components
- Error handling and validation

### `requirements.txt`
Python package dependencies:
```
youtube-transcript-api     # YouTube transcript extraction
streamlit                  # Web framework
google-generativeai        # Google Gemini API client
python-dotenv             # Environment variable management
pathlib                   # Path utilities
```

## Troubleshooting

### ❌ "GOOGLE_API_KEY not found"
**Problem:** The API key isn't loaded from `.env`

**Solutions:**
- Verify `.env` file exists in the project root
- Check the key format: `GOOGLE_API_KEY=your_key_here`
- Restart the Streamlit app after updating `.env`
- Ensure no quotes around the key value

### ❌ "404 models/gemini-2.5-flash is not found"
**Problem:** Model not available with your API key

**Solutions:**
- Verify Google Generative Language API is enabled
- Check API key has proper permissions
- Consider trying `gemini-2.0-flash` or `gemini-flash-latest`

### ❌ "Error extracting transcript"
**Problem:** Video doesn't have available transcripts

**Reasons:**
- Video doesn't have captions/subtitles
- Captions are disabled by creator
- Video is too new (transcripts take time to generate)

**Solution:** Try a different video with available captions

### ❌ "429 Quota exceeded"
**Problem:** You've hit the rate limit

**Solutions:**
- Wait 60 seconds for free tier limit to reset
- Upgrade to a paid Google Cloud plan
- Reduce request frequency
- Implement caching for duplicate requests

### ❌ "Invalid YouTube URL"
**Problem:** Wrong URL format

**Correct format:** `https://www.youtube.com/watch?v=VIDEO_ID`

**Don't use:** 
- Shortened URLs (`youtu.be/...`)
- Playlists or channel URLs
- Live stream URLs

## Performance Tips

1. **Optimize Transcript Length** – Shorter videos summarize faster
2. **Use Lite Models** – Consider `gemini-2.0-flash-lite` for faster processing
3. **Enable Caching** – Store results to avoid re-summarizing
4. **Batch Processing** – Process multiple videos with strategic delays
5. **Monitor Usage** – Check [Google Cloud Usage Dashboard](https://ai.dev/usage) regularly

## Cost Estimation (Paid Plans)

**Gemini 2.5 Flash Pricing (approximate):**
- Input: $0.075 per million tokens
- Output: $0.30 per million tokens

**Example:** 
- 1,000-word transcript: ~250 tokens
- 100 summaries: ~$0.002-0.003 total

## Security Best Practices

✅ **Do:**
- Keep `.env` file in `.gitignore`
- Use environment variables for secrets
- Rotate API keys regularly
- Monitor API usage and set up billing alerts
- Use dedicated API keys for this project

❌ **Don't:**
- Commit `.env` files with real keys
- Hardcode API keys in source code
- Share API keys in chat or email
- Use personal API keys for production

## Environment Variables

Create a `.env` file with:

```env
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional (for future enhancements)
# LOG_LEVEL=INFO
# CACHE_DIR=./cache
# MAX_RETRIES=3
```

## Future Enhancements

🚀 Planned features:
- [ ] Local caching of summaries
- [ ] Support for non-English transcripts
- [ ] Export summaries to PDF/Word
- [ ] Playlist processing
- [ ] Custom summarization templates
- [ ] Dark mode UI
- [ ] Audio transcription (non-YouTube)
- [ ] Multi-language support

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support & Resources

- 📚 [Streamlit Documentation](https://docs.streamlit.io)
- 🤖 [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- 📺 [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- 💳 [Google Cloud Console](https://console.cloud.google.com)
- ⚙️ [API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)

## Troubleshooting Checklist

- [ ] Virtual environment activated?
- [ ] Requirements installed (`pip install -r requirements.txt`)?
- [ ] `.env` file created with valid API key?
- [ ] Streamlit running (`streamlit run app.py`)?
- [ ] YouTube video has captions enabled?
- [ ] Not exceeded API quota (wait 1 minute)?
- [ ] Using correct YouTube URL format?

## Quick Start Commands

**Complete setup in 3 commands:**
```bash
pip install -r requirements.txt
cp .env.example .env
# (Edit .env with your API key)
streamlit run app.py
```

Then visit: `http://localhost:8501`

---

**Created:** December 2025  
**Repository:** [Youtube_Video_Analyzer](https://github.com/BS192cd/Youtube_Video_Analyzer)  
**Author:** BS192cd

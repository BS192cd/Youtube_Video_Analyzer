# YouTube Transcript to Detailed Notes Converter

A web application that extracts transcripts from YouTube videos and generates concise, AI-powered summaries using Google's Gemini API. Built with Streamlit for easy deployment and a simple user interface.

## Features

**Core Functionality**
- Extract transcripts from any YouTube video with captions
- Automatic transcript fetching via YouTube Transcript API
- AI-powered summarization using Google Gemini 2.5 Flash
- Fast and lightweight processing
- Clean, intuitive web interface built with Streamlit

**Advanced Features**
- Automatic retry with exponential backoff for rate limiting
- Graceful error handling with user-friendly messages
- Support for multiple languages with auto-detection fallback
- Real-time processing feedback during summarization

## Prerequisites

Before you get started, make sure you have:
- Python 3.8 or higher installed on your system
- A Google API Key with Gemini API access (free tier available)
- YouTube videos with available captions or transcripts

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/BS192cd/Youtube_Video_Analyzer.git
cd YTtanscriber
```

### Step 2: Create Virtual Environment (Recommended)
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

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### Getting Your Google API Key

1. Go to Google AI Studio at https://ai.google.dev
2. Click on "Get API Key" and create a new API key
3. Make sure the Generative Language API is enabled in your Google Cloud project

### Adding the API Key to Your Project

**Method 1: Using .env file (Recommended)**
```bash
cp .env.example .env
```

Then edit the `.env` file and add your key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

**Method 2: Set as environment variable in PowerShell**
```powershell
$env:GOOGLE_API_KEY = "your_google_api_key_here"
```

Important: Never commit your `.env` file with real API keys to git. The `.gitignore` file already excludes it.

## Usage

### Starting the Application
```bash
streamlit run app.py
```

The app will open automatically at http://localhost:8501

### How to Use the App

1. Paste a YouTube URL - Enter a YouTube video link in the format: https://www.youtube.com/watch?v=VIDEO_ID

2. View the thumbnail - The video's thumbnail will display automatically below the input

3. Extract and summarize - Click the "Get Detailed Notes" button to process the video

4. The app will:
   - Extract the video transcript
   - Send it to Google Gemini for summarization
   - Display the results as a concise summary

### Example Workflow

```
Input: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Output: 
Detailed Notes:
- Features a classic 80s music video production
- Notable for iconic music and memorable visuals
- Became a famous internet meme over the years
```

## API and Models Used

### YouTube Transcript API
- Extracts transcripts and captions from YouTube videos
- No API key required for this service
- Supports multiple languages with automatic fallback
- Free to use with no quotas

### Google Gemini API
- Model: gemini-2.5-flash (latest, fast, and cost-effective)
- Free tier: 10 requests per minute
- Paid plans available through Google Cloud with much higher limits

## Understanding Rate Limits and Quotas

### Free Tier Limitations
The free tier allows 10 requests per minute for text generation. This resets automatically every minute.

### When You Hit the Rate Limit
The app includes automatic retry logic that will:
- Attempt up to 3 retries automatically
- Wait between 6 and 24 seconds before each retry
- Show you a progress message during the wait
- Explain what to do if all retries fail

### Solutions When Quota is Exceeded

**Quick fix - Wait for reset:** The free tier quota resets every minute. If you hit the limit, wait about 60 seconds and try again.

**Upgrade to paid plan:** Visit your Google Cloud Console and enable billing. This gives you significantly higher limits. Pricing is generally around 0.01 to 0.05 dollars per request depending on the model.

**Use multiple API keys:** You can rotate between different API keys to distribute requests across multiple quotas.

**Implement caching:** Store previously summarized videos locally so you don't need to re-process them.

## Project Structure

Here's how the files are organized:
```
YTtanscriber/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python package dependencies
├── .env.example          # Template for environment variables
├── .env                  # Your API keys (in .gitignore)
├── .gitignore           # Files to exclude from git
├── .venv/               # Virtual environment folder (local only)
└── README.md            # This file
```

## What Each File Does

**app.py** - Contains the complete application with:
- YouTube transcript extraction logic
- Google Gemini API integration with retry handling
- Streamlit web interface components
- Error handling and input validation

**requirements.txt** - Lists all Python package dependencies:
- youtube-transcript-api for extracting transcripts
- streamlit for the web interface
- google-generativeai for Gemini API access
- python-dotenv for loading environment variables
- pathlib for file path handling

## Troubleshooting

### Problem: "GOOGLE_API_KEY not found"

This error means the app can't find your API key.

Solutions:
- Make sure you created a .env file in the project root directory
- Check that the file contains: GOOGLE_API_KEY=your_key_here
- Don't put quotes around your API key
- Restart the Streamlit app after updating the .env file
- Make sure there are no extra spaces in the key

### Problem: "404 models/gemini-2.5-flash is not found"

The model isn't available with your current API key setup.

Solutions:
- Verify you enabled the Generative Language API in Google Cloud Console
- Check that your API key has the necessary permissions
- Try using an older model like gemini-2.0-flash or gemini-flash-latest instead

### Problem: "Error extracting transcript"

The app couldn't get a transcript from the video.

Common reasons:
- The video doesn't have captions or subtitles
- The video creator disabled captions
- The video is too new and captions haven't been auto-generated yet

Solution: Try with a different video that has visible captions

### Problem: "429 Quota exceeded"

You've hit the rate limit for the free tier.

Solutions:
- Wait about 60 seconds for the free tier limit to reset
- Upgrade your Google Cloud account to a paid plan for higher limits
- Make fewer requests or space them out over time
- Cache results from previous summaries to avoid duplicate requests

### Problem: "Invalid YouTube URL"

The URL format isn't recognized.

Use this format: https://www.youtube.com/watch?v=VIDEO_ID

Don't use these formats:
- Shortened URLs from youtu.be
- Playlist URLs
- Channel URLs
- Live stream URLs

## Performance Tips

- Shorter videos will process much faster than long ones
- Consider using lighter models like gemini-2.0-flash-lite if speed is important
- Store results locally to avoid re-summarizing the same videos
- Space out multiple requests if processing several videos at once
- Check your usage on the Google Cloud dashboard regularly

## Cost Estimation for Paid Plans

Google charges based on input and output tokens. Here's a rough estimate:

Gemini 2.5 Flash pricing:
- Input: around 0.075 dollars per million tokens
- Output: around 0.30 dollars per million tokens

A typical example:
- Average YouTube transcript: about 250 tokens
- Processing 100 different videos: roughly 0.002 to 0.003 dollars total

## Security and Best Practices

Do keep in mind:
- Always keep your .env file in .gitignore
- Use environment variables for any sensitive information
- Rotate your API keys periodically
- Monitor your API usage and set up billing alerts
- Use a dedicated API key just for this project

Don't do these things:
- Don't commit .env files with real API keys to git
- Don't hardcode API keys anywhere in your source code
- Don't share API keys in emails, chat, or other communication channels
- Don't use personal API keys for production applications

## Environment Variables

Create a .env file in the project root with the following:

```
GOOGLE_API_KEY=your_api_key_here
```

Optional variables for future features:
```
LOG_LEVEL=INFO
CACHE_DIR=./cache
MAX_RETRIES=3
```

## Possible Future Features

Things we might add later:
- Caching of summaries to avoid re-processing
- Support for non-English transcripts
- Export summaries to PDF or Word format
- Processing entire playlists at once
- Custom templates for different summary styles
- Dark mode for the user interface
- Ability to transcribe audio files directly
- Better support for multiple languages

## Contributing

We welcome contributions from anyone interested in improving this project:
1. Fork the repository on GitHub
2. Create a new branch for your feature
3. Make your changes and commit them with clear messages
4. Push your branch to your fork
5. Open a pull request with a description of your changes

## License

This project is open source and available under the MIT License.

## Resources and Help

If you need more information:
- Streamlit docs: https://docs.streamlit.io
- Google Gemini API docs: https://ai.google.dev/gemini-api/docs
- YouTube Transcript API: https://github.com/jdepoix/youtube-transcript-api
- Google Cloud Console: https://console.cloud.google.com
- Information about API rate limits: https://ai.google.dev/gemini-api/docs/rate-limits

## Quick Setup Checklist

Before getting started, verify:
- Virtual environment is activated
- All requirements installed (pip install -r requirements.txt)
- .env file created with your API key
- Streamlit is running (streamlit run app.py)
- YouTube video has captions available
- API quota hasn't been exceeded
- Using correct YouTube URL format

## Quick Start

Complete setup in just a few commands:
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
streamlit run app.py
```

Then open your browser to http://localhost:8501

---

**Created:** December 2025
**Repository:** Github.com/BS192cd/Youtube_Video_Analyzer
**Original Author:** BS192cd

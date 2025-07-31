# Backend Server Setup Guide

The Map Memoir backend server provides AI story generation and text-to-speech functionality. Due to disk space constraints, here's a simplified setup guide.

## 🔧 Requirements

- Python 3.8+ 
- At least 2GB of free disk space
- Google Gemini API key (for AI story generation)

## 🚀 Quick Setup

### 1. Install Python Dependencies (Minimal)

```bash
cd server
python3 -m venv venv
source venv/bin/activate

# Install core dependencies only
pip install flask flask-cors python-dotenv google-generativeai openai
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Update `.env` with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional, for alternative TTS
```

### 3. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## 🎯 Getting API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### OpenAI API Key (Optional)
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key to your `.env` file

## ⚡ Minimal Server (If Full Setup Fails)

If you encounter disk space issues, you can run a minimal version:

```bash
# Install only essential packages
pip install flask flask-cors python-dotenv requests

# Run minimal server
python -c "
from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/generate-story', methods=['POST'])
def generate_story():
    return jsonify({
        'story': 'This is a demo story. The backend server is running in minimal mode.',
        'audio_url': None
    })

app.run(debug=True, port=5000)
"
```

## 🔍 Testing

1. Start the frontend: `cd frontend && npm run dev`
2. Start the backend: `cd server && python app.py`
3. Visit `http://localhost:3000`
4. Look for "Server: Online" indicator in the UI

## 📝 Notes

- The TTS dependencies (like `TTS` package) are large and optional
- You can use OpenAI's API for text-to-speech as an alternative
- The frontend will work with limited functionality even if the backend is offline

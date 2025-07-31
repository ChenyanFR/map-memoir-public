from flask import Blueprint, request, send_file, jsonify
from services.sota_tts_service import generate_story_audio
from dotenv import load_dotenv
import tempfile
import os
import base64
import asyncio

load_dotenv()
audio_bp = Blueprint('audio', __name__)

THEME_VOICE_MAP = {
    "fairy tale": "tts_models/en/ljspeech/tacotron2-DDC",
    "documentary": "tts_models/en/ljspeech/glow-tts",
    "sci-fi": "tts_models/en/ljspeech/tacotron2-DDC",
    "mystery": "tts_models/en/ljspeech/tacotron2-DDC"
}

@audio_bp.route("/generate_audio", methods=["POST", "OPTIONS"])
def generate_audio():
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    script = data.get("script")
    theme = data.get("theme", "documentary")

    if not script:
        return jsonify({"error": "Script is required"}), 400

    try:
        model_name = THEME_VOICE_MAP.get(theme.lower(), "tts_models/en/ljspeech/tacotron2-DDC")

        tts_result = asyncio.run(generate_story_audio(text=script, theme=theme))
        if not tts_result or "audio_content" not in tts_result:
            return jsonify({"error": "Audio generation failed"}), 500

        audio_bytes = base64.b64decode(tts_result["audio_content"])
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_bytes)
        tmp.close()

        print("Generated audio file:", tmp.name)
        return send_file(tmp.name, mimetype="audio/wav", as_attachment=False)

    except Exception as e:
        print("❌ Error generating audio:", e)
        return jsonify({"error": "Internal Server Error"}), 500

import os
from TTS.api import TTS
from datetime import datetime

theme_to_model = {
    "fairy tale": "tts_models/en/ljspeech/tacotron2-DDC",
    "documentary": "tts_models/en/vctk/vits",
    "adventure": "tts_models/en/ljspeech/tacotron2-DDC_ph",
    "default": "tts_models/en/ljspeech/tacotron2-DDC"
}

def generate_voice_file(text, theme="default"):
    model_name = theme_to_model.get(theme.lower(), theme_to_model["default"])
    tts = TTS(model_name=model_name)
    
    os.makedirs("story_audio", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"story_audio/story_{timestamp}.wav"
    
    tts.tts_to_file(text=text, file_path=file_path)
    return file_path

from TTS.api import TTS

def generate_voice(script, theme):
    model_map = {
        "documentary": "tts_models/en/ljspeech/tacotron2-DDC",
        "fairy tale": "tts_models/en/ljspeech/glow-tts",
        "fantasy": "tts_models/en/vctk/vits",
    }
    model_name = model_map.get(theme.lower(), "tts_models/en/ljspeech/tacotron2-DDC")
    tts = TTS(model_name=model_name)
    output_path = f"static/audio/story_{theme.replace(' ', '_')}.wav"
    tts.tts_to_file(text=script, file_path=output_path)
    return output_path

"""
Speech Service for Map Memoir
Handles Google Cloud Speech-to-Text and Text-to-Speech services
"""

import os
import base64
import io
from typing import Optional, Dict, Any, List
from google.cloud import speech
from google.cloud import texttospeech
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Pydantic models
class SpeechToTextResult(BaseModel):
    transcript: str = Field(description="Transcribed text")
    confidence: float = Field(description="Confidence score")
    language_code: str = Field(description="Detected language code")

class TextToSpeechResult(BaseModel):
    audio_content: str = Field(description="Base64 encoded audio content")
    content_type: str = Field(description="Audio content type")

class SpeechService:
    def __init__(self):
        """Initialize Google Cloud Speech services"""
        try:
            # Initialize Speech-to-Text client
            self.speech_client = speech.SpeechClient()
            print("✅ Google Cloud Speech-to-Text client initialized")
        except Exception as e:
            self.speech_client = None
            print(f"⚠️ Speech-to-Text client initialization failed: {e}")
        
        try:
            # Initialize Text-to-Speech client
            self.tts_client = texttospeech.TextToSpeechClient()
            print("✅ Google Cloud Text-to-Speech client initialized")
        except Exception as e:
            self.tts_client = None
            print(f"⚠️ Text-to-Speech client initialization failed: {e}")
    
    def transcribe_audio(self, audio_content: bytes, 
                        language_code: str = "en-US",
                        sample_rate: int = 16000,
                        audio_format: str = "WEBM_OPUS") -> Optional[SpeechToTextResult]:
        """
        Transcribe audio content to text
        
        Args:
            audio_content: Audio data as bytes
            language_code: Language code (e.g., "en-US", "zh-CN")
            sample_rate: Audio sample rate in Hz
            audio_format: Audio encoding format
            
        Returns:
            SpeechToTextResult or None if transcription fails
        """
        if not self.speech_client:
            print("❌ Speech-to-Text client not available")
            return None
        
        try:
            # Map audio format to Google Cloud enum
            encoding_map = {
                "WEBM_OPUS": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "LINEAR16": speech.RecognitionConfig.AudioEncoding.LINEAR16,
                "FLAC": speech.RecognitionConfig.AudioEncoding.FLAC,
                "MULAW": speech.RecognitionConfig.AudioEncoding.MULAW,
                "AMR": speech.RecognitionConfig.AudioEncoding.AMR,
                "AMR_WB": speech.RecognitionConfig.AudioEncoding.AMR_WB,
                "OGG_OPUS": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                "MP3": speech.RecognitionConfig.AudioEncoding.MP3,
            }
            
            encoding = encoding_map.get(audio_format, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=sample_rate,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model="latest_long"
            )
            
            # Create audio object
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Perform the transcription
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Process results
            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]
                
                return SpeechToTextResult(
                    transcript=alternative.transcript,
                    confidence=alternative.confidence,
                    language_code=language_code
                )
            else:
                print("❌ No transcription results found")
                return None
                
        except Exception as e:
            print(f"Speech-to-Text error: {str(e)}")
            return None
    
    def transcribe_audio_base64(self, audio_base64: str, 
                               language_code: str = "en-US",
                               sample_rate: int = 16000,
                               audio_format: str = "WEBM_OPUS") -> Optional[SpeechToTextResult]:
        """
        Transcribe base64 encoded audio to text
        
        Args:
            audio_base64: Base64 encoded audio data
            language_code: Language code
            sample_rate: Audio sample rate
            audio_format: Audio encoding format
            
        Returns:
            SpeechToTextResult or None
        """
        try:
            # Decode base64 audio
            audio_content = base64.b64decode(audio_base64)
            return self.transcribe_audio(audio_content, language_code, sample_rate, audio_format)
            
        except Exception as e:
            print(f"Base64 decode error: {str(e)}")
            return None
    
    def synthesize_speech(self, text: str, 
                         language_code: str = "en-US",
                         voice_gender: str = "NEUTRAL",
                         audio_format: str = "MP3") -> Optional[TextToSpeechResult]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            language_code: Language code (e.g., "en-US", "zh-CN")
            voice_gender: Voice gender ("NEUTRAL", "MALE", "FEMALE")
            audio_format: Audio format ("MP3", "WAV", "OGG")
            
        Returns:
            TextToSpeechResult or None if synthesis fails
        """
        if not self.tts_client:
            print("❌ Text-to-Speech client not available")
            return None
        
        try:
            # Prepare input text
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice_gender_map = {
                "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL,
                "MALE": texttospeech.SsmlVoiceGender.MALE,
                "FEMALE": texttospeech.SsmlVoiceGender.FEMALE
            }
            
            gender = voice_gender_map.get(voice_gender.upper(), texttospeech.SsmlVoiceGender.NEUTRAL)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=gender
            )
            
            # Configure audio format
            audio_format_map = {
                "MP3": texttospeech.AudioEncoding.MP3,
                "WAV": texttospeech.AudioEncoding.LINEAR16,
                "OGG": texttospeech.AudioEncoding.OGG_OPUS
            }
            
            encoding = audio_format_map.get(audio_format.upper(), texttospeech.AudioEncoding.MP3)
            
            audio_config = texttospeech.AudioConfig(audio_encoding=encoding)
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Encode to base64
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            # Determine content type
            content_type_map = {
                "MP3": "audio/mpeg",
                "WAV": "audio/wav",
                "OGG": "audio/ogg"
            }
            
            content_type = content_type_map.get(audio_format.upper(), "audio/mpeg")
            
            return TextToSpeechResult(
                audio_content=audio_base64,
                content_type=content_type
            )
            
        except Exception as e:
            print(f"Text-to-Speech error: {str(e)}")
            return None
    
    def get_available_voices(self, language_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of available voices for synthesis
        
        Args:
            language_code: Optional language filter
            
        Returns:
            List of available voices
        """
        if not self.tts_client:
            print("❌ Text-to-Speech client not available")
            return []
        
        try:
            voices = self.tts_client.list_voices(language_code=language_code)
            
            voice_list = []
            for voice in voices.voices:
                voice_info = {
                    "name": voice.name,
                    "language_codes": list(voice.language_codes),
                    "ssml_gender": voice.ssml_gender.name,
                    "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            print(f"Get voices error: {str(e)}")
            return []
    
    def transcribe_long_audio(self, audio_content: bytes,
                             language_code: str = "en-US",
                             audio_format: str = "WEBM_OPUS") -> Optional[SpeechToTextResult]:
        """
        Transcribe long audio files using long-running recognition
        
        Args:
            audio_content: Audio data as bytes
            language_code: Language code
            audio_format: Audio encoding format
            
        Returns:
            SpeechToTextResult or None
        """
        if not self.speech_client:
            print("❌ Speech-to-Text client not available")
            return None
        
        try:
            # For long audio, we might need to use long_running_recognize
            # This is a simplified version - in production, you'd upload to Cloud Storage
            
            encoding_map = {
                "WEBM_OPUS": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "LINEAR16": speech.RecognitionConfig.AudioEncoding.LINEAR16,
                "FLAC": speech.RecognitionConfig.AudioEncoding.FLAC,
                "MP3": speech.RecognitionConfig.AudioEncoding.MP3,
            }
            
            encoding = encoding_map.get(audio_format, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS)
            
            config = speech.RecognitionConfig(
                encoding=encoding,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model="latest_long"
            )
            
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Use long running recognize for audio > 1 minute
            operation = self.speech_client.long_running_recognize(config=config, audio=audio)
            
            print("⏳ Processing long audio file...")
            response = operation.result(timeout=300)  # 5 minute timeout
            
            # Combine all transcripts
            full_transcript = ""
            total_confidence = 0
            result_count = 0
            
            for result in response.results:
                alternative = result.alternatives[0]
                full_transcript += alternative.transcript + " "
                total_confidence += alternative.confidence
                result_count += 1
            
            if result_count > 0:
                average_confidence = total_confidence / result_count
                return SpeechToTextResult(
                    transcript=full_transcript.strip(),
                    confidence=average_confidence,
                    language_code=language_code
                )
            
            return None
            
        except Exception as e:
            print(f"Long audio transcription error: {str(e)}")
            return None

# Global instance
speech_service = SpeechService()

# Convenience functions
def transcribe_audio(audio_content: bytes, language_code: str = "en-US") -> Optional[Dict[str, Any]]:
    """Transcribe audio to text"""
    result = speech_service.transcribe_audio(audio_content, language_code)
    return result.dict() if result else None

def transcribe_audio_base64(audio_base64: str, language_code: str = "en-US") -> Optional[Dict[str, Any]]:
    """Transcribe base64 audio to text"""
    result = speech_service.transcribe_audio_base64(audio_base64, language_code)
    return result.dict() if result else None

def synthesize_speech(text: str, language_code: str = "en-US", voice_gender: str = "NEUTRAL") -> Optional[Dict[str, Any]]:
    """Convert text to speech"""
    result = speech_service.synthesize_speech(text, language_code, voice_gender)
    return result.dict() if result else None

def get_available_voices(language_code: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get available voices"""
    return speech_service.get_available_voices(language_code)
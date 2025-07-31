"""
SOTA Text-to-Speech Service
Supports multiple state-of-the-art TTS models with fallback to Google TTS
"""

import os
import requests
import base64
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class TTSQuality(Enum):
    """TTS Quality levels"""
    BASIC = "basic"          # Google TTS
    HIGH = "high"           # ElevenLabs standard
    PREMIUM = "premium"     # ElevenLabs with cloning
    ULTRA = "ultra"         # Custom fine-tuned models

class TTSProvider(Enum):
    """Supported TTS providers"""
    GOOGLE = "google"
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    AZURE = "azure"
    TORTOISE = "tortoise"

@dataclass
class VoiceConfig:
    """Voice configuration for TTS"""
    provider: TTSProvider
    voice_id: str
    model: str
    emotion: Optional[str] = None
    speed: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.75

@dataclass
class TTSResult:
    """TTS generation result"""
    audio_content: bytes
    content_type: str
    provider: TTSProvider
    voice_id: str
    duration_ms: int
    cost_estimate: float

class ElevenLabsService:
    """ElevenLabs TTS integration"""
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        self.available = bool(self.api_key)
        
        # Predefined voices for different story types
        self.voice_presets = {
            "adventure": "21m00Tcm4TlvDq8ikWAM",  # Rachel - energetic
            "documentary": "2EiwWnXFnvU5JabPnv8n",  # Clyde - authoritative
            "romantic": "ThT5KcBeYPX3keUQqHPh",   # Dorothy - warm
            "mystery": "onwK4e9ZLuTAKqWW03F9",    # Daniel - dramatic
            "family": "pFZP5JQG7iQjIQuC4Bku"     # Lily - friendly
        }
    
    async def synthesize_speech(self, text: str, voice_config: VoiceConfig) -> Optional[TTSResult]:
        """Generate speech using ElevenLabs API"""
        if not self.available:
            return None
        
        url = f"{self.base_url}/text-to-speech/{voice_config.voice_id}"
        
        payload = {
            "text": text,
            "model_id": voice_config.model,
            "voice_settings": {
                "stability": voice_config.stability,
                "similarity_boost": voice_config.similarity_boost,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        
                        return TTSResult(
                            audio_content=audio_content,
                            content_type="audio/mpeg",
                            provider=TTSProvider.ELEVENLABS,
                            voice_id=voice_config.voice_id,
                            duration_ms=len(audio_content) // 32,  # Estimate
                            cost_estimate=len(text) * 0.0001  # Rough estimate
                        )
                    else:
                        print(f"ElevenLabs API error: {response.status}")
                        return None
        except Exception as e:
            print(f"ElevenLabs synthesis error: {e}")
            return None
    
    def get_voice_for_theme(self, theme: str) -> str:
        """Get appropriate voice ID for story theme"""
        return self.voice_presets.get(theme.lower(), self.voice_presets["documentary"])

class OpenAITTSService:
    """OpenAI TTS integration"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.available = bool(self.api_key)
        
        # OpenAI TTS voices
        self.voices = {
            "alloy": "balanced, neutral",
            "echo": "male, expressive", 
            "fable": "male, dramatic",
            "onyx": "male, deep",
            "nova": "female, energetic",
            "shimmer": "female, warm"
        }
    
    async def synthesize_speech(self, text: str, voice_config: VoiceConfig) -> Optional[TTSResult]:
        """Generate speech using OpenAI TTS API"""
        if not self.available:
            return None
        
        url = "https://api.openai.com/v1/audio/speech"
        
        payload = {
            "model": voice_config.model or "tts-1-hd",
            "input": text,
            "voice": voice_config.voice_id or "nova",
            "response_format": "mp3",
            "speed": voice_config.speed
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        
                        return TTSResult(
                            audio_content=audio_content,
                            content_type="audio/mpeg",
                            provider=TTSProvider.OPENAI,
                            voice_id=voice_config.voice_id,
                            duration_ms=len(audio_content) // 32,
                            cost_estimate=len(text) * 0.000015  # OpenAI pricing
                        )
                    else:
                        print(f"OpenAI TTS API error: {response.status}")
                        return None
        except Exception as e:
            print(f"OpenAI TTS synthesis error: {e}")
            return None

class SOTATTSService:
    """Main SOTA TTS service with multiple providers and fallback"""
    
    def __init__(self):
        # Initialize all providers
        self.elevenlabs = ElevenLabsService()
        self.openai_tts = OpenAITTSService()
        
        # Import existing Google TTS service
        try:
            from services.speech_service import speech_service
            self.google_tts = speech_service
            print("✅ Google TTS available as fallback")
        except ImportError:
            self.google_tts = None
            print("⚠️ Google TTS not available")
        
        # Provider priority order
        self.provider_priority = [
            TTSProvider.ELEVENLABS,  # Best quality
            TTSProvider.OPENAI,      # Good quality, reliable
            TTSProvider.GOOGLE       # Fallback
        ]
        
        print("🎙️ SOTA TTS Service initialized")
        print(f"   ElevenLabs: {'✅' if self.elevenlabs.available else '❌'}")
        print(f"   OpenAI TTS: {'✅' if self.openai_tts.available else '❌'}")
        print(f"   Google TTS: {'✅' if self.google_tts else '❌'}")
    
    def get_optimal_config(self, theme: str, quality: TTSQuality) -> VoiceConfig:
        """Get optimal voice configuration for theme and quality"""
        
        if quality == TTSQuality.PREMIUM and self.elevenlabs.available:
            return VoiceConfig(
                provider=TTSProvider.ELEVENLABS,
                voice_id=self.elevenlabs.get_voice_for_theme(theme),
                model="eleven_multilingual_v2",
                emotion=theme,
                stability=0.7,
                similarity_boost=0.8
            )
        
        elif quality == TTSQuality.HIGH and self.openai_tts.available:
            voice_map = {
                "adventure": "nova",
                "documentary": "onyx", 
                "romantic": "shimmer",
                "mystery": "fable",
                "family": "alloy"
            }
            return VoiceConfig(
                provider=TTSProvider.OPENAI,
                voice_id=voice_map.get(theme, "nova"),
                model="tts-1-hd",
                speed=1.0
            )
        
        else:  # BASIC quality or fallback
            return VoiceConfig(
                provider=TTSProvider.GOOGLE,
                voice_id="en-US-Neural2-F",
                model="google_tts"
            )
    
    async def synthesize_speech(self, text: str, theme: str = "documentary", 
                              quality: TTSQuality = TTSQuality.HIGH) -> Optional[TTSResult]:
        """
        Synthesize speech with automatic provider selection and fallback
        
        Args:
            text: Text to synthesize
            theme: Story theme (adventure, documentary, romantic, etc.)
            quality: Desired quality level
            
        Returns:
            TTSResult with audio and metadata
        """
        
        # Get optimal configuration
        config = self.get_optimal_config(theme, quality)
        
        # Try providers in order of preference
        providers_to_try = [
            (config.provider, config),
            # Add fallback configs
            *[(p, self.get_optimal_config(theme, TTSQuality.BASIC)) 
              for p in self.provider_priority if p != config.provider]
        ]
        
        for provider, voice_config in providers_to_try:
            try:
                if provider == TTSProvider.ELEVENLABS and self.elevenlabs.available:
                    result = await self.elevenlabs.synthesize_speech(text, voice_config)
                    if result:
                        print(f"✅ Generated audio using ElevenLabs")
                        return result
                
                elif provider == TTSProvider.OPENAI and self.openai_tts.available:
                    result = await self.openai_tts.synthesize_speech(text, voice_config)
                    if result:
                        print(f"✅ Generated audio using OpenAI TTS")
                        return result
                
                elif provider == TTSProvider.GOOGLE and self.google_tts:
                    # Convert to Google TTS format
                    voice_gender = "FEMALE" if "female" in theme else "NEUTRAL"
                    google_result = self.google_tts.synthesize_speech(
                        text=text,
                        language_code="en-US",
                        voice_gender=voice_gender,
                        audio_format="MP3"
                    )
                    
                    if google_result:
                        audio_content = base64.b64decode(google_result.audio_content)
                        result = TTSResult(
                            audio_content=audio_content,
                            content_type="audio/mpeg",
                            provider=TTSProvider.GOOGLE,
                            voice_id=voice_gender,
                            duration_ms=len(audio_content) // 32,
                            cost_estimate=0.0  # Google pricing varies
                        )
                        print(f"✅ Generated audio using Google TTS (fallback)")
                        return result
                        
            except Exception as e:
                print(f"❌ Provider {provider} failed: {e}")
                continue
        
        print(f"❌ All TTS providers failed for text: {text[:50]}...")
        return None
    
    def get_available_voices(self, provider: TTSProvider | None = None) -> Dict[str, List[str]]:
        """Get available voices for each provider"""
        voices = {}
        
        if not provider or provider == TTSProvider.ELEVENLABS:
            if self.elevenlabs.available:
                voices["elevenlabs"] = list(self.elevenlabs.voice_presets.keys())
        
        if not provider or provider == TTSProvider.OPENAI:
            if self.openai_tts.available:
                voices["openai"] = list(self.openai_tts.voices.keys())
        
        if not provider or provider == TTSProvider.GOOGLE:
            if self.google_tts:
                voices["google"] = ["NEUTRAL", "MALE", "FEMALE"]
        
        return voices
    
    async def clone_voice(self, audio_sample: bytes, voice_name: str) -> Optional[str]:
        """
        Clone a voice using audio sample (ElevenLabs feature)
        
        Args:
            audio_sample: Audio sample for cloning
            voice_name: Name for the new voice
            
        Returns:
            Voice ID if successful
        """
        if not self.elevenlabs.available:
            return None
        
        # This would implement ElevenLabs voice cloning API
        # Placeholder for actual implementation
        print(f"🎭 Voice cloning not yet implemented")
        return None

# Global instance
sota_tts_service = SOTATTSService()

# Convenience functions
async def generate_story_audio(text: str, theme: str = "documentary", 
                             quality: str = "high") -> Optional[Dict[str, Any]]:
    """Generate audio for story with optimal settings"""
    quality_enum = TTSQuality(quality)
    result = await sota_tts_service.synthesize_speech(text, theme, quality_enum)
    
    if result:
        return {
            "audio_content": base64.b64encode(result.audio_content).decode('utf-8'),
            "content_type": result.content_type,
            "provider": result.provider.value,
            "voice_id": result.voice_id,
            "duration_ms": result.duration_ms,
            "cost_estimate": result.cost_estimate
        }
    return None

async def get_voice_options(theme: str | None = None) -> Dict[str, Any]:
    """Get available voice options for a theme"""
    voices = sota_tts_service.get_available_voices()
    
    return {
        "available_providers": list(voices.keys()),
        "voices_by_provider": voices,
        "quality_levels": [q.value for q in TTSQuality],
        "recommended_for_theme": theme
    }
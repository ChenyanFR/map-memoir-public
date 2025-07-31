"""
Enhanced Audio Generation Routes
SOTA Text-to-Speech only for maximum user experience
Using ElevenLabs and OpenAI TTS for premium quality
"""

from flask import Blueprint, request, jsonify, send_file
import asyncio
import tempfile
import base64
import os
import aiohttp
from datetime import datetime

# Create blueprint for enhanced audio routes
enhanced_audio_bp = Blueprint('enhanced_audio', __name__)

class SOTATTSService:
    """State-of-the-art TTS service for hackathon demo"""
    
    def __init__(self):
        """Initialize premium TTS services"""
        
        # ElevenLabs configuration (primary)
        self.elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_url = "https://api.elevenlabs.io/v1"
        self.elevenlabs_available = bool(self.elevenlabs_key)
        
        # OpenAI TTS configuration (backup)
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = bool(self.openai_key)
        
        # Premium voice selections for different themes
        self.theme_voices = {
            "adventure": {
                "elevenlabs": "21m00Tcm4TlvDq8ikWAM",  # Rachel - energetic
                "openai": "nova",  # energetic female
                "description": "Energetic voice perfect for adventure stories"
            },
            "documentary": {
                "elevenlabs": "2EiwWnXFnvU5JabPnv8n",  # Clyde - authoritative
                "openai": "onyx",  # deep male
                "description": "Professional voice ideal for documentaries"
            },
            "romantic": {
                "elevenlabs": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - warm
                "openai": "shimmer",  # warm female
                "description": "Warm voice perfect for romantic stories"
            },
            "mystery": {
                "elevenlabs": "onwK4e9ZLuTAKqWW03F9",  # Daniel - dramatic
                "openai": "fable",  # dramatic male
                "description": "Dramatic voice great for mystery tales"
            },
            "family": {
                "elevenlabs": "pFZP5JQG7iQjIQuC4Bku",  # Lily - friendly
                "openai": "alloy",  # balanced neutral
                "description": "Friendly voice perfect for family stories"
            }
        }
        
        print(f"🎙️ SOTA TTS Service initialized")
        print(f"   ElevenLabs: {'✅ Available' if self.elevenlabs_available else '❌ Not configured'}")
        print(f"   OpenAI TTS: {'✅ Available' if self.openai_available else '❌ Not configured'}")
    
    async def synthesize_with_elevenlabs(self, text: str, voice_id: str) -> bytes:
        """Generate speech using ElevenLabs API"""
        
        url = f"{self.elevenlabs_url}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json", 
            "xi-api-key": self.elevenlabs_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error {response.status}: {error_text}")
    
    async def synthesize_with_openai(self, text: str, voice: str) -> bytes:
        """Generate speech using OpenAI TTS API"""
        
        url = "https://api.openai.com/v1/audio/speech"
        
        payload = {
            "model": "tts-1-hd",  # High quality model
            "input": text,
            "voice": voice,
            "response_format": "mp3",
            "speed": 1.0
        }
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI TTS API error {response.status}: {error_text}")
    
    async def generate_premium_audio(self, text: str, theme: str = "documentary") -> dict:
        """
        Generate premium quality audio with automatic provider selection
        
        Args:
            text: Text to synthesize
            theme: Story theme for voice selection
            
        Returns:
            Dictionary with audio data and metadata
        """
        
        # Get voice configuration for theme
        voice_config = self.theme_voices.get(theme, self.theme_voices["documentary"])
        
        try:
            # Primary: Try ElevenLabs for best quality
            if self.elevenlabs_available:
                try:
                    audio_content = await self.synthesize_with_elevenlabs(
                        text, voice_config["elevenlabs"]
                    )
                    
                    return {
                        "audio_content": audio_content,
                        "provider": "elevenlabs",
                        "voice_id": voice_config["elevenlabs"],
                        "quality": "premium",
                        "theme": theme,
                        "description": voice_config["description"]
                    }
                    
                except Exception as e:
                    print(f"ElevenLabs failed: {e}, trying OpenAI...")
            
            # Backup: OpenAI TTS (still high quality)
            if self.openai_available:
                audio_content = await self.synthesize_with_openai(
                    text, voice_config["openai"]
                )
                
                return {
                    "audio_content": audio_content,
                    "provider": "openai",
                    "voice_id": voice_config["openai"], 
                    "quality": "high",
                    "theme": theme,
                    "description": voice_config["description"]
                }
            
            # No SOTA TTS available
            raise Exception("No premium TTS services available")
            
        except Exception as e:
            raise Exception(f"All premium TTS services failed: {str(e)}")

# Initialize global TTS service
sota_tts = SOTATTSService()

@enhanced_audio_bp.route('/api/audio/generate', methods=['POST'])
def generate_sota_audio():
    """
    Generate premium audio using SOTA TTS models
    
    Expected JSON body:
    {
        "text": "Welcome to Map Memoir with ultra-realistic voice synthesis!",
        "theme": "adventure",
        "format": "mp3"
    }
    
    Returns:
    {
        "success": true,
        "audio": "base64_encoded_premium_audio",
        "provider": "elevenlabs",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "quality": "premium",
        "theme": "adventure"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        theme = data.get('theme', 'documentary')
        
        # Validate text length for demo
        if len(text) > 2000:
            return jsonify({'error': 'Text too long for demo (max 2000 characters)'}), 400
        
        # Generate premium audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                sota_tts.generate_premium_audio(text, theme)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'audio': base64.b64encode(result['audio_content']).decode('utf-8'),
            'content_type': 'audio/mpeg',
            'provider': result['provider'],
            'voice_id': result['voice_id'],
            'quality': result['quality'],
            'theme': result['theme'],
            'description': result['description'],
            'message': 'Premium audio generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Premium audio generation failed: {str(e)}'
        }), 500

@enhanced_audio_bp.route('/api/audio/story-narration', methods=['POST'])
def generate_story_narration():
    """
    Generate complete story narration with premium quality
    
    Expected JSON body:
    {
        "story": "Complete story text...",
        "timeline": ["Chapter 1: Tokyo Adventure", "Chapter 2: Paris Romance"],
        "theme": "adventure",
        "chapter_breaks": true
    }
    
    Returns:
    {
        "success": true,
        "audio_segments": [...],
        "full_audio": "base64_combined_audio",
        "provider": "elevenlabs"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'story' not in data:
            return jsonify({'error': 'Story field is required'}), 400
        
        story = data['story']
        timeline = data.get('timeline', [])
        theme = data.get('theme', 'documentary')
        chapter_breaks = data.get('chapter_breaks', False)
        
        if chapter_breaks and timeline:
            # Generate segmented narration
            segments = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                for i, chapter in enumerate(timeline):
                    # Create chapter text with dramatic pause
                    chapter_text = f"{chapter}... "
                    
                    # Add story segment if available
                    story_sentences = story.split('. ')
                    if i < len(story_sentences):
                        chapter_text += story_sentences[i] + "."
                    
                    result = loop.run_until_complete(
                        sota_tts.generate_premium_audio(chapter_text, theme)
                    )
                    
                    segments.append({
                        "chapter": chapter,
                        "audio": base64.b64encode(result['audio_content']).decode('utf-8'),
                        "provider": result['provider'],
                        "quality": result['quality']
                    })
                    
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'audio_segments': segments,
                'segments_count': len(segments),
                'theme': theme,
                'message': 'Story narration generated with premium quality'
            })
        
        else:
            # Generate single narration for entire story
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    sota_tts.generate_premium_audio(story, theme)
                )
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'full_audio': base64.b64encode(result['audio_content']).decode('utf-8'),
                'provider': result['provider'],
                'voice_id': result['voice_id'],
                'quality': result['quality'],
                'theme': theme,
                'description': result['description']
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Story narration failed: {str(e)}'
        }), 500

@enhanced_audio_bp.route('/api/audio/download', methods=['POST'])
def download_premium_audio():
    """
    Generate and download premium audio file
    
    Expected JSON body:
    {
        "text": "Story content...",
        "theme": "adventure", 
        "filename": "my_story.mp3"
    }
    
    Returns:
    MP3 file download with premium quality
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        theme = data.get('theme', 'documentary')
        filename = data.get('filename', f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        
        # Generate premium audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                sota_tts.generate_premium_audio(text, theme)
            )
        finally:
            loop.close()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(result['audio_content'])
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        return jsonify({'error': f'Audio download failed: {str(e)}'}), 500

@enhanced_audio_bp.route('/api/audio/voices', methods=['GET'])
def get_premium_voices():
    """
    Get available premium voices and themes
    
    Returns:
    {
        "themes": {...},
        "providers": ["elevenlabs", "openai"],
        "quality_levels": ["high", "premium"]
    }
    """
    try:
        return jsonify({
            'themes': {
                theme: {
                    'description': config['description'],
                    'elevenlabs_voice': config['elevenlabs'],
                    'openai_voice': config['openai']
                }
                for theme, config in sota_tts.theme_voices.items()
            },
            'providers': {
                'elevenlabs': {
                    'available': sota_tts.elevenlabs_available,
                    'quality': 'premium',
                    'description': 'State-of-the-art voice synthesis with natural emotions'
                },
                'openai': {
                    'available': sota_tts.openai_available, 
                    'quality': 'high',
                    'description': 'High-quality neural text-to-speech'
                }
            },
            'recommended_for_demo': 'elevenlabs'
        })
        
    except Exception as e:
        return jsonify({'error': f'Get voices failed: {str(e)}'}), 500

@enhanced_audio_bp.route('/api/audio/test', methods=['GET'])
def test_premium_tts():
    """Test premium TTS services"""
    try:
        test_text = "Welcome to Map Memoir, where your travel stories come alive with ultra-realistic voice synthesis!"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                sota_tts.generate_premium_audio(test_text, "adventure")
            )
        finally:
            loop.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Premium TTS is working perfectly',
            'test_result': {
                'provider': result['provider'],
                'quality': result['quality'],
                'voice_description': result['description'],
                'audio_size_kb': len(result['audio_content']) // 1024
            },
            'providers_status': {
                'elevenlabs': sota_tts.elevenlabs_available,
                'openai': sota_tts.openai_available
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Premium TTS test failed: {str(e)}'
        }), 500

# Legacy compatibility route (upgraded to SOTA)
@enhanced_audio_bp.route('/generate_audio', methods=['POST'])
def legacy_generate_audio():
    """
    Legacy audio generation endpoint with SOTA upgrade
    Maintains API compatibility while using premium TTS
    """
    try:
        data = request.get_json()
        
        if not data or 'script' not in data:
            return jsonify({'error': 'Script field is required'}), 400
        
        script = data['script']
        theme = data.get('theme', 'documentary')
        
        # Generate premium audio using new service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                sota_tts.generate_premium_audio(script, theme)
            )
        finally:
            loop.close()
        
        # Return as file (legacy compatibility)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(result['audio_content'])
        temp_file.close()
        
        return send_file(temp_file.name, mimetype='audio/mpeg', as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': f'Legacy audio generation failed: {str(e)}'}), 500
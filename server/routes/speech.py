"""
Speech API routes for Map Memoir
Handles speech-to-text and text-to-speech functionality
"""

from flask import Blueprint, request, jsonify
import base64
from services.speech_service import speech_service

# Create blueprint for speech routes
speech_bp = Blueprint('speech', __name__)

@speech_bp.route('/api/speech/transcribe', methods=['POST'])
def transcribe_audio_route():
    """
    Transcribe audio to text
    
    Expected JSON body:
    {
        "audio": "base64_encoded_audio_data",
        "language": "en-US",
        "format": "WEBM_OPUS",
        "sample_rate": 16000
    }
    
    Returns:
    {
        "transcript": "Hello world",
        "confidence": 0.95,
        "language_code": "en-US"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'audio' not in data:
            return jsonify({'error': 'Audio data is required'}), 400
        
        audio_base64 = data['audio']
        language_code = data.get('language', 'en-US')
        audio_format = data.get('format', 'WEBM_OPUS')
        sample_rate = data.get('sample_rate', 16000)
        
        # Transcribe audio
        result = speech_service.transcribe_audio_base64(
            audio_base64, 
            language_code, 
            sample_rate, 
            audio_format
        )
        
        if result:
            return jsonify(result.dict())
        else:
            return jsonify({'error': 'Transcription failed'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Transcription error: {str(e)}'}), 500

@speech_bp.route('/api/speech/transcribe-file', methods=['POST'])
def transcribe_file_route():
    """
    Transcribe uploaded audio file
    
    Expected: multipart/form-data with audio file
    Optional form fields:
    - language: language code (default: en-US)
    - long_audio: true/false for long audio processing
    
    Returns:
    {
        "transcript": "Hello world",
        "confidence": 0.95,
        "language_code": "en-US"
    }
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        language_code = request.form.get('language', 'en-US')
        long_audio = request.form.get('long_audio', 'false').lower() == 'true'
        
        # Read audio file content
        audio_content = audio_file.read()
        
        # Determine audio format from file extension
        filename = audio_file.filename.lower()
        if filename.endswith('.wav'):
            audio_format = 'LINEAR16'
        elif filename.endswith('.mp3'):
            audio_format = 'MP3'
        elif filename.endswith('.flac'):
            audio_format = 'FLAC'
        elif filename.endswith('.webm'):
            audio_format = 'WEBM_OPUS'
        else:
            audio_format = 'WEBM_OPUS'  # Default
        
        # Choose transcription method based on audio length
        if long_audio:
            result = speech_service.transcribe_long_audio(audio_content, language_code, audio_format)
        else:
            result = speech_service.transcribe_audio(audio_content, language_code, 16000, audio_format)
        
        if result:
            return jsonify(result.dict())
        else:
            return jsonify({'error': 'Transcription failed'}), 500
        
    except Exception as e:
        return jsonify({'error': f'File transcription error: {str(e)}'}), 500

@speech_bp.route('/api/speech/synthesize', methods=['POST'])
def synthesize_speech_route():
    """
    Convert text to speech
    
    Expected JSON body:
    {
        "text": "Hello world",
        "language": "en-US",
        "voice_gender": "NEUTRAL",
        "format": "MP3"
    }
    
    Returns:
    {
        "audio_content": "base64_encoded_audio",
        "content_type": "audio/mpeg"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        language_code = data.get('language', 'en-US')
        voice_gender = data.get('voice_gender', 'NEUTRAL')
        audio_format = data.get('format', 'MP3')
        
        # Validate text length
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        # Synthesize speech
        result = speech_service.synthesize_speech(text, language_code, voice_gender, audio_format)
        
        if result:
            return jsonify(result.dict())
        else:
            return jsonify({'error': 'Speech synthesis failed'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Speech synthesis error: {str(e)}'}), 500

@speech_bp.route('/api/speech/voices', methods=['GET'])
def get_voices_route():
    """
    Get available voices for speech synthesis
    
    Optional query parameter:
    - language: filter by language code
    
    Returns:
    {
        "voices": [
            {
                "name": "en-US-Wavenet-A",
                "language_codes": ["en-US"],
                "ssml_gender": "FEMALE",
                "natural_sample_rate_hertz": 24000
            }
        ],
        "count": 50
    }
    """
    try:
        language_code = request.args.get('language')
        
        # Get available voices
        voices = speech_service.get_available_voices(language_code)
        
        return jsonify({
            'voices': voices,
            'count': len(voices)
        })
        
    except Exception as e:
        return jsonify({'error': f'Get voices error: {str(e)}'}), 500

@speech_bp.route('/api/speech/process-voice-memo', methods=['POST'])
def process_voice_memo_route():
    """
    Process a complete voice memo: transcribe and extract locations
    
    Expected JSON body:
    {
        "audio": "base64_encoded_audio_data",
        "language": "en-US",
        "extract_locations": true
    }
    
    Returns:
    {
        "transcript": "I went to Paris then Rome",
        "confidence": 0.95,
        "locations": ["Paris", "Rome"],
        "processing_time": 2.5
    }
    """
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        
        if not data or 'audio' not in data:
            return jsonify({'error': 'Audio data is required'}), 400
        
        audio_base64 = data['audio']
        language_code = data.get('language', 'en-US')
        extract_locations = data.get('extract_locations', True)
        
        # Step 1: Transcribe audio
        transcription_result = speech_service.transcribe_audio_base64(audio_base64, language_code)
        
        if not transcription_result:
            return jsonify({'error': 'Transcription failed'}), 500
        
        response_data = transcription_result.dict()
        
        # Step 2: Extract locations if requested
        if extract_locations and transcription_result.transcript:
            try:
                from services.ai_service import extract_locations_from_text
                import asyncio
                
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    locations = loop.run_until_complete(
                        extract_locations_from_text(transcription_result.transcript)
                    )
                    response_data['locations'] = locations
                finally:
                    loop.close()
                    
            except Exception as e:
                print(f"Location extraction error: {e}")
                response_data['locations'] = []
                response_data['location_extraction_error'] = str(e)
        
        # Add processing time
        processing_time = time.time() - start_time
        response_data['processing_time'] = round(processing_time, 2)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Voice memo processing error: {str(e)}'}), 500

@speech_bp.route('/api/speech/test', methods=['GET'])
def test_speech_route():
    """Test endpoint for speech functionality"""
    try:
        # Test text-to-speech with a simple phrase
        test_text = "Hello, this is a test of the speech service."
        
        result = speech_service.synthesize_speech(test_text, "en-US", "NEUTRAL", "MP3")
        
        if result:
            # Don't return the full audio content in test, just confirm it works
            return jsonify({
                'status': 'success',
                'message': 'Speech service is working',
                'test_result': {
                    'text_tested': test_text,
                    'synthesis_successful': True,
                    'audio_format': 'MP3',
                    'audio_size_bytes': len(base64.b64decode(result.audio_content))
                },
                'services': {
                    'speech_to_text': speech_service.speech_client is not None,
                    'text_to_speech': speech_service.tts_client is not None
                }
            })
        else:
            return jsonify({
                'status': 'partial',
                'message': 'Speech service connected but synthesis failed',
                'services': {
                    'speech_to_text': speech_service.speech_client is not None,
                    'text_to_speech': speech_service.tts_client is not None
                }
            }), 206
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Speech test failed: {str(e)}'
        }), 500
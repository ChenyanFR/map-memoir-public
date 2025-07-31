"""
AI-powered location extraction using OpenAI
"""

from flask import Blueprint, request, jsonify
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

ai_locations_bp = Blueprint('ai_locations', __name__)

# Initialize OpenAI client
openai_client = None
try:
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai_client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized for location extraction")
    else:
        print("⚠️ OpenAI API key not found")
except Exception as e:
    print(f"⚠️ OpenAI client initialization failed: {e}")

@ai_locations_bp.route('/api/ai/extract-locations', methods=['POST'])
def ai_extract_locations():
    """
    Extract locations using OpenAI GPT-3.5-turbo
    
    Expected JSON:
    {
        "text": "I traveled from New York to Paris, then Rome"
    }
    
    Returns:
    {
        "locations": ["New York", "Paris", "Rome"],
        "count": 3,
        "method": "openai_gpt35_turbo"
    }
    """
    try:
        if not openai_client:
            return jsonify({
                'error': 'OpenAI service not available',
                'suggestion': 'Check OPENAI_API_KEY in environment'
            }), 500
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Create prompt for location extraction
        prompt = f"""Extract all location names (cities, countries, landmarks, etc.) from the following text. Return only location names that are real places.

Text: "{text}"

Return the result as a JSON object with a "locations" field containing an array of location names in the order they appear.

Example format:
{{
  "locations": ["Paris", "Rome", "Tokyo"]
}}"""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Handle markdown code blocks
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.rfind('```')
                response_text = response_text[json_start:json_end].strip()
            
            parsed_response = json.loads(response_text)
            locations = parsed_response.get('locations', [])
            
        except json.JSONDecodeError:
            # Fallback: try to extract locations from plain text
            lines = response_text.split('\n')
            locations = []
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•')):
                    location = line.lstrip('- •').strip()
                    if location:
                        locations.append(location)
        
        return jsonify({
            'locations': locations,
            'count': len(locations),
            'method': 'openai_gpt35_turbo',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'AI location extraction failed: {str(e)}',
            'status': 'error'
        }), 500

@ai_locations_bp.route('/api/ai/generate-timeline', methods=['POST'])
def ai_generate_timeline():
    """
    Generate timeline using OpenAI GPT-3.5-turbo
    
    Expected JSON:
    {
        "locations": ["Paris", "Rome", "Tokyo"]
    }
    
    Returns:
    {
        "timeline": ["Day 1: Arrival in Paris", ...],
        "method": "openai_gpt35_turbo"
    }
    """
    try:
        if not openai_client:
            return jsonify({
                'error': 'OpenAI service not available'
            }), 500
        
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'Locations field is required'}), 400
        
        locations = data['locations']
        
        if not isinstance(locations, list) or len(locations) == 0:
            return jsonify({'error': 'Locations must be a non-empty array'}), 400
        
        # Create prompt for timeline generation
        locations_list = "\n".join([f"- {location}" for location in locations])
        
        prompt = f"""You are a travel storyteller. Given an ordered list of locations, create a plausible and engaging timeline of events for a trip. The trip starts at the first location and ends at the last. Make it sound like an exciting journey. Keep each timeline event concise, like a chapter title.

Locations:
{locations_list}

Generate a timeline of events for this trip. Return the result as a JSON object with a "timeline" field containing an array of event strings.

Example format:
{{
  "timeline": [
    "Chapter 1: Arrival in Paris",
    "Chapter 2: Exploring the Louvre",
    "Chapter 3: Journey to Rome"
  ]
}}"""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Handle markdown code blocks
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.rfind('```')
                response_text = response_text[json_start:json_end].strip()
            
            parsed_response = json.loads(response_text)
            timeline = parsed_response.get('timeline', [])
            
        except json.JSONDecodeError:
            # Fallback: create basic timeline
            timeline = [f"Visit {location}" for location in locations]
        
        if not timeline:
            timeline = [f"Visit {location}" for location in locations]
        
        return jsonify({
            'timeline': timeline,
            'method': 'openai_gpt35_turbo',
            'location_count': len(locations),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'AI timeline generation failed: {str(e)}',
            'status': 'error'
        }), 500

@ai_locations_bp.route('/api/ai/complete-pipeline', methods=['POST'])
def ai_complete_pipeline():
    """
    Complete pipeline: extract locations from text and generate timeline
    
    Expected JSON:
    {
        "text": "I traveled from New York to Paris, then Rome"
    }
    
    Returns:
    {
        "original_text": "...",
        "locations": ["New York", "Paris", "Rome"],
        "timeline": ["Chapter 1: Departure from New York", ...],
        "method": "openai_gpt35_turbo"
    }
    """
    try:
        if not openai_client:
            return jsonify({
                'error': 'OpenAI service not available'
            }), 500
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Step 1: Extract locations
        locations_prompt = f"""Extract all location names (cities, countries, landmarks, etc.) from the following text. Return only location names that are real places.

Text: "{text}"

Return the result as a JSON object with a "locations" field containing an array of location names in the order they appear.

Example format:
{{
  "locations": ["Paris", "Rome", "Tokyo"]
}}"""

        locations_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": locations_prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        locations_text = locations_response.choices[0].message.content.strip()
        
        # Parse locations
        try:
            if '```json' in locations_text:
                json_start = locations_text.find('```json') + 7
                json_end = locations_text.find('```', json_start)
                locations_text = locations_text[json_start:json_end].strip()
            
            parsed_locations = json.loads(locations_text)
            locations = parsed_locations.get('locations', [])
            
        except json.JSONDecodeError:
            locations = []
        
        if not locations:
            return jsonify({
                'error': 'No locations found in the text',
                'original_text': text
            }), 400
        
        # Step 2: Generate timeline
        locations_list = "\n".join([f"- {location}" for location in locations])
        
        timeline_prompt = f"""You are a travel storyteller. Given an ordered list of locations, create a plausible and engaging timeline of events for a trip. Make it sound like an exciting journey. Keep each timeline event concise, like a chapter title.

Locations:
{locations_list}

Generate a timeline of events for this trip. Return the result as a JSON object with a "timeline" field containing an array of event strings.

Example format:
{{
  "timeline": [
    "Chapter 1: Arrival in Paris",
    "Chapter 2: Exploring the Louvre", 
    "Chapter 3: Journey to Rome"
  ]
}}"""

        timeline_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": timeline_prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        timeline_text = timeline_response.choices[0].message.content.strip()
        
        # Parse timeline
        try:
            if '```json' in timeline_text:
                json_start = timeline_text.find('```json') + 7
                json_end = timeline_text.find('```', json_start)
                timeline_text = timeline_text[json_start:json_end].strip()
            
            parsed_timeline = json.loads(timeline_text)
            timeline = parsed_timeline.get('timeline', [])
            
        except json.JSONDecodeError:
            timeline = [f"Visit {location}" for location in locations]
        
        if not timeline:
            timeline = [f"Visit {location}" for location in locations]
        
        return jsonify({
            'original_text': text,
            'locations': locations,
            'timeline': timeline,
            'method': 'openai_gpt35_turbo',
            'steps_completed': ['location_extraction', 'timeline_generation'],
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Complete pipeline failed: {str(e)}',
            'status': 'error'
        }), 500

@ai_locations_bp.route('/api/ai/test', methods=['GET'])
def test_ai_locations():
    """Test AI location services"""
    try:
        if not openai_client:
            return jsonify({
                'status': 'unavailable',
                'error': 'OpenAI client not configured',
                'suggestion': 'Check OPENAI_API_KEY environment variable'
            }), 500
        
        return jsonify({
            'status': 'available',
            'message': 'AI location services are ready',
            'model': 'gpt-3.5-turbo',
            'available_endpoints': [
                '/api/ai/extract-locations',
                '/api/ai/generate-timeline', 
                '/api/ai/complete-pipeline'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
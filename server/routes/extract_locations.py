"""
Location extraction and timeline generation API routes
"""

from flask import Blueprint, request, jsonify
import asyncio
from typing import List, Dict, Any
from services.ai_service import generate_timeline_from_locations, extract_locations_from_text
from services.maps_service import geocode_locations
from utils.location_utils import validate_locations, clean_location_names

# Create blueprint for location routes
extract_locations_bp = Blueprint('extract_locations', __name__)

@extract_locations_bp.route('/api/extract-locations', methods=['POST'])
def extract_locations_route():
    """
    Extract locations from text input
    
    Expected JSON body:
    {
        "text": "I went to Paris, then Rome, and finally Tokyo"
    }
    
    Returns:
    {
        "locations": ["Paris", "Rome", "Tokyo"],
        "geocoded_locations": [
            {"name": "Paris", "lat": 48.8566, "lng": 2.3522},
            {"name": "Rome", "lat": 41.9028, "lng": 12.4964},
            {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Extract locations from text using AI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            extracted_locations = loop.run_until_complete(extract_locations_from_text(text))
        finally:
            loop.close()
        
        # Clean and validate location names
        cleaned_locations = clean_location_names(extracted_locations)
        validated_locations = validate_locations(cleaned_locations)
        
        # Geocode the locations
        geocoded_locations = geocode_locations(validated_locations)
        
        return jsonify({
            'locations': validated_locations,
            'geocoded_locations': geocoded_locations
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to extract locations: {str(e)}'}), 500

@extract_locations_bp.route('/api/generate-timeline', methods=['POST'])
def generate_timeline_route():
    """
    Generate timeline from locations
    
    Expected JSON body:
    {
        "locations": ["Paris", "Rome", "Tokyo"]
    }
    
    Returns:
    {
        "timeline": [
            "Chapter 1: Arrival in Paris",
            "Chapter 2: Exploring the City of Light",
            "Chapter 3: Journey to the Eternal City",
            "Chapter 4: Discovering Rome's Ancient Wonders",
            "Chapter 5: Flight to the Land of the Rising Sun",
            "Chapter 6: Tokyo's Modern Marvels"
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'Locations field is required'}), 400
        
        locations = data['locations']
        
        if not isinstance(locations, list) or len(locations) == 0:
            return jsonify({'error': 'Locations must be a non-empty array'}), 400
        
        # Generate timeline using AI service
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(generate_timeline_from_locations(locations))
            return jsonify(result)
        finally:
            loop.close()
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate timeline: {str(e)}'}), 500

@extract_locations_bp.route('/api/extract-locations-and-timeline', methods=['POST'])
def extract_locations_and_timeline_route():
    """
    Combined endpoint: extract locations from text and generate timeline
    
    Expected JSON body:
    {
        "text": "I went to Paris, then Rome, and finally Tokyo"
    }
    
    Returns:
    {
        "locations": ["Paris", "Rome", "Tokyo"],
        "geocoded_locations": [...],
        "timeline": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Step 1: Extract locations
        extracted_locations = extract_locations_from_text(text)
        cleaned_locations = clean_location_names(extracted_locations)
        validated_locations = validate_locations(cleaned_locations)
        
        # Step 2: Geocode locations
        geocoded_locations = geocode_locations(validated_locations)
        
        # Step 3: Generate timeline
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            timeline_result = loop.run_until_complete(generate_timeline_from_locations(validated_locations))
            timeline = timeline_result.get('timeline', [])
        finally:
            loop.close()
        
        return jsonify({
            'locations': validated_locations,
            'geocoded_locations': geocoded_locations,
            'timeline': timeline
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to process request: {str(e)}'}), 500

@extract_locations_bp.route('/api/test-extract-locations', methods=['GET'])
def test_extract_locations():
    """Test endpoint for location extraction"""
    try:
        # Test with sample data
        test_text = "I traveled from New York to Paris, then went to Rome, and finally visited Tokyo."
        
        # Extract and process locations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            extracted_locations = loop.run_until_complete(extract_locations_from_text(test_text))
        finally:
            loop.close()
            
        cleaned_locations = clean_location_names(extracted_locations)
        validated_locations = validate_locations(cleaned_locations)
        
        return jsonify({
            'status': 'success',
            'test_text': test_text,
            'extracted_locations': extracted_locations,
            'cleaned_locations': cleaned_locations,
            'validated_locations': validated_locations,
            'message': 'Location extraction test completed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Test failed: {str(e)}'
        }), 500
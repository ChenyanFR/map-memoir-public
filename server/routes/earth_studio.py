"""
Earth Studio Routes - English Version
Handles geocoding and AI text parsing for Earth Studio integration
"""

from flask import Blueprint, request, jsonify, send_file
import asyncio
import tempfile
import os
from datetime import datetime

# Create blueprint
earth_studio_bp = Blueprint('earth_studio', __name__)

# Predefined location coordinates (avoiding geocoding API calls)
PREDEFINED_LOCATIONS = {
    "san francisco": {"name": "San Francisco", "latitude": 37.7749, "longitude": -122.4194},
    "monterey": {"name": "Monterey", "latitude": 36.6002, "longitude": -121.8947},
    "big sur": {"name": "Big Sur", "latitude": 36.2704, "longitude": -121.8081},
    "los angeles": {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437},
    "new york": {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    "new york city": {"name": "New York City", "latitude": 40.7128, "longitude": -74.0060},
    "paris": {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    "tokyo": {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    "london": {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    "rome": {"name": "Rome", "latitude": 41.9028, "longitude": 12.4964},
    "berlin": {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050},
    "amsterdam": {"name": "Amsterdam", "latitude": 52.3676, "longitude": 4.9041},
    "prague": {"name": "Prague", "latitude": 50.0755, "longitude": 14.4378},
    "vienna": {"name": "Vienna", "latitude": 48.2082, "longitude": 16.3738},
    "seoul": {"name": "Seoul", "latitude": 37.5665, "longitude": 126.9780},
    "shanghai": {"name": "Shanghai", "latitude": 31.2304, "longitude": 121.4737},
    "hong kong": {"name": "Hong Kong", "latitude": 22.3193, "longitude": 114.1694},
    "singapore": {"name": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    "bangkok": {"name": "Bangkok", "latitude": 13.7563, "longitude": 100.5018}
}

def geocode_location_simple(location_name):
    """Simple geocoding using predefined coordinates"""
    location_key = location_name.lower().strip()
    
    if location_key in PREDEFINED_LOCATIONS:
        return PREDEFINED_LOCATIONS[location_key]
    
    # If not found, return default location
    return {
        "name": location_name,
        "latitude": 37.7749,  # San Francisco as default
        "longitude": -122.4194
    }

def extract_locations_simple(text):
    """Simple location extraction based on keyword matching"""
    text_lower = text.lower()
    found_locations = []
    
    # Check predefined locations
    for location_key, location_data in PREDEFINED_LOCATIONS.items():
        if location_key in text_lower:
            found_locations.append(location_data["name"])
    
    # Remove duplicates
    return list(dict.fromkeys(found_locations))

@earth_studio_bp.route('/api/earth-studio/create-project', methods=['POST'])
def create_earth_studio_project():
    """
    Create Earth Studio project with improved error handling
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'Locations field is required'}), 400
        
        location_names = data['locations']
        timeline = data.get('timeline', [])
        title = data.get('title', f"Earth Studio Project - {datetime.now().strftime('%Y%m%d')}")
        
        # Use simple geocoding
        geocoded_locations = []
        for location_name in location_names:
            geocoded_location = geocode_location_simple(location_name)
            geocoded_locations.append(geocoded_location)
        
        # Generate simplified Earth Studio project
        from services.earth_studio_service import earth_studio_service
        
        project = earth_studio_service.generate_earth_studio_project(
            geocoded_locations, timeline, title
        )
        
        # Export to Earth Studio JSON
        earth_studio_json = earth_studio_service.export_to_earth_studio_json(project)
        
        return jsonify({
            'success': True,
            'project': project.dict(),
            'earth_studio_json': earth_studio_json,
            'location_count': len(geocoded_locations),
            'total_duration': project.duration,
            'keyframes_count': len(project.keyframes),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Earth Studio project creation failed: {str(e)}',
            'suggestion': 'Try using predefined locations like San Francisco, Paris, Tokyo'
        }), 500

@earth_studio_bp.route('/api/earth-studio/from-text', methods=['POST'])
def create_from_text():
    """
    Create Earth Studio project from text with improved location extraction
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        title = data.get('title', 'Map Memoir Journey')
        video_style = data.get('video_style', 'cinematic')
        
        # Use simple location extraction
        extracted_locations = extract_locations_simple(text)
        
        if not extracted_locations:
            return jsonify({
                'error': 'No recognized locations found in the text',
                'suggestion': 'Try mentioning cities like New York, Paris, Tokyo, London, etc.',
                'text_received': text[:100] + "..." if len(text) > 100 else text
            }), 400
        
        # Geocode locations
        geocoded_locations = []
        for location_name in extracted_locations:
            geocoded_location = geocode_location_simple(location_name)
            geocoded_locations.append(geocoded_location)
        
        # Generate simple timeline
        timeline = [f"Chapter {i+1}: Exploring {loc['name']}" for i, loc in enumerate(geocoded_locations)]
        
        # Create Earth Studio project
        from services.earth_studio_service import earth_studio_service
        
        project = earth_studio_service.generate_earth_studio_project(
            geocoded_locations, timeline, title
        )
        
        # Export to Earth Studio JSON
        earth_studio_json = earth_studio_service.export_to_earth_studio_json(project)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'extracted_locations': extracted_locations,
            'geocoded_locations': [loc for loc in geocoded_locations],
            'timeline': timeline,
            'project': project.dict(),
            'earth_studio_json': earth_studio_json,
            'video_style': video_style,
            'stats': {
                'locations_found': len(extracted_locations),
                'locations_geocoded': len(geocoded_locations),
                'timeline_events': len(timeline),
                'video_duration': project.duration,
                'keyframes': len(project.keyframes)
            },
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Text to Earth Studio conversion failed: {str(e)}',
            'suggestion': 'Try using simpler text with well-known city names'
        }), 500

@earth_studio_bp.route('/api/earth-studio/preview', methods=['POST'])
def preview_animation():
    """
    Generate preview information for Earth Studio animation
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'Locations field is required'}), 400
        
        locations = data['locations']
        timeline = data.get('timeline', [])
        
        # Use existing utility functions to generate keyframes
        from utils.earth_studio_utils import create_smooth_camera_path
        
        keyframes = create_smooth_camera_path(locations, "cinematic")
        
        # Create preview data
        preview_data = {
            'keyframes': keyframes,
            'duration': keyframes[-1]['time'] if keyframes else 0,
            'locations_count': len(locations),
            'camera_positions': len(keyframes),
            'estimated_render_time': f"{len(keyframes) * 2} minutes",
            'flight_path': [
                {
                    'from': locations[i].get('name', f'Location {i}'),
                    'to': locations[i+1].get('name', f'Location {i+1}'),
                    'distance_km': 'calculated',
                    'flight_time': '3.0s'
                }
                for i in range(len(locations) - 1)
            ]
        }
        
        return jsonify({
            'preview': preview_data,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Preview generation failed: {str(e)}',
            'status': 'error'
        }), 500

@earth_studio_bp.route('/api/earth-studio/test', methods=['GET'])
def test_earth_studio():
    """Test Earth Studio service functionality"""
    try:
        # Test data
        test_locations = [
            {'name': 'New York', 'latitude': 40.7128, 'longitude': -74.0060},
            {'name': 'Paris', 'latitude': 48.8566, 'longitude': 2.3522},
            {'name': 'Tokyo', 'latitude': 35.6762, 'longitude': 139.6503}
        ]
        
        test_timeline = [
            "Chapter 1: Departure from New York",
            "Chapter 2: Arrival in Paris",
            "Chapter 3: Journey to Tokyo"
        ]
        
        # Generate test project
        from services.earth_studio_service import earth_studio_service
        
        project = earth_studio_service.generate_earth_studio_project(
            test_locations, test_timeline, "Test Journey"
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Earth Studio service is working',
            'test_project': {
                'title': project.title,
                'duration': project.duration,
                'keyframes_count': len(project.keyframes),
                'locations_tested': len(test_locations)
            },
            'available_endpoints': [
                '/api/earth-studio/create-project',
                '/api/earth-studio/from-text',
                '/api/earth-studio/download-project',
                '/api/earth-studio/preview'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Earth Studio test failed: {str(e)}'
        }), 500

@earth_studio_bp.route('/api/earth-studio/quick-demo', methods=['POST'])
def quick_demo():
    """Quick demo with predefined amazing routes"""
    
    demo_routes = {
        "california": {
            "locations": ["San Francisco", "Los Angeles"],
            "title": "California Coast"
        },
        "europe": {
            "locations": ["London", "Paris", "Rome"],
            "title": "European Capitals"
        },
        "asia": {
            "locations": ["Tokyo", "Seoul", "Shanghai"],
            "title": "Asian Megacities"
        }
    }
    
    try:
        data = request.get_json() or {}
        route = data.get('route', 'california')
        
        if route not in demo_routes:
            route = 'california'
        
        route_data = demo_routes[route]
        
        # Geocode locations
        geocoded_locations = []
        for location_name in route_data["locations"]:
            geocoded_location = geocode_location_simple(location_name)
            geocoded_locations.append(geocoded_location)
        
        # Generate timeline
        timeline = [f"Chapter {i+1}: Discovering {loc['name']}" for i, loc in enumerate(geocoded_locations)]
        
        # Create project
        from services.earth_studio_service import earth_studio_service
        
        project = earth_studio_service.generate_earth_studio_project(
            geocoded_locations, timeline, route_data["title"]
        )
        
        return jsonify({
            'success': True,
            'route': route,
            'project': project.dict(),
            'earth_studio_json': earth_studio_service.export_to_earth_studio_json(project),
            'message': f'Quick demo project created: {route_data["title"]}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Quick demo failed: {str(e)}'
        }), 500
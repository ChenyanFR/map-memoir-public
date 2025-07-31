"""
Maps API routes for Map Memoir
Handles geocoding, places search, and directions
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any
from services.maps_service import maps_service

# Create blueprint for maps routes
maps_bp = Blueprint('maps', __name__)

@maps_bp.route('/api/maps/geocode', methods=['POST'])
def geocode_location_route():
    """
    Geocode a location name to coordinates
    
    Expected JSON body:
    {
        "location": "Paris, France"
    }
    
    Returns:
    {
        "name": "Paris, France",
        "formatted_address": "Paris, France",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
        "types": ["locality", "political"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'location' not in data:
            return jsonify({'error': 'Location field is required'}), 400
        
        location = data['location']
        
        # Geocode the location
        result = maps_service.geocode_location(location)
        
        if result:
            return jsonify(result.dict())
        else:
            return jsonify({'error': f'Could not geocode location: {location}'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Geocoding failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/geocode-batch', methods=['POST'])
def geocode_locations_route():
    """
    Geocode multiple locations
    
    Expected JSON body:
    {
        "locations": ["Paris", "Rome", "Tokyo"]
    }
    
    Returns:
    {
        "results": [
            {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522, ...},
            {"name": "Rome", "latitude": 41.9028, "longitude": 12.4964, ...}
        ],
        "successful": 2,
        "failed": 1
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'Locations field is required'}), 400
        
        locations = data['locations']
        
        if not isinstance(locations, list):
            return jsonify({'error': 'Locations must be an array'}), 400
        
        # Geocode all locations
        results = maps_service.geocode_locations(locations)
        
        successful = len(results)
        failed = len(locations) - successful
        
        return jsonify({
            'results': [result.dict() for result in results],
            'successful': successful,
            'failed': failed,
            'total': len(locations)
        })
        
    except Exception as e:
        return jsonify({'error': f'Batch geocoding failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/search-nearby', methods=['POST'])
def search_nearby_route():
    """
    Search for places near a location
    
    Expected JSON body:
    {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "query": "restaurants",
        "radius": 1000
    }
    
    Returns:
    {
        "places": [
            {
                "name": "Restaurant Name",
                "address": "123 Street",
                "latitude": 48.8567,
                "longitude": 2.3523,
                "rating": 4.5,
                "types": ["restaurant", "food"]
            }
        ],
        "count": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        query = data.get('query')
        radius = data.get('radius', 5000)
        
        # Search nearby places
        results = maps_service.search_places_nearby(latitude, longitude, query, radius)
        
        return jsonify({
            'places': [result.dict() for result in results],
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Nearby search failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/search-text', methods=['POST'])
def search_text_route():
    """
    Search places by text query
    
    Expected JSON body:
    {
        "query": "Eiffel Tower Paris",
        "location": [48.8566, 2.3522]  // optional center point
    }
    
    Returns:
    {
        "places": [...],
        "count": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query field is required'}), 400
        
        query = data['query']
        location = data.get('location')  # Optional [lat, lng]
        
        if location and len(location) == 2:
            location = tuple(location)
        else:
            location = None
        
        # Search places by text
        results = maps_service.search_places_by_text(query, location)
        
        return jsonify({
            'places': [result.dict() for result in results],
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Text search failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/place-details/<place_id>', methods=['GET'])
def get_place_details_route(place_id):
    """
    Get detailed information about a place
    
    Returns:
    {
        "name": "Place Name",
        "formatted_address": "Full Address",
        "rating": 4.5,
        "website": "https://example.com",
        "phone": "+1234567890",
        "opening_hours": {...},
        "reviews": [...]
    }
    """
    try:
        # Get place details
        details = maps_service.get_place_details(place_id)
        
        if details:
            return jsonify(details)
        else:
            return jsonify({'error': f'Place not found: {place_id}'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Place details failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/directions', methods=['POST'])
def get_directions_route():
    """
    Get directions between locations
    
    Expected JSON body:
    {
        "origin": "Paris, France",
        "destination": "Rome, Italy",
        "waypoints": ["Lyon, France"]  // optional
    }
    
    Returns:
    {
        "routes": [...],
        "status": "OK"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'origin' not in data or 'destination' not in data:
            return jsonify({'error': 'Origin and destination are required'}), 400
        
        origin = data['origin']
        destination = data['destination']
        waypoints = data.get('waypoints')
        
        # Get directions
        directions = maps_service.get_directions(origin, destination, waypoints)
        
        if directions:
            return jsonify(directions)
        else:
            return jsonify({'error': 'Could not find directions'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Directions failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/distance-matrix', methods=['POST'])
def get_distance_matrix_route():
    """
    Calculate distances between multiple points
    
    Expected JSON body:
    {
        "origins": ["Paris, France", "London, UK"],
        "destinations": ["Rome, Italy", "Berlin, Germany"]
    }
    
    Returns:
    {
        "rows": [
            {
                "elements": [
                    {"distance": {"text": "1,420 km", "value": 1420000}, "duration": {...}},
                    ...
                ]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'origins' not in data or 'destinations' not in data:
            return jsonify({'error': 'Origins and destinations are required'}), 400
        
        origins = data['origins']
        destinations = data['destinations']
        
        if not isinstance(origins, list) or not isinstance(destinations, list):
            return jsonify({'error': 'Origins and destinations must be arrays'}), 400
        
        # Calculate distance matrix
        matrix = maps_service.calculate_distance_matrix(origins, destinations)
        
        if matrix:
            return jsonify(matrix)
        else:
            return jsonify({'error': 'Could not calculate distance matrix'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Distance matrix failed: {str(e)}'}), 500

@maps_bp.route('/api/maps/test', methods=['GET'])
def test_maps_route():
    """Test endpoint for maps functionality"""
    try:
        # Test geocoding
        test_location = "Eiffel Tower, Paris"
        result = maps_service.geocode_location(test_location)
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Maps service is working',
                'test_result': {
                    'location_tested': test_location,
                    'geocoded': result.dict()
                }
            })
        else:
            return jsonify({
                'status': 'partial',
                'message': 'Maps service connected but geocoding failed',
                'error': 'Could not geocode test location'
            }), 206
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Maps test failed: {str(e)}'
        }), 500
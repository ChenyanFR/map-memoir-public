"""
Location utility functions for processing and validating location data
Enhanced version with more comprehensive location processing
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple, Set
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.distance import geodesic

def clean_location_names(locations: List[str]) -> List[str]:
    """
    Clean and normalize location names
    
    Args:
        locations: List of raw location names
        
    Returns:
        List of cleaned location names
    """
    cleaned = []
    
    for location in locations:
        if not location or not isinstance(location, str):
            continue
            
        # Remove extra whitespace
        cleaned_name = location.strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['the ', 'a ', 'an ', 'in ', 'at ', 'to ', 'from ']
        for prefix in prefixes_to_remove:
            if cleaned_name.lower().startswith(prefix):
                cleaned_name = cleaned_name[len(prefix):]
        
        # Remove special characters but keep spaces, hyphens, apostrophes, and commas
        cleaned_name = re.sub(r'[^\w\s\-\',.]', '', cleaned_name)
        
        # Remove extra spaces and normalize
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        
        # Capitalize properly (title case)
        cleaned_name = cleaned_name.title()
        
        # Special handling for common location patterns
        cleaned_name = _fix_common_location_patterns(cleaned_name)
        
        if cleaned_name and len(cleaned_name) > 1:
            cleaned.append(cleaned_name)
    
    return cleaned

def _fix_common_location_patterns(location: str) -> str:
    """Fix common location name patterns"""
    # Fix state/country abbreviations
    location = re.sub(r'\bUs\b', 'US', location)
    location = re.sub(r'\bUk\b', 'UK', location)
    location = re.sub(r'\bUsa\b', 'USA', location)
    
    # Fix common city patterns
    patterns = {
        r'\bSt\b': 'Saint',
        r'\bMt\b': 'Mount',
        r'\bFt\b': 'Fort',
        r'\bLos Angeles\b': 'Los Angeles',
        r'\bNew York\b': 'New York',
        r'\bSan Francisco\b': 'San Francisco'
    }
    
    for pattern, replacement in patterns.items():
        location = re.sub(pattern, replacement, location, flags=re.IGNORECASE)
    
    return location

def validate_locations(locations: List[str]) -> List[str]:
    """
    Validate and filter location names
    
    Args:
        locations: List of location names to validate
        
    Returns:
        List of valid location names
    """
    valid_locations = []
    
    # Common non-location words to filter out
    stopwords = {
        'and', 'or', 'but', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'from',
        'with', 'by', 'for', 'of', 'as', 'is', 'was', 'are', 'were', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'must', 'shall', 'i', 'you', 'he',
        'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my',
        'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these',
        'those', 'here', 'there', 'when', 'where', 'how', 'what', 'who',
        'which', 'why', 'then', 'now', 'today', 'tomorrow', 'yesterday',
        'time', 'day', 'week', 'month', 'year', 'morning', 'afternoon',
        'evening', 'night', 'first', 'last', 'next', 'before', 'after'
    }
    
    # Words that indicate it might be a location
    location_indicators = {
        'city', 'town', 'village', 'county', 'state', 'country', 'nation',
        'island', 'beach', 'mountain', 'river', 'lake', 'park', 'airport',
        'station', 'hotel', 'restaurant', 'museum', 'tower', 'bridge',
        'cathedral', 'church', 'temple', 'palace', 'castle', 'university',
        'college', 'school', 'hospital', 'mall', 'center', 'square', 'street',
        'avenue', 'road', 'boulevard', 'plaza', 'district', 'neighborhood'
    }
    
    for location in locations:
        if not location:
            continue
            
        location_lower = location.lower()
        
        # Skip if it's a common stopword
        if location_lower in stopwords:
            continue
            
        # Skip very short names (likely not locations)
        if len(location) < 2:
            continue
            
        # Skip if it's all numbers
        if location.isdigit():
            continue
            
        # Skip if it contains mostly numbers
        if len(re.findall(r'\d', location)) > len(location) / 2:
            continue
        
        # Check for location indicators (bonus points)
        has_location_indicator = any(indicator in location_lower for indicator in location_indicators)
        
        # Check if it looks like a proper noun (starts with capital letter)
        is_proper_noun = location[0].isupper() if location else False
        
        # Check length and character composition
        is_reasonable_length = 2 <= len(location) <= 50
        has_letters = any(c.isalpha() for c in location)
        
        # Accept location if it passes basic criteria
        if (is_reasonable_length and has_letters and 
            (is_proper_noun or has_location_indicator)):
            valid_locations.append(location)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_locations = []
    for location in valid_locations:
        location_normalized = location.lower().strip()
        if location_normalized not in seen:
            seen.add(location_normalized)
            unique_locations.append(location)
    
    return unique_locations

def geocode_location(location_name: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Geocode a single location name to get coordinates
    
    Args:
        location_name: Name of the location to geocode
        timeout: Timeout in seconds for the geocoding request
        
    Returns:
        Dictionary with location data or None if geocoding fails
    """
    try:
        geolocator = Nominatim(user_agent="map-memoir-app", timeout=timeout)
        location = geolocator.geocode(location_name)
        
        if location:
            return {
                'name': location_name,
                'full_name': location.address,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'raw': location.raw
            }
    
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error for {location_name}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error geocoding {location_name}: {str(e)}")
    
    return None

def geocode_locations(location_names: List[str]) -> List[Dict[str, Any]]:
    """
    Geocode multiple locations
    
    Args:
        location_names: List of location names to geocode
        
    Returns:
        List of successfully geocoded locations
    """
    geocoded_locations = []
    
    for location_name in location_names:
        geocoded = geocode_location(location_name)
        if geocoded:
            geocoded_locations.append(geocoded)
        else:
            # Add a placeholder if geocoding fails
            geocoded_locations.append({
                'name': location_name,
                'full_name': location_name,
                'latitude': None,
                'longitude': None,
                'error': 'Geocoding failed'
            })
    
    return geocoded_locations

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the distance between two coordinates using geodesic distance
    
    Args:
        lat1, lng1: Coordinates of first point
        lat2, lng2: Coordinates of second point
        
    Returns:
        Distance in kilometers
    """
    try:
        point1 = (lat1, lng1)
        point2 = (lat2, lng2)
        distance = geodesic(point1, point2).kilometers
        return round(distance, 2)
    except Exception as e:
        print(f"Distance calculation error: {e}")
        return 0.0

def calculate_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the bearing between two coordinates
    
    Args:
        lat1, lng1: Coordinates of first point
        lat2, lng2: Coordinates of second point
        
    Returns:
        Bearing in degrees (0-360)
    """
    try:
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lng = math.radians(lng2 - lng1)
        
        # Calculate bearing
        y = math.sin(delta_lng) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lng))
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360  # Normalize to 0-360
        
        return round(bearing, 2)
    except Exception as e:
        print(f"Bearing calculation error: {e}")
        return 0.0

def optimize_location_order(locations: List[Dict[str, Any]], 
                          start_location: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Optimize the order of locations to minimize travel distance using nearest neighbor algorithm
    
    Args:
        locations: List of geocoded locations with lat/lng
        start_location: Optional starting location
        
    Returns:
        List of locations in optimized order
    """
    if len(locations) <= 2:
        return locations
    
    # Filter out locations without coordinates
    valid_locations = [loc for loc in locations if loc.get('latitude') and loc.get('longitude')]
    
    if len(valid_locations) <= 2:
        return locations
    
    # Simple nearest neighbor algorithm
    if start_location and start_location.get('latitude') and start_location.get('longitude'):
        optimized = [start_location]
        remaining = [loc for loc in valid_locations if loc != start_location]
        current_location = start_location
    else:
        optimized = [valid_locations[0]]  # Start with first location
        remaining = valid_locations[1:]
        current_location = valid_locations[0]
    
    while remaining:
        # Find nearest location
        nearest_distance = float('inf')
        nearest_location = None
        
        for location in remaining:
            distance = calculate_distance(
                current_location['latitude'], current_location['longitude'],
                location['latitude'], location['longitude']
            )
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_location = location
        
        if nearest_location:
            optimized.append(nearest_location)
            remaining.remove(nearest_location)
            current_location = nearest_location
    
    # Add back any locations that couldn't be geocoded
    invalid_locations = [loc for loc in locations if not (loc.get('latitude') and loc.get('longitude'))]
    optimized.extend(invalid_locations)
    
    return optimized

def calculate_trip_statistics(locations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for a trip (total distance, duration estimate, etc.)
    
    Args:
        locations: List of geocoded locations in order
        
    Returns:
        Dictionary with trip statistics
    """
    if len(locations) < 2:
        return {
            'total_distance_km': 0,
            'total_locations': len(locations),
            'estimated_travel_time_hours': 0,
            'bounding_box': None
        }
    
    # Filter valid locations
    valid_locations = [loc for loc in locations if loc.get('latitude') and loc.get('longitude')]
    
    if len(valid_locations) < 2:
        return {
            'total_distance_km': 0,
            'total_locations': len(locations),
            'estimated_travel_time_hours': 0,
            'bounding_box': None
        }
    
    # Calculate total distance
    total_distance = 0
    for i in range(len(valid_locations) - 1):
        current = valid_locations[i]
        next_loc = valid_locations[i + 1]
        
        distance = calculate_distance(
            current['latitude'], current['longitude'],
            next_loc['latitude'], next_loc['longitude']
        )
        total_distance += distance
    
    # Estimate travel time (assume average speed of 60 km/h)
    estimated_travel_time = total_distance / 60  # hours
    
    # Calculate bounding box
    lats = [loc['latitude'] for loc in valid_locations]
    lngs = [loc['longitude'] for loc in valid_locations]
    
    bounding_box = {
        'north': max(lats),
        'south': min(lats),
        'east': max(lngs),
        'west': min(lngs),
        'center': {
            'latitude': sum(lats) / len(lats),
            'longitude': sum(lngs) / len(lngs)
        }
    }
    
    return {
        'total_distance_km': round(total_distance, 2),
        'total_locations': len(locations),
        'valid_locations': len(valid_locations),
        'estimated_travel_time_hours': round(estimated_travel_time, 1),
        'bounding_box': bounding_box,
        'average_distance_between_stops': round(total_distance / (len(valid_locations) - 1), 2) if len(valid_locations) > 1 else 0
    }

def find_nearby_locations(target_location: Dict[str, Any], 
                         other_locations: List[Dict[str, Any]], 
                         radius_km: float = 50) -> List[Dict[str, Any]]:
    """
    Find locations within a certain radius of a target location
    
    Args:
        target_location: Location to search around
        other_locations: List of locations to search through
        radius_km: Search radius in kilometers
        
    Returns:
        List of nearby locations with distances
    """
    if not target_location.get('latitude') or not target_location.get('longitude'):
        return []
    
    nearby = []
    
    for location in other_locations:
        if not location.get('latitude') or not location.get('longitude'):
            continue
        
        if location == target_location:
            continue
        
        distance = calculate_distance(
            target_location['latitude'], target_location['longitude'],
            location['latitude'], location['longitude']
        )
        
        if distance <= radius_km:
            location_with_distance = location.copy()
            location_with_distance['distance_km'] = distance
            nearby.append(location_with_distance)
    
    # Sort by distance
    nearby.sort(key=lambda x: x['distance_km'])
    
    return nearby

def extract_location_types(location_name: str) -> List[str]:
    """
    Extract potential location types from location name
    
    Args:
        location_name: Name of the location
        
    Returns:
        List of potential location types
    """
    types = []
    location_lower = location_name.lower()
    
    # Define type keywords
    type_keywords = {
        'city': ['city', 'town', 'village', 'municipality'],
        'landmark': ['tower', 'bridge', 'monument', 'statue', 'arch'],
        'nature': ['park', 'garden', 'forest', 'beach', 'mountain', 'lake', 'river'],
        'culture': ['museum', 'gallery', 'theater', 'opera', 'cathedral', 'church', 'temple', 'palace', 'castle'],
        'transport': ['airport', 'station', 'port', 'terminal'],
        'accommodation': ['hotel', 'resort', 'hostel', 'inn'],
        'dining': ['restaurant', 'cafe', 'bar', 'pub', 'bistro'],
        'shopping': ['mall', 'market', 'bazaar', 'shop', 'store'],
        'education': ['university', 'college', 'school', 'academy'],
        'district': ['district', 'quarter', 'neighborhood', 'area', 'zone']
    }
    
    for type_name, keywords in type_keywords.items():
        if any(keyword in location_lower for keyword in keywords):
            types.append(type_name)
    
    return types if types else ['unknown']

# Convenience functions for easy import
def process_locations_complete(locations: List[str]) -> Dict[str, Any]:
    """
    Complete location processing pipeline
    
    Args:
        locations: Raw location names
        
    Returns:
        Dictionary with processed locations and statistics
    """
    # Clean and validate
    cleaned = clean_location_names(locations)
    validated = validate_locations(cleaned)
    
    # Geocode
    geocoded = geocode_locations(validated)
    
    # Optimize order
    optimized = optimize_location_order(geocoded)
    
    # Calculate statistics
    stats = calculate_trip_statistics(optimized)
    
    return {
        'original_locations': locations,
        'cleaned_locations': cleaned,
        'validated_locations': validated,
        'geocoded_locations': geocoded,
        'optimized_locations': optimized,
        'trip_statistics': stats,
        'processing_summary': {
            'input_count': len(locations),
            'cleaned_count': len(cleaned),
            'validated_count': len(validated),
            'geocoded_count': len([loc for loc in geocoded if loc.get('latitude')]),
            'optimization_applied': len(optimized) > 2
        }
    }
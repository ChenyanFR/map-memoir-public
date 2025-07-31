"""
Maps Service for Map Memoir
Handles Google Maps API integration for geocoding and places search
"""

import os
import googlemaps
from typing import List, Dict, Any, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Pydantic models
class GeocodeResult(BaseModel):
    name: str = Field(description="Location name")
    formatted_address: str = Field(description="Full formatted address")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    place_id: Optional[str] = Field(default=None, description="Google Place ID")
    types: List[str] = Field(default=[], description="Location types")

class PlaceSearchResult(BaseModel):
    name: str = Field(description="Place name")
    address: str = Field(description="Place address")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    place_id: str = Field(description="Google Place ID")
    rating: Optional[float] = Field(default=None, description="Place rating")
    types: List[str] = Field(default=[], description="Place types")
    photo_reference: Optional[str] = Field(default=None, description="Photo reference")

class MapsService:
    def __init__(self):
        """Initialize Google Maps and Geopy clients"""
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        
        if self.api_key:
            self.gmaps = googlemaps.Client(key=self.api_key)
            print("✅ Google Maps client initialized")
        else:
            self.gmaps = None
            print("⚠️ Google Maps API key not found")
        
        # Backup geocoder using Nominatim (OpenStreetMap)
        self.backup_geocoder = Nominatim(user_agent="map-memoir-app", timeout=10)
    
    def geocode_location(self, location_name: str) -> Optional[GeocodeResult]:
        """
        Geocode a location name to get coordinates and details
        
        Args:
            location_name: Name of the location to geocode
            
        Returns:
            GeocodeResult object or None if geocoding fails
        """
        try:
            if self.gmaps:
                # Use Google Maps Geocoding API
                geocode_result = self.gmaps.geocode(location_name)
                
                if geocode_result:
                    result = geocode_result[0]
                    geometry = result['geometry']['location']
                    
                    return GeocodeResult(
                        name=location_name,
                        formatted_address=result['formatted_address'],
                        latitude=geometry['lat'],
                        longitude=geometry['lng'],
                        place_id=result.get('place_id'),
                        types=result.get('types', [])
                    )
            
            # Fallback to Nominatim
            location = self.backup_geocoder.geocode(location_name)
            if location:
                return GeocodeResult(
                    name=location_name,
                    formatted_address=location.address,
                    latitude=float(location.latitude),
                    longitude=float(location.longitude),
                    place_id=None,
                    types=[]
                )
            
        except Exception as e:
            print(f"Geocoding error for {location_name}: {str(e)}")
        
        return None
    
    def geocode_locations(self, location_names: List[str]) -> List[GeocodeResult]:
        """
        Geocode multiple locations
        
        Args:
            location_names: List of location names to geocode
            
        Returns:
            List of successfully geocoded locations
        """
        results = []
        
        for location_name in location_names:
            result = self.geocode_location(location_name)
            if result:
                results.append(result)
                print(f"✅ Geocoded: {location_name}")
            else:
                print(f"❌ Failed to geocode: {location_name}")
        
        return results
    
    def search_places_nearby(self, latitude: float, longitude: float, 
                           query: Optional[str] = None, 
                           radius: int = 5000, 
                           place_type: Optional[str] = None) -> List[PlaceSearchResult]:
        """
        Search for places near a given coordinate
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            query: Search query (optional)
            radius: Search radius in meters (default 5000m)
            place_type: Type of place to search for (optional)
            
        Returns:
            List of places found
        """
        if not self.gmaps:
            print("❌ Google Maps client not available")
            return []
        
        try:
            location = (latitude, longitude)
            
            if query:
                # Text search
                places_result = self.gmaps.places(
                    query=query,
                    location=location,
                    radius=radius
                )
            else:
                # Nearby search
                places_result = self.gmaps.places_nearby(
                    location=location,
                    radius=radius,
                    type=place_type
                )
            
            results = []
            for place in places_result.get('results', []):
                geometry = place['geometry']['location']
                
                # Get photo reference if available
                photo_reference = None
                if 'photos' in place and place['photos']:
                    photo_reference = place['photos'][0].get('photo_reference')
                
                result = PlaceSearchResult(
                    name=place['name'],
                    address=place.get('vicinity', ''),
                    latitude=geometry['lat'],
                    longitude=geometry['lng'],
                    place_id=place['place_id'],
                    rating=place.get('rating'),
                    types=place.get('types', []),
                    photo_reference=photo_reference
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Places search error: {str(e)}")
            return []
    
    def search_places_by_text(self, query: str, location: Optional[Tuple[float, float]] = None) -> List[PlaceSearchResult]:
        """
        Search places by text query
        
        Args:
            query: Search query
            location: Optional center point for search (lat, lng)
            
        Returns:
            List of places found
        """
        if not self.gmaps:
            print("❌ Google Maps client not available")
            return []
        
        try:
            places_result = self.gmaps.places(
                query=query,
                location=location
            )
            
            results = []
            for place in places_result.get('results', []):
                geometry = place['geometry']['location']
                
                # Get photo reference if available
                photo_reference = None
                if 'photos' in place and place['photos']:
                    photo_reference = place['photos'][0].get('photo_reference')
                
                result = PlaceSearchResult(
                    name=place['name'],
                    address=place.get('formatted_address', place.get('vicinity', '')),
                    latitude=geometry['lat'],
                    longitude=geometry['lng'],
                    place_id=place['place_id'],
                    rating=place.get('rating'),
                    types=place.get('types', []),
                    photo_reference=photo_reference
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Text search error: {str(e)}")
            return []
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Place details dictionary or None
        """
        if not self.gmaps:
            print("❌ Google Maps client not available")
            return None
        
        try:
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'geometry', 'rating', 
                       'photos', 'types', 'website', 'formatted_phone_number',
                       'opening_hours', 'reviews']
            )
            
            return place_details.get('result')
            
        except Exception as e:
            print(f"Place details error: {str(e)}")
            return None
    
    def calculate_distance_matrix(self, origins: List[str], destinations: List[str]) -> Optional[Dict[str, Any]]:
        """
        Calculate distances and travel times between multiple points
        
        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            
        Returns:
            Distance matrix result or None
        """
        if not self.gmaps:
            print("❌ Google Maps client not available")
            return None
        
        try:
            distance_result = self.gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode="driving",
                units="metric"
            )
            
            return distance_result
            
        except Exception as e:
            print(f"Distance matrix error: {str(e)}")
            return None
    
    def get_directions(self, origin: str, destination: str, 
                      waypoints: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get directions between locations
        
        Args:
            origin: Starting location
            destination: End location
            waypoints: Optional waypoints along the route
            
        Returns:
            Directions result or None
        """
        if not self.gmaps:
            print("❌ Google Maps client not available")
            return None
        
        try:
            directions_result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                waypoints=waypoints,
                mode="driving"
            )
            
            return directions_result
            
        except Exception as e:
            print(f"Directions error: {str(e)}")
            return None

# Global instance
maps_service = MapsService()

# Convenience functions
def geocode_location(location_name: str) -> Optional[Dict[str, Any]]:
    """Geocode a single location"""
    result = maps_service.geocode_location(location_name)
    return result.dict() if result else None

def geocode_locations(location_names: List[str]) -> List[Dict[str, Any]]:
    """Geocode multiple locations"""
    results = maps_service.geocode_locations(location_names)
    return [result.dict() for result in results]

def search_places_nearby(lat: float, lng: float, query: str = None, radius: int = 5000) -> List[Dict[str, Any]]:
    """Search places near coordinates"""
    results = maps_service.search_places_nearby(lat, lng, query, radius)
    return [result.dict() for result in results]

def search_places_by_text(query: str) -> List[Dict[str, Any]]:
    """Search places by text"""
    results = maps_service.search_places_by_text(query)
    return [result.dict() for result in results]
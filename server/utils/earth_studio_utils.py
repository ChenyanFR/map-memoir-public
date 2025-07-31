"""
Earth Studio utility functions
Helper functions for Google Earth Studio integration
"""

import math
import json
from typing import List, Dict, Any, Tuple, Optional
from geopy.distance import geodesic
from datetime import datetime

class CameraMovement:
    """Camera movement calculations for cinematic effects"""
    
    @staticmethod
    def calculate_great_circle_path(start_lat: float, start_lng: float, 
                                  end_lat: float, end_lng: float, 
                                  num_points: int = 10) -> List[Tuple[float, float]]:
        """
        Calculate great circle path between two points for smooth camera movement
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            num_points: Number of interpolation points
            
        Returns:
            List of (lat, lng) coordinate pairs along the path
        """
        path_points = []
        
        # Convert to radians
        lat1 = math.radians(start_lat)
        lng1 = math.radians(start_lng)
        lat2 = math.radians(end_lat)
        lng2 = math.radians(end_lng)
        
        # Calculate distance
        d = math.acos(math.sin(lat1) * math.sin(lat2) + 
                     math.cos(lat1) * math.cos(lat2) * math.cos(lng2 - lng1))
        
        for i in range(num_points + 1):
            f = i / num_points
            
            # Spherical interpolation
            a = math.sin((1 - f) * d) / math.sin(d) if math.sin(d) != 0 else (1 - f)
            b = math.sin(f * d) / math.sin(d) if math.sin(d) != 0 else f
            
            x = a * math.cos(lat1) * math.cos(lng1) + b * math.cos(lat2) * math.cos(lng2)
            y = a * math.cos(lat1) * math.sin(lng1) + b * math.cos(lat2) * math.sin(lng2)
            z = a * math.sin(lat1) + b * math.sin(lat2)
            
            # Convert back to lat/lng
            lat = math.atan2(z, math.sqrt(x*x + y*y))
            lng = math.atan2(y, x)
            
            path_points.append((math.degrees(lat), math.degrees(lng)))
        
        return path_points
    
    @staticmethod
    def calculate_optimal_altitude(location_type: str, distance_to_next: float = 0) -> float:
        """
        Calculate optimal camera altitude based on location type and context
        
        Args:
            location_type: Type of location (city, landmark, nature, etc.)
            distance_to_next: Distance to next location in km
            
        Returns:
            Optimal altitude in meters
        """
        base_altitudes = {
            'city': 25000,
            'landmark': 15000,
            'nature': 40000,
            'mountain': 60000,
            'island': 30000,
            'default': 35000
        }
        
        altitude = base_altitudes.get(location_type, base_altitudes['default'])
        
        # Adjust based on distance to next location
        if distance_to_next > 1000:  # Long distance transition
            altitude *= 1.5
        elif distance_to_next < 100:  # Short distance transition
            altitude *= 0.7
            
        return altitude
    
    @staticmethod
    def calculate_dynamic_timing(locations: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate dynamic timing based on location importance and distances
        
        Args:
            locations: List of geocoded locations
            
        Returns:
            List of durations for each location in seconds
        """
        if len(locations) < 2:
            return [5.0] * len(locations)
        
        durations = []
        
        for i, location in enumerate(locations):
            base_duration = 4.0  # Base duration in seconds
            
            # Adjust for location importance
            name = location.get('name', '').lower()
            
            # Major cities get more time
            if any(city in name for city in ['new york', 'paris', 'london', 'tokyo', 'rome']):
                base_duration *= 1.5
            
            # Landmarks get focused time
            if any(landmark in name for landmark in ['tower', 'bridge', 'temple', 'castle', 'cathedral']):
                base_duration *= 1.3
            
            # First and last locations get extra time
            if i == 0 or i == len(locations) - 1:
                base_duration *= 1.2
            
            durations.append(base_duration)
        
        return durations

class LocationAnalyzer:
    """Analyze locations for optimal camera treatment"""
    
    @staticmethod
    def classify_location_type(location: Dict[str, Any]) -> str:
        """
        Classify location type for appropriate camera treatment
        
        Args:
            location: Location data with name and coordinates
            
        Returns:
            Location type classification
        """
        name = location.get('name', '').lower()
        
        # City classification
        major_cities = ['new york', 'paris', 'london', 'tokyo', 'rome', 'beijing', 'sydney']
        if any(city in name for city in major_cities):
            return 'major_city'
        
        if any(word in name for word in ['city', 'town', 'metro']):
            return 'city'
        
        # Landmark classification
        landmarks = ['tower', 'bridge', 'statue', 'arch', 'monument', 'palace', 'castle']
        if any(landmark in name for landmark in landmarks):
            return 'landmark'
        
        # Nature classification
        nature_words = ['mountain', 'peak', 'hill', 'valley', 'canyon', 'cliff']
        if any(word in name for word in nature_words):
            return 'mountain'
        
        water_words = ['beach', 'coast', 'island', 'bay', 'lake', 'river', 'sea']
        if any(word in name for word in water_words):
            return 'water'
        
        # Cultural sites
        cultural_words = ['museum', 'temple', 'cathedral', 'church', 'shrine', 'gallery']
        if any(word in name for word in cultural_words):
            return 'cultural'
        
        return 'general'
    
    @staticmethod
    def suggest_camera_style(location_type: str) -> Dict[str, Any]:
        """
        Suggest camera movement style based on location type
        
        Args:
            location_type: Classification of location
            
        Returns:
            Camera style parameters
        """
        styles = {
            'major_city': {
                'approach_angle': 'high_oblique',
                'final_angle': 'medium_tilt',
                'movement_style': 'smooth_descent',
                'rotation': 'slow_pan',
                'altitude_ratio': 0.8
            },
            'landmark': {
                'approach_angle': 'dramatic_tilt',
                'final_angle': 'close_focus',
                'movement_style': 'reveal_approach',
                'rotation': 'orbit',
                'altitude_ratio': 0.5
            },
            'mountain': {
                'approach_angle': 'wide_panorama',
                'final_angle': 'elevated_view',
                'movement_style': 'steady_approach',
                'rotation': 'minimal',
                'altitude_ratio': 1.5
            },
            'water': {
                'approach_angle': 'low_approach',
                'final_angle': 'coastal_view',
                'movement_style': 'flowing',
                'rotation': 'gentle_sweep',
                'altitude_ratio': 0.9
            },
            'cultural': {
                'approach_angle': 'respectful_distance',
                'final_angle': 'architectural_focus',
                'movement_style': 'deliberate',
                'rotation': 'centered',
                'altitude_ratio': 0.7
            },
            'general': {
                'approach_angle': 'standard',
                'final_angle': 'balanced',
                'movement_style': 'smooth',
                'rotation': 'gentle',
                'altitude_ratio': 1.0
            }
        }
        
        return styles.get(location_type, styles['general'])

class EarthStudioExporter:
    """Export utilities for Earth Studio format"""
    
    @staticmethod
    def create_earth_studio_keyframe(time: float, lat: float, lng: float, 
                                   altitude: float, heading: float = 0, 
                                   tilt: float = 0, roll: float = 0) -> Dict[str, Any]:
        """
        Create Earth Studio compatible keyframe
        
        Args:
            time: Time in seconds
            lat, lng: Coordinates
            altitude: Camera altitude in meters
            heading, tilt, roll: Camera orientation
            
        Returns:
            Earth Studio keyframe dictionary
        """
        return {
            "time": time,
            "value": {
                "position": {
                    "lat": lat,
                    "lng": lng,
                    "altitude": altitude
                },
                "orientation": {
                    "heading": heading,
                    "tilt": tilt,
                    "roll": roll
                }
            },
            "interpolation": "ease_in_out",
            "easing": "cubic_bezier"
        }
    
    @staticmethod
    def add_cinematic_effects(project_data: Dict[str, Any], 
                            style: str = "cinematic") -> Dict[str, Any]:
        """
        Add cinematic effects to Earth Studio project
        
        Args:
            project_data: Base project data
            style: Cinematic style ('cinematic', 'documentary', 'adventure')
            
        Returns:
            Enhanced project data with effects
        """
        effects_config = {
            "cinematic": {
                "motion_blur": {"enabled": True, "strength": 0.8},
                "depth_of_field": {"enabled": True, "focus_distance": "auto"},
                "atmosphere": {"enabled": True, "density": 1.2},
                "lighting": {"time_of_day": "golden_hour"},
                "color_grading": {"saturation": 1.1, "contrast": 1.05}
            },
            "documentary": {
                "motion_blur": {"enabled": False},
                "depth_of_field": {"enabled": False},
                "atmosphere": {"enabled": True, "density": 1.0},
                "lighting": {"time_of_day": "natural"},
                "color_grading": {"saturation": 1.0, "contrast": 1.0}
            },
            "adventure": {
                "motion_blur": {"enabled": True, "strength": 1.0},
                "depth_of_field": {"enabled": True, "focus_distance": "auto"},
                "atmosphere": {"enabled": True, "density": 0.8},
                "lighting": {"time_of_day": "dramatic"},
                "color_grading": {"saturation": 1.2, "contrast": 1.1}
            }
        }
        
        # Add effects to project
        project_data["effects"] = effects_config.get(style, effects_config["cinematic"])
        
        return project_data
    
    @staticmethod
    def validate_earth_studio_project(project_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Earth Studio project data
        
        Args:
            project_data: Project data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ["project", "timeline"]
        for field in required_fields:
            if field not in project_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate timeline structure
        if "timeline" in project_data:
            timeline = project_data["timeline"]
            if "tracks" not in timeline:
                errors.append("Timeline missing tracks")
            else:
                for i, track in enumerate(timeline["tracks"]):
                    if "keyframes" not in track:
                        errors.append(f"Track {i} missing keyframes")
                    elif len(track["keyframes"]) < 2:
                        errors.append(f"Track {i} needs at least 2 keyframes")
        
        # Validate keyframes
        if "timeline" in project_data and "tracks" in project_data["timeline"]:
            for track in project_data["timeline"]["tracks"]:
                if "keyframes" in track:
                    for i, keyframe in enumerate(track["keyframes"]):
                        if "time" not in keyframe:
                            errors.append(f"Keyframe {i} missing time")
                        if "value" not in keyframe:
                            errors.append(f"Keyframe {i} missing value")
                        elif "position" not in keyframe["value"]:
                            errors.append(f"Keyframe {i} missing position")
        
        return len(errors) == 0, errors

class VideoStylePresets:
    """Predefined video style configurations"""
    
    @staticmethod
    def get_style_preset(style_name: str) -> Dict[str, Any]:
        """
        Get predefined style configuration
        
        Args:
            style_name: Name of the style preset
            
        Returns:
            Style configuration dictionary
        """
        presets = {
            "epic_journey": {
                "transition_duration": 4.0,
                "pause_duration": 3.0,
                "altitude_multiplier": 1.2,
                "camera_movement": "dramatic",
                "effects": "cinematic"
            },
            "quick_tour": {
                "transition_duration": 2.0,
                "pause_duration": 1.5,
                "altitude_multiplier": 0.8,
                "camera_movement": "fast",
                "effects": "clean"
            },
            "documentary": {
                "transition_duration": 3.0,
                "pause_duration": 4.0,
                "altitude_multiplier": 1.0,
                "camera_movement": "steady",
                "effects": "natural"
            },
            "adventure": {
                "transition_duration": 3.5,
                "pause_duration": 2.5,
                "altitude_multiplier": 1.1,
                "camera_movement": "dynamic",
                "effects": "high_contrast"
            }
        }
        
        return presets.get(style_name, presets["epic_journey"])
    
    @staticmethod
    def list_available_styles() -> List[str]:
        """Get list of available style presets"""
        return ["epic_journey", "quick_tour", "documentary", "adventure"]

# Utility functions for easy import
def calculate_distance_between_locations(loc1: Dict[str, Any], loc2: Dict[str, Any]) -> float:
    """Calculate distance between two locations in kilometers"""
    if not all([loc1.get('latitude'), loc1.get('longitude'), 
                loc2.get('latitude'), loc2.get('longitude')]):
        return 0.0
    
    point1 = (loc1['latitude'], loc1['longitude'])
    point2 = (loc2['latitude'], loc2['longitude'])
    
    return geodesic(point1, point2).kilometers

def optimize_video_timing(locations: List[Dict[str, Any]], 
                         total_duration: float = 30.0) -> List[float]:
    """
    Optimize timing for video based on location importance and distances
    
    Args:
        locations: List of locations
        total_duration: Target total duration in seconds
        
    Returns:
        List of durations for each location
    """
    if not locations:
        return []
    
    # Calculate base importance scores
    importance_scores = []
    for location in locations:
        score = 1.0
        location_type = LocationAnalyzer.classify_location_type(location)
        
        # Adjust score based on type
        type_multipliers = {
            'major_city': 1.5,
            'landmark': 1.3,
            'cultural': 1.2,
            'mountain': 1.1,
            'water': 1.1,
            'general': 1.0
        }
        score *= type_multipliers.get(location_type, 1.0)
        importance_scores.append(score)
    
    # Normalize scores to distribute total duration
    total_score = sum(importance_scores)
    durations = [(score / total_score) * total_duration for score in importance_scores]
    
    # Ensure minimum duration per location
    min_duration = 2.0
    for i in range(len(durations)):
        if durations[i] < min_duration:
            durations[i] = min_duration
    
    return durations

def create_smooth_camera_path(locations: List[Dict[str, Any]], 
                            style: str = "cinematic") -> List[Dict[str, Any]]:
    """
    Create smooth camera path with optimal transitions
    
    Args:
        locations: List of geocoded locations
        style: Camera movement style
        
    Returns:
        List of camera keyframes
    """
    if len(locations) < 2:
        return []
    
    keyframes = []
    style_config = VideoStylePresets.get_style_preset(style)
    
    current_time = 0.0
    
    for i, location in enumerate(locations):
        if not location.get('latitude') or not location.get('longitude'):
            continue
        
        lat, lng = location['latitude'], location['longitude']
        location_type = LocationAnalyzer.classify_location_type(location)
        camera_style = LocationAnalyzer.suggest_camera_style(location_type)
        
        # Calculate altitude
        base_altitude = CameraMovement.calculate_optimal_altitude(location_type)
        altitude = base_altitude * style_config['altitude_multiplier']
        
        # Calculate camera angles
        tilt = 45 if camera_style['final_angle'] == 'medium_tilt' else 30
        heading = (i * 30) % 360  # Vary heading for visual interest
        
        # Add keyframe
        keyframe = EarthStudioExporter.create_earth_studio_keyframe(
            time=current_time,
            lat=lat,
            lng=lng,
            altitude=altitude,
            heading=heading,
            tilt=tilt
        )
        
        keyframes.append(keyframe)
        current_time += style_config['transition_duration'] + style_config['pause_duration']
    
    return keyframes
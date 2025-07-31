"""
Google Earth Studio Integration Service
Generates Earth Studio project files and animation scripts from travel data
"""

import json
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EarthStudioKeyframe(BaseModel):
    """Earth Studio keyframe data"""
    time: float = Field(description="Time in seconds")
    latitude: float = Field(description="Camera latitude")
    longitude: float = Field(description="Camera longitude")
    altitude: float = Field(description="Camera altitude in meters")
    heading: float = Field(default=0, description="Camera heading in degrees")
    tilt: float = Field(default=0, description="Camera tilt in degrees")
    roll: float = Field(default=0, description="Camera roll in degrees")

class EarthStudioProject(BaseModel):
    """Complete Earth Studio project configuration"""
    title: str = Field(description="Project title")
    duration: float = Field(description="Total duration in seconds")
    keyframes: List[EarthStudioKeyframe] = Field(description="Animation keyframes")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project settings")

class EarthStudioService:
    def __init__(self):
        """Initialize Earth Studio service"""
        # Default animation settings
        self.default_settings = {
            "fps": 30,
            "resolution": {"width": 1920, "height": 1080},
            "quality": "high",
            "motion_blur": True,
            "atmosphere": True,
            "stars": False
        }
        
        # Animation parameters
        self.default_flight_altitude = 50000  # meters
        self.transition_duration = 3.0  # seconds per location
        self.pause_duration = 2.0  # seconds to pause at each location
        
    def calculate_camera_path(self, locations: List[Dict[str, Any]], 
                            story_timeline: List[str] = None) -> List[EarthStudioKeyframe]:
        """
        Calculate smooth camera path between locations
        
        Args:
            locations: List of geocoded locations with lat/lng
            story_timeline: Optional timeline for timing
            
        Returns:
            List of keyframes for smooth animation
        """
        keyframes = []
        current_time = 0.0
        
        for i, location in enumerate(locations):
            if not location.get('latitude') or not location.get('longitude'):
                continue
                
            lat = location['latitude']
            lng = location['longitude']
            
            # Calculate appropriate altitude based on location type
            altitude = self._calculate_altitude(location, i, len(locations))
            
            # Calculate camera angles for cinematic effect
            heading, tilt = self._calculate_camera_angles(location, i, len(locations))
            
            # Add approach keyframe (flying in)
            if i > 0:
                approach_time = current_time + self.transition_duration * 0.7
                keyframes.append(EarthStudioKeyframe(
                    time=approach_time,
                    latitude=lat,
                    longitude=lng,
                    altitude=altitude * 2,  # Higher approach
                    heading=heading,
                    tilt=45,  # Tilted approach
                    roll=0
                ))
            
            # Add main location keyframe
            location_time = current_time + self.transition_duration
            keyframes.append(EarthStudioKeyframe(
                time=location_time,
                latitude=lat,
                longitude=lng,
                altitude=altitude,
                heading=heading,
                tilt=tilt,
                roll=0
            ))
            
            # Add pause keyframe (linger at location)
            pause_time = location_time + self.pause_duration
            keyframes.append(EarthStudioKeyframe(
                time=pause_time,
                latitude=lat,
                longitude=lng,
                altitude=altitude * 0.8,  # Slightly closer for detail
                heading=heading + 15,  # Slight rotation
                tilt=tilt,
                roll=0
            ))
            
            current_time = pause_time
            
        return keyframes
    
    def _calculate_altitude(self, location: Dict[str, Any], index: int, total: int) -> float:
        """Calculate appropriate camera altitude for location"""
        # Base altitude
        altitude = self.default_flight_altitude
        
        # Adjust for location type
        location_name = location.get('name', '').lower()
        
        if any(word in location_name for word in ['city', 'tokyo', 'new york', 'paris', 'london']):
            altitude = 25000  # Lower for cities
        elif any(word in location_name for word in ['mountain', 'peak', 'alps']):
            altitude = 80000  # Higher for mountains
        elif any(word in location_name for word in ['island', 'beach', 'coast']):
            altitude = 35000  # Medium for coastal areas
        
        # Add variety - alternate high and low shots
        if index % 2 == 1:
            altitude *= 0.7
            
        return altitude
    
    def _calculate_camera_angles(self, location: Dict[str, Any], 
                                index: int, total: int) -> tuple[float, float]:
        """Calculate cinematic camera angles"""
        # Vary heading for visual interest
        heading = (index * 45) % 360
        
        # Vary tilt for different perspectives
        if index == 0:  # Opening shot - dramatic angle
            tilt = 60
        elif index == total - 1:  # Closing shot - gentle angle
            tilt = 30
        else:  # Middle shots - varied angles
            tilt = 45 + (index % 3) * 10
            
        return heading, tilt
    
    def generate_earth_studio_project(self, 
                                    locations: List[Dict[str, Any]],
                                    timeline: List[str] = None,
                                    title: str = "Map Memoir Journey") -> EarthStudioProject:
        """
        Generate complete Earth Studio project
        
        Args:
            locations: Geocoded locations with coordinates
            timeline: Story timeline for narration sync
            title: Project title
            
        Returns:
            Complete Earth Studio project configuration
        """
        # Generate keyframes
        keyframes = self.calculate_camera_path(locations, timeline)
        
        # Calculate total duration
        total_duration = keyframes[-1].time + 2.0 if keyframes else 10.0
        
        # Create project
        project = EarthStudioProject(
            title=title,
            duration=total_duration,
            keyframes=keyframes,
            settings=self.default_settings.copy()
        )
        
        return project
    
    def export_to_earth_studio_json(self, project: EarthStudioProject) -> str:
        """
        Export project to Earth Studio compatible JSON format
        
        Args:
            project: Earth Studio project configuration
            
        Returns:
            JSON string compatible with Earth Studio
        """
        # Convert to Earth Studio format
        earth_studio_data = {
            "version": "1.0",
            "project": {
                "name": project.title,
                "duration": project.duration,
                "fps": project.settings.get("fps", 30),
                "resolution": project.settings.get("resolution", {"width": 1920, "height": 1080})
            },
            "timeline": {
                "tracks": [
                    {
                        "name": "Camera",
                        "type": "camera",
                        "keyframes": [
                            {
                                "time": kf.time,
                                "value": {
                                    "position": {
                                        "lat": kf.latitude,
                                        "lng": kf.longitude,
                                        "altitude": kf.altitude
                                    },
                                    "rotation": {
                                        "heading": kf.heading,
                                        "tilt": kf.tilt,
                                        "roll": kf.roll
                                    }
                                },
                                "interpolation": "ease_in_out"
                            }
                            for kf in project.keyframes
                        ]
                    }
                ]
            },
            "effects": [
                {
                    "name": "Atmosphere",
                    "enabled": project.settings.get("atmosphere", True)
                },
                {
                    "name": "Motion Blur",
                    "enabled": project.settings.get("motion_blur", True)
                }
            ]
        }
        
        return json.dumps(earth_studio_data, indent=2)
    
    def generate_prompt_for_ai_enhancement(self, 
                                         locations: List[Dict[str, Any]],
                                         timeline: List[str]) -> str:
        """
        Generate prompt for AI to enhance the video with narrative elements
        
        Args:
            locations: Travel locations
            timeline: Story timeline
            
        Returns:
            Prompt for AI video enhancement
        """
        locations_text = ", ".join([loc.get('name', 'Unknown') for loc in locations])
        timeline_text = "\n".join([f"{i+1}. {event}" for i, event in enumerate(timeline)])
        
        prompt = f"""Create a cinematic Google Earth Studio animation script for a travel story.

Journey Overview:
Locations: {locations_text}

Story Timeline:
{timeline_text}

Please enhance this with:
1. Dramatic camera movements that match the story beats
2. Optimal timing for each location reveal
3. Smooth transitions that follow realistic flight paths
4. Cinematic angles that highlight each location's unique features
5. Pacing that allows viewers to appreciate each destination

Focus on creating a compelling visual narrative that brings this travel story to life through Earth's satellite imagery."""

        return prompt

# Global instance
earth_studio_service = EarthStudioService()

# Convenience functions
def create_earth_studio_project(locations: List[Dict[str, Any]], 
                               timeline: List[str] = None,
                               title: str = "Map Memoir Journey") -> Dict[str, Any]:
    """Create Earth Studio project from travel data"""
    project = earth_studio_service.generate_earth_studio_project(locations, timeline, title)
    return project.dict()

def export_earth_studio_json(locations: List[Dict[str, Any]], 
                           timeline: List[str] = None,
                           title: str = "Map Memoir Journey") -> str:
    """Export travel data to Earth Studio JSON"""
    project = earth_studio_service.generate_earth_studio_project(locations, timeline, title)
    return earth_studio_service.export_to_earth_studio_json(project)
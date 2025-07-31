"""
AI Service for Map Memoir
Handles Google Gemini AI and OpenAI integration for story and timeline generation
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
import google.generativeai as genai
import openai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Pydantic models
class LocationInput(BaseModel):
    locations: List[str] = Field(description="An ordered array of locations for a trip")

class TimelineOutput(BaseModel):
    timeline: List[str] = Field(description="An array of events representing the timeline of the story")

class StoryInput(BaseModel):
    locations: List[str] = Field(description="Locations for the story")
    timeline: List[str] = Field(description="Timeline events")
    voice_transcript: Optional[str] = Field(default=None, description="User's voice input transcript")
    theme: Optional[str] = Field(default="adventure", description="Story theme")

class StoryOutput(BaseModel):
    story: str = Field(description="Generated story content")
    title: str = Field(description="Story title")
    summary: str = Field(description="Story summary")

class AIService:
    def __init__(self):
        """Initialize AI services - prioritize OpenAI GPT-3.5-turbo"""
        # OpenAI setup (primary)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            print("OpenAI GPT-3.5-turbo client initialized (primary)")
        else:
            self.openai_client = None
            print("OpenAI API key not found")
        
        # Google Gemini setup (backup)
        self.gemini_api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("Gemini AI configured (backup)")
        else:
            self.gemini_model = None
            print("Gemini API key not found")
    
    def _create_generation_config(self, temperature: float = 0.7, max_tokens: int = 2048) -> dict:
        """Create generation configuration"""
        return {
            'temperature': temperature,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': max_tokens,
        }
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from AI response"""
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
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {}
    
    async def generate_timeline_from_locations(self, input_data: LocationInput) -> TimelineOutput:
        """Generate timeline from locations using Gemini AI"""
        
        locations_list = "\n".join([f"- {location}" for location in input_data.locations])
        
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
        
        try:
            if self.openai_client:
                # Use OpenAI GPT-3.5-turbo (primary)
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content
                parsed_response = self._parse_json_response(response_text)
                timeline = parsed_response.get('timeline', [])
                
            elif self.gemini_model:
                # Fallback to Gemini
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=self._create_generation_config()
                )
                
                response_text = response.text.strip()
                parsed_response = self._parse_json_response(response_text)
                timeline = parsed_response.get('timeline', [])
                
            else:
                raise Exception("No AI service available")
            
            # Fallback if parsing fails
            if not timeline:
                timeline = [f"Visit {location}" for location in input_data.locations]
            
            return TimelineOutput(timeline=timeline)
            
        except Exception as e:
            print(f"Error generating timeline: {str(e)}")
            # Fallback timeline
            fallback_timeline = [f"Visit {location}" for location in input_data.locations]
            return TimelineOutput(timeline=fallback_timeline)
    
    async def generate_story_from_data(self, input_data: StoryInput) -> StoryOutput:
        """Generate story from locations, timeline, and optional voice input"""
        
        locations_text = ", ".join(input_data.locations)
        timeline_text = "\n".join([f"{i+1}. {event}" for i, event in enumerate(input_data.timeline)])
        
        voice_context = ""
        if input_data.voice_transcript:
            voice_context = f"\n\nUser's personal input: '{input_data.voice_transcript}'\nIncorporate this personal touch into the story."
        
        prompt = f"""You are a creative storyteller. Create an engaging travel story based on the following information:

**Locations visited:** {locations_text}

**Timeline of events:**
{timeline_text}

**Story theme:** {input_data.theme}{voice_context}

Create a compelling narrative that brings this journey to life. The story should be engaging, descriptive, and capture the essence of each location and event. Make it feel like a personal travel memoir.

Return the result as a JSON object with these fields:
- "title": A catchy title for the story
- "story": The full story content (500-800 words)
- "summary": A brief summary (50-100 words)

Example format:
{{
  "title": "A Journey Through Europe",
  "story": "The adventure began in the bustling streets of Paris...",
  "summary": "An unforgettable journey through three iconic European cities..."
}}"""
        
        try:
            if self.openai_client:
                # Use OpenAI GPT-3.5-turbo (primary)
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=3000
                )
                
                response_text = response.choices[0].message.content
                parsed_response = self._parse_json_response(response_text)
                
            elif self.gemini_model:
                # Fallback to Gemini
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=self._create_generation_config(temperature=0.8, max_tokens=3000)
                )
                
                response_text = response.text.strip()
                parsed_response = self._parse_json_response(response_text)
                
            else:
                raise Exception("No AI service available")
            
            # Extract or create fallback content
            title = parsed_response.get('title', f"Journey to {locations_text}")
            story = parsed_response.get('story', f"An amazing adventure through {locations_text}.")
            summary = parsed_response.get('summary', f"A travel story covering {len(input_data.locations)} locations.")
            
            return StoryOutput(title=title, story=story, summary=summary)
            
        except Exception as e:
            print(f"Error generating story: {str(e)}")
            # Fallback story
            return StoryOutput(
                title=f"Journey to {locations_text}",
                story=f"An unforgettable adventure through {locations_text}. Each destination brought new experiences and memories that will last a lifetime.",
                summary=f"A travel story covering {len(input_data.locations)} amazing locations."
            )
    
    async def extract_locations_from_text(self, text: str) -> List[str]:
        """Extract location names from text using AI"""
        
        prompt = f"""Extract all location names (cities, countries, landmarks, etc.) from the following text. Return only location names that are real places.

Text: "{text}"

Return the result as a JSON object with a "locations" field containing an array of location names in the order they appear.

Example format:
{{
  "locations": ["Paris", "Rome", "Tokyo"]
}}"""
        
        try:
            if self.openai_client:
                # Use OpenAI GPT-3.5-turbo (primary)
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                
                response_text = response.choices[0].message.content
                parsed_response = self._parse_json_response(response_text)
                locations = parsed_response.get('locations', [])
                
            elif self.gemini_model:
                # Fallback to Gemini
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=self._create_generation_config(temperature=0.3)
                )
                
                response_text = response.text.strip()
                parsed_response = self._parse_json_response(response_text)
                locations = parsed_response.get('locations', [])
                
            else:
                raise Exception("No AI service available")
            
            return locations if locations else []
            
        except Exception as e:
            print(f"Error extracting locations: {str(e)}")
            return []

# Global instance
ai_service = AIService()

# Convenience functions
async def generate_timeline_from_locations(locations: List[str]) -> Dict[str, Any]:
    """Generate timeline from locations"""
    input_data = LocationInput(locations=locations)
    result = await ai_service.generate_timeline_from_locations(input_data)
    return result.dict()

async def generate_story_from_data(locations: List[str], timeline: List[str], 
                                 voice_transcript: Optional[str] = None, 
                                 theme: str = "adventure") -> Dict[str, Any]:
    """Generate story from data"""
    input_data = StoryInput(
        locations=locations, 
        timeline=timeline, 
        voice_transcript=voice_transcript,
        theme=theme
    )
    result = await ai_service.generate_story_from_data(input_data)
    return result.dict()

async def extract_locations_from_text(text: str) -> List[str]:
    """Extract locations from text"""
    return await ai_service.extract_locations_from_text(text)
"""
Stories API routes for Map Memoir
Handles story creation, management, and AI generation
"""

from flask import Blueprint, request, jsonify
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from services.ai_service import generate_timeline_from_locations, generate_story_from_data, extract_locations_from_text
from services.maps_service import geocode_locations

# Create blueprint for stories routes
stories_bp = Blueprint('stories', __name__)

# In-memory storage for demo (in production, use a database)
stories_db = {}

@stories_bp.route('/api/stories/create', methods=['POST'])
def create_story_route():
    """
    Create a new story from locations, timeline, and optional voice input
    
    Expected JSON body:
    {
        "locations": ["Paris", "Rome", "Tokyo"],
        "timeline": ["Arrival in Paris", "Exploring Rome", "Tokyo adventures"],
        "voice_transcript": "It was an amazing trip...",
        "theme": "adventure",
        "title": "My European Adventure"
    }
    
    Returns:
    {
        "story_id": "uuid",
        "title": "Generated Title",
        "story": "Full story content...",
        "summary": "Brief summary...",
        "locations": [...],
        "timeline": [...],
        "created_at": "2025-07-13T..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'Locations field is required'}), 400
        
        locations = data['locations']
        timeline = data.get('timeline', [])
        voice_transcript = data.get('voice_transcript')
        theme = data.get('theme', 'adventure')
        user_title = data.get('title')
        
        if not isinstance(locations, list) or len(locations) == 0:
            return jsonify({'error': 'Locations must be a non-empty array'}), 400
        
        # Generate timeline if not provided
        if not timeline:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                timeline_result = loop.run_until_complete(generate_timeline_from_locations(locations))
                timeline = timeline_result.get('timeline', [])
            finally:
                loop.close()
        
        # Generate story using AI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            story_result = loop.run_until_complete(
                generate_story_from_data(locations, timeline, voice_transcript, theme)
            )
        finally:
            loop.close()
        
        # Create story record
        story_id = str(uuid.uuid4())
        story_data = {
            'story_id': story_id,
            'title': user_title or story_result.get('title', 'Untitled Story'),
            'story': story_result.get('story', ''),
            'summary': story_result.get('summary', ''),
            'locations': locations,
            'timeline': timeline,
            'voice_transcript': voice_transcript,
            'theme': theme,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Store in memory (use database in production)
        stories_db[story_id] = story_data
        
        return jsonify(story_data)
        
    except Exception as e:
        return jsonify({'error': f'Story creation failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/create-from-text', methods=['POST'])
def create_story_from_text_route():
    """
    Create a story from text input (extracts locations automatically)
    
    Expected JSON body:
    {
        "text": "I traveled from New York to Paris, then to Rome...",
        "theme": "adventure",
        "title": "My Trip"
    }
    
    Returns:
    {
        "story_id": "uuid",
        "title": "Generated Title",
        "story": "Full story content...",
        "extracted_locations": ["New York", "Paris", "Rome"],
        "geocoded_locations": [...],
        "timeline": [...],
        "created_at": "2025-07-13T..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        theme = data.get('theme', 'adventure')
        user_title = data.get('title')
        
        # Extract locations from text
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            extracted_locations = loop.run_until_complete(extract_locations_from_text(text))
        finally:
            loop.close()
        
        if not extracted_locations:
            return jsonify({'error': 'No locations found in the text'}), 400
        
        # Geocode the locations
        from services.maps_service import maps_service
        geocoded_locations = maps_service.geocode_locations(extracted_locations)
        
        # Generate timeline
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            timeline_result = loop.run_until_complete(generate_timeline_from_locations(extracted_locations))
            timeline = timeline_result.get('timeline', [])
        finally:
            loop.close()
        
        # Generate story
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            story_result = loop.run_until_complete(
                generate_story_from_data(extracted_locations, timeline, text, theme)
            )
        finally:
            loop.close()
        
        # Create story record
        story_id = str(uuid.uuid4())
        story_data = {
            'story_id': story_id,
            'title': user_title or story_result.get('title', 'Untitled Story'),
            'story': story_result.get('story', ''),
            'summary': story_result.get('summary', ''),
            'locations': extracted_locations,
            'geocoded_locations': [loc.dict() for loc in geocoded_locations],
            'timeline': timeline,
            'original_text': text,
            'theme': theme,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Store in memory
        stories_db[story_id] = story_data
        
        return jsonify(story_data)
        
    except Exception as e:
        return jsonify({'error': f'Story creation from text failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/<story_id>', methods=['GET'])
def get_story_route(story_id):
    """
    Get a story by ID
    
    Returns:
    {
        "story_id": "uuid",
        "title": "Story Title",
        "story": "Full content...",
        ...
    }
    """
    try:
        story = stories_db.get(story_id)
        
        if story:
            return jsonify(story)
        else:
            return jsonify({'error': f'Story not found: {story_id}'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Get story failed: {str(e)}'}), 500

@stories_bp.route('/api/stories', methods=['GET'])
def list_stories_route():
    """
    List all stories
    
    Optional query parameters:
    - limit: number of stories to return (default: 50)
    - offset: number of stories to skip (default: 0)
    
    Returns:
    {
        "stories": [...],
        "total": 10,
        "limit": 50,
        "offset": 0
    }
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Get all stories and sort by creation date
        all_stories = list(stories_db.values())
        all_stories.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply pagination
        paginated_stories = all_stories[offset:offset + limit]
        
        return jsonify({
            'stories': paginated_stories,
            'total': len(all_stories),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return jsonify({'error': f'List stories failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/<story_id>', methods=['PUT'])
def update_story_route(story_id):
    """
    Update a story
    
    Expected JSON body:
    {
        "title": "New Title",
        "story": "Updated content...",
        "summary": "Updated summary..."
    }
    
    Returns:
    {
        "story_id": "uuid",
        "title": "Updated Title",
        ...
    }
    """
    try:
        story = stories_db.get(story_id)
        
        if not story:
            return jsonify({'error': f'Story not found: {story_id}'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['title', 'story', 'summary', 'theme']
        for field in allowed_fields:
            if field in data:
                story[field] = data[field]
        
        story['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated story
        stories_db[story_id] = story
        
        return jsonify(story)
        
    except Exception as e:
        return jsonify({'error': f'Update story failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/<story_id>', methods=['DELETE'])
def delete_story_route(story_id):
    """
    Delete a story
    
    Returns:
    {
        "message": "Story deleted successfully"
    }
    """
    try:
        if story_id in stories_db:
            del stories_db[story_id]
            return jsonify({'message': 'Story deleted successfully'})
        else:
            return jsonify({'error': f'Story not found: {story_id}'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Delete story failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/regenerate/<story_id>', methods=['POST'])
def regenerate_story_route(story_id):
    """
    Regenerate story content using AI
    
    Expected JSON body:
    {
        "theme": "adventure",
        "regenerate_timeline": false
    }
    
    Returns:
    {
        "story_id": "uuid",
        "title": "New Title",
        "story": "Regenerated content...",
        ...
    }
    """
    try:
        story = stories_db.get(story_id)
        
        if not story:
            return jsonify({'error': f'Story not found: {story_id}'}), 404
        
        data = request.get_json() or {}
        theme = data.get('theme', story.get('theme', 'adventure'))
        regenerate_timeline = data.get('regenerate_timeline', False)
        
        locations = story['locations']
        timeline = story['timeline']
        voice_transcript = story.get('voice_transcript')
        
        # Regenerate timeline if requested
        if regenerate_timeline:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                timeline_result = loop.run_until_complete(generate_timeline_from_locations(locations))
                timeline = timeline_result.get('timeline', timeline)
            finally:
                loop.close()
        
        # Regenerate story
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            story_result = loop.run_until_complete(
                generate_story_from_data(locations, timeline, voice_transcript, theme)
            )
        finally:
            loop.close()
        
        # Update story
        story.update({
            'title': story_result.get('title', story['title']),
            'story': story_result.get('story', story['story']),
            'summary': story_result.get('summary', story['summary']),
            'timeline': timeline,
            'theme': theme,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Save updated story
        stories_db[story_id] = story
        
        return jsonify(story)
        
    except Exception as e:
        return jsonify({'error': f'Story regeneration failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/search', methods=['POST'])
def search_stories_route():
    """
    Search stories by keywords
    
    Expected JSON body:
    {
        "query": "Paris adventure",
        "fields": ["title", "story", "locations"]
    }
    
    Returns:
    {
        "stories": [...],
        "count": 5,
        "query": "Paris adventure"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query field is required'}), 400
        
        query = data['query'].lower()
        search_fields = data.get('fields', ['title', 'story', 'summary', 'locations'])
        
        matching_stories = []
        
        for story in stories_db.values():
            # Search in specified fields
            for field in search_fields:
                if field in story:
                    field_value = story[field]
                    
                    # Handle different field types
                    if isinstance(field_value, str):
                        if query in field_value.lower():
                            matching_stories.append(story)
                            break
                    elif isinstance(field_value, list):
                        if any(query in str(item).lower() for item in field_value):
                            matching_stories.append(story)
                            break
        
        # Remove duplicates and sort by creation date
        unique_stories = {story['story_id']: story for story in matching_stories}.values()
        sorted_stories = sorted(unique_stories, key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'stories': list(sorted_stories),
            'count': len(sorted_stories),
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': f'Story search failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/export/<story_id>', methods=['GET'])
def export_story_route(story_id):
    """
    Export story in different formats
    
    Query parameters:
    - format: json, txt, md (default: json)
    
    Returns:
    Story content in requested format
    """
    try:
        story = stories_db.get(story_id)
        
        if not story:
            return jsonify({'error': f'Story not found: {story_id}'}), 404
        
        export_format = request.args.get('format', 'json').lower()
        
        if export_format == 'json':
            return jsonify(story)
        
        elif export_format == 'txt':
            content = f"Title: {story['title']}\n\n"
            content += f"Summary: {story['summary']}\n\n"
            content += f"Locations: {', '.join(story['locations'])}\n\n"
            content += f"Story:\n{story['story']}\n\n"
            content += f"Created: {story['created_at']}"
            
            return content, 200, {'Content-Type': 'text/plain'}
        
        elif export_format == 'md':
            content = f"# {story['title']}\n\n"
            content += f"## Summary\n{story['summary']}\n\n"
            content += f"## Locations\n"
            for location in story['locations']:
                content += f"- {location}\n"
            content += f"\n## Timeline\n"
            for i, event in enumerate(story['timeline'], 1):
                content += f"{i}. {event}\n"
            content += f"\n## Story\n{story['story']}\n\n"
            content += f"*Created: {story['created_at']}*"
            
            return content, 200, {'Content-Type': 'text/markdown'}
        
        else:
            return jsonify({'error': f'Unsupported format: {export_format}'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Story export failed: {str(e)}'}), 500

@stories_bp.route('/api/stories/test', methods=['GET'])
def test_stories_route():
    """Test endpoint for stories functionality"""
    try:
        # Test story creation with sample data
        test_locations = ["Paris", "Rome"]
        test_theme = "adventure"
        
        # Test timeline generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            timeline_result = loop.run_until_complete(generate_timeline_from_locations(test_locations))
            timeline_success = bool(timeline_result.get('timeline'))
        except Exception as e:
            timeline_success = False
            timeline_error = str(e)
        finally:
            loop.close()
        
        # Test story generation
        if timeline_success:
            test_timeline = timeline_result['timeline']
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                story_result = loop.run_until_complete(
                    generate_story_from_data(test_locations, test_timeline, None, test_theme)
                )
                story_success = bool(story_result.get('story'))
            except Exception as e:
                story_success = False
                story_error = str(e)
            finally:
                loop.close()
        else:
            story_success = False
            story_error = "Timeline generation failed"
        
        return jsonify({
            'status': 'success' if timeline_success and story_success else 'partial',
            'message': 'Stories service test completed',
            'test_results': {
                'timeline_generation': {
                    'success': timeline_success,
                    'error': timeline_error if not timeline_success else None
                },
                'story_generation': {
                    'success': story_success,
                    'error': story_error if not story_success else None
                },
                'test_data': {
                    'locations': test_locations,
                    'theme': test_theme
                }
            },
            'stories_count': len(stories_db)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Stories test failed: {str(e)}'
        }), 500
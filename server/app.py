import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.generate_script import script_bp
from routes.generate_audio import audio_bp
from routes.enhanced_audio import enhanced_audio_bp
from routes.ai_locations import ai_locations_bp
from routes.earth_studio import earth_studio_bp
from datetime import datetime


# Import routes with error handling
try:
    from routes.generate_script import script_bp
    script_available = True
    print("✅ Script route loaded")
except ImportError as e:
    script_bp = None
    script_available = False
    print(f"⚠️ Script route failed: {e}")

# Use enhanced audio instead of old generate_audio
try:
    from routes.enhanced_audio import enhanced_audio_bp
    enhanced_audio_available = True
    print("✅ Enhanced audio route loaded")
except ImportError as e:
    enhanced_audio_bp = None
    enhanced_audio_available = False
    print(f"⚠️ Enhanced audio route failed: {e}")

# Import AI routes
try:
    from routes.ai_locations import ai_locations_bp
    ai_locations_available = True
    print("✅ AI locations route loaded")
except ImportError as e:
    ai_locations_bp = None
    ai_locations_available = False
    print(f"⚠️ AI locations route failed: {e}")

# Import Earth Studio routes
try:
    from routes.earth_studio import earth_studio_bp
    earth_studio_available = True
    print("✅ Earth Studio route loaded")
except ImportError as e:
    earth_studio_bp = None
    earth_studio_available = False
    print(f"⚠️ Earth Studio route failed: {e}")
    
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# app.register_blueprint(script_bp)
# app.register_blueprint(audio_bp) 

# Register available blueprints
if script_available and script_bp:
    app.register_blueprint(script_bp)
    print("✅ Registered script blueprint")

if enhanced_audio_available and enhanced_audio_bp:
    app.register_blueprint(enhanced_audio_bp)
    print("✅ Registered enhanced audio blueprint")

if ai_locations_available and ai_locations_bp:
    app.register_blueprint(ai_locations_bp)
    print("✅ Registered AI locations blueprint")

if earth_studio_available and earth_studio_bp:
    app.register_blueprint(earth_studio_bp)
    print("✅ Registered Earth Studio blueprint")

# Root route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Map Memoir API - Earth Studio Focus',
        'status': 'running',
        'version': '3.0.0',
        'available_services': {
            'script_generation': script_available,
            'enhanced_audio': enhanced_audio_available,
            'ai_locations': ai_locations_available,
            'earth_studio': earth_studio_available
        },
        'earth_studio_endpoints': {
            'test': '/api/earth-studio/test',
            'create_project': '/api/earth-studio/create-project',
            'preview': '/api/earth-studio/preview'
        } if earth_studio_available else {}
    })

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Map Memoir API test endpoint',
        'services': {
            'script_service': 'available' if script_available else 'unavailable',
            'enhanced_audio_service': 'available' if enhanced_audio_available else 'unavailable',
            'ai_locations_service': 'available' if ai_locations_available else 'unavailable',
            'earth_studio_service': 'available' if earth_studio_available else 'unavailable'
        },
        'web_interface': 'http://localhost:8000/earth_studio_viewer.html',
        'focus': 'Earth Studio development with web interface',
        'next_tests': [
            'Try /earth_studio_viewer.html for web interface',
            'Try /api/earth-studio/test to check Earth Studio API'
        ]
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

# Static file routes
@app.route('/earth_studio_viewer.html')
def earth_studio_viewer():
    """Serve the Earth Studio viewer HTML page"""
    try:
        return send_from_directory('.', 'earth_studio_viewer.html')
    except FileNotFoundError:
        return jsonify({'error': 'Earth Studio viewer not found'}), 404

@app.route('/favicon.ico') 
def favicon():
    """Handle favicon requests"""
    return '', 204

if __name__ == "__main__":
    print(os.getenv("PORT"))
    print("🚀 Starting Map Memoir API - Earth Studio Focus...?")
    print(f"📋 Script service: {'✅ Available' if script_available else '❌ Unavailable'}")
    print(f"🎙️ Enhanced audio: {'✅ Available' if enhanced_audio_available else '❌ Unavailable'}")
    print(f"🤖 AI locations: {'✅ Available' if ai_locations_available else '❌ Unavailable'}")
    print(f"🎬 Earth Studio: {'✅ Available' if earth_studio_available else '❌ Unavailable'}")
    print("🌐 Focus: Earth Studio video generation")
    print("🌐 Web interface: http://localhost:8000/earth_studio_viewer.html")
    
    port = int(os.getenv('PORT', 8000))
    print(f"🔗 Server will run on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)

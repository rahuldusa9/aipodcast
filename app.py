"""
Flask Web Application for Podcast Generator
Provides REST API and web interface for podcast generation
"""

import os
import asyncio
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

import edge_tts
from podcast_generator import PodcastGenerator
from utils.voice_manager import (
    list_all_voices, 
    organize_voices_by_locale,
    get_demo_text_for_locale,
    PODCAST_VOICES
)
from utils.script_parser import parse_podcast_script, get_script_statistics
from utils.prosody import list_available_emotions


app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global podcast generator instance
podcast_generator = PodcastGenerator(output_dir=OUTPUT_DIR)


@app.route('/')
def index():
    """Serve main web interface"""
    return send_file('static/index.html')


async def get_voices():
    """
    Get all available voices organized by locale
    
    Returns:
        JSON: {
            "en-US": [
                {"id": "en-US-AriaNeural", "name": "Aria", "gender": "Female"},
                ...
            ],
            ...
        }
    """
    try:
        voices = await list_all_voices()
        organized = organize_voices_by_locale(voices)
        
        return jsonify({
            'success': True,
            'voices': organized,
            'total': len(voices)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/voices/default', methods=['GET'])
def get_default_voices():
    """
    Get default podcast voice assignments
    
    Returns:
        JSON: Default voice mapping for speakers
    """
    return jsonify({
        'success': True,
        'voices': PODCAST_VOICES
    })


@app.route('/api/emotions', methods=['GET'])
def get_emotions():
    """
    Get list of available emotions with descriptions
    
    Returns:
        JSON: List of emotions with prosody details
    """
    emotions = list_available_emotions()
    
    return jsonify({
        'success': True,
        'emotions': emotions
    })


async def voice_demo(voice_id):
    """
    Generate demo audio for a specific voice
    
    Args:
        voice_id (str): Edge TTS voice ID (e.g., 'en-US-AriaNeural')
        
    Returns:
        Audio: MP3 demo file
    """
    try:
        # Detect language from voice ID and get appropriate demo text
        locale = voice_id.split('-')
        if len(locale) >= 2:
            locale = f"{locale[0]}-{locale[1]}"
        else:
            locale = 'en-US'
        
        demo_text = get_demo_text_for_locale(locale)
        
        # Generate audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir=OUTPUT_DIR)
        temp_path = temp_file.name
        temp_file.close()
        
        communicate = edge_tts.Communicate(demo_text, voice_id)
        await communicate.save(temp_path)
        
        return send_file(
            temp_path,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name=f"demo_{voice_id}.mp3"
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate demo: {str(e)}'
        }), 500


async def generate_podcast():
    """
    Generate podcast from topic and requirements
    
    Request body:
    {
        "topic": "Artificial Intelligence",
        "requirements": {
            "duration_minutes": 5,
            "speakers": ["HOST", "GUEST"],
            "tone": "professional",  # or casual, educational, entertaining
            "structure": "interview",
            "key_points": ["Point 1", "Point 2"]
        }
    }
    
    Returns:
        Audio: Generated podcast MP3 file
    """
    try:
        data = request.json
        topic = data.get('topic')
        requirements = data.get('requirements', {})
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Extract requirements
        duration_minutes = requirements.get('duration_minutes', 5)
        tone = requirements.get('tone', 'professional')
        key_points = requirements.get('key_points', [])
        language = requirements.get('language', 'en-US')
        custom_voices = data.get('voices', None)
        
        # Generate script using Gemini AI
        print(f"Generating script for topic: {topic}")
        print(f"  Language: {language}, Duration: {duration_minutes} min, Tone: {tone}")
        if key_points:
            print(f"  Key points: {', '.join(key_points)}")
        if custom_voices:
            print(f"  Custom voices: {custom_voices}")
        
        script = podcast_generator.generate_template_script(
            topic,
            duration_minutes=duration_minutes,
            tone=tone,
            key_points=key_points,
            language=language
        )
        
        # Generate podcast
        print(f"Generating podcast audio...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"podcast_{timestamp}.mp3"
        
        output_path = await podcast_generator.generate_from_script(
            script,
            output_filename=output_filename,
            custom_voices=custom_voices,
            language=language
        )
        
        # Return the audio file
        return send_file(
            output_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f"podcast_{topic[:30].replace(' ', '_')}.mp3"
        )
    
    except Exception as e:
        print(f"Error generating podcast: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


async def generate_from_script():
    """
    Generate podcast from custom script
    
    Request body:
    {
        "script": "[HOST|excited] Welcome!\n[GUEST|calm] Thanks!",
        "voices": {
            "HOST": "en-US-JennyNeural",
            "GUEST": "en-US-GuyNeural"
        }
    }
    
    Returns:
        Audio: Generated podcast MP3 file
    """
    try:
        data = request.json
        script_text = data.get('script')
        custom_voices = data.get('voices')
        
        if not script_text:
            return jsonify({
                'success': False,
                'error': 'Script is required'
            }), 400
        
        # Validate script
        segments = parse_podcast_script(script_text)
        if not segments:
            return jsonify({
                'success': False,
                'error': 'Invalid script format. Use [SPEAKER|emotion] text'
            }), 400
        
        # Generate podcast
        print(f"Generating podcast from custom script ({len(segments)} segments)")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"podcast_custom_{timestamp}.mp3"
        
        output_path = await podcast_generator.generate_from_script(
            script_text,
            custom_voices=custom_voices,
            output_filename=output_filename
        )
        
        # Return the audio file
        return send_file(
            output_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='podcast_custom.mp3'
        )
    
    except Exception as e:
        print(f"Error generating podcast from script: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/script/validate', methods=['POST'])
def validate_script():
    """
    Validate a podcast script
    
    Request body:
    {
        "script": "[HOST|excited] Welcome!\n[GUEST|calm] Thanks!"
    }
    
    Returns:
        JSON: Validation results and statistics
    """
    try:
        data = request.json
        script_text = data.get('script')
        
        if not script_text:
            return jsonify({
                'success': False,
                'error': 'Script is required'
            }), 400
        
        # Parse and validate
        segments = parse_podcast_script(script_text)
        
        if not segments:
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'No valid segments found. Use format: [SPEAKER|emotion] text'
            })
        
        # Get statistics
        stats = get_script_statistics(segments)
        
        return jsonify({
            'success': True,
            'valid': True,
            'statistics': stats,
            'segments': segments
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


async def preview_script():
    """
    Generate a script preview (first 30 seconds)
    
    Request body:
    {
        "script": "[HOST|excited] Welcome!\n[GUEST|calm] Thanks!"
    }
    
    Returns:
        Audio: Preview MP3 file
    """
    try:
        data = request.json
        script_text = data.get('script')
        
        if not script_text:
            return jsonify({
                'success': False,
                'error': 'Script is required'
            }), 400
        
        # Parse script and take first 2 segments for preview
        segments = parse_podcast_script(script_text)
        if not segments:
            return jsonify({
                'success': False,
                'error': 'Invalid script format'
            }), 400
        
        # Create preview script (first 2 segments only)
        preview_segments = segments[:2]
        from utils.script_parser import format_script_for_display
        preview_script = format_script_for_display(preview_segments)
        
        # Generate preview audio
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"preview_{timestamp}.mp3"
        
        output_path = await podcast_generator.generate_from_script(
            preview_script,
            output_filename=output_filename
        )
        
        return send_file(
            output_path,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='preview.mp3'
        )
    
    except Exception as e:
        print(f"Error generating preview: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'version': '1.0.0'
    })


# Async route wrapper
def async_route(f):
    """Wrapper to handle async routes in Flask"""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    wrapper.__name__ = f.__name__
    return wrapper


# Apply async wrapper to async routes
app.route('/api/voices', methods=['GET'])(async_route(get_voices))
app.route('/api/voice/demo/<voice_id>', methods=['GET'])(async_route(voice_demo))
app.route('/api/podcast/generate', methods=['POST'])(async_route(generate_podcast))
app.route('/api/podcast/from-script', methods=['POST'])(async_route(generate_from_script))
app.route('/api/script/preview', methods=['POST'])(async_route(preview_script))


if __name__ == '__main__':
    print("=" * 60)
    print("🎙️  Professional Podcast Generator")
    print("=" * 60)
    print("\n Starting Flask server...")
    print(f" Output directory: {OUTPUT_DIR}")
    print("\n Server running at: http://localhost:5000")
    print(" Press Ctrl+C to stop\n")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

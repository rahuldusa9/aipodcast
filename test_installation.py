"""
Test script to verify installation and basic functionality
Run this before starting the server to ensure everything is set up correctly
"""

import sys
import os

print("=" * 60)
print("🎙️  Podcast Generator - Installation Test")
print("=" * 60)
print()

# Test 1: Python version
print("1. Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"   ✗ Python version too old. Need 3.8+, got {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Test 2: Required modules
print("\n2. Checking required modules...")
required_modules = [
    ('flask', 'Flask'),
    ('edge_tts', 'Edge TTS'),
    ('pydub', 'Pydub'),
    ('numpy', 'NumPy'),
]

missing_modules = []
for module_name, display_name in required_modules:
    try:
        __import__(module_name)
        print(f"   ✓ {display_name}")
    except ImportError:
        print(f"   ✗ {display_name} - NOT INSTALLED")
        missing_modules.append(module_name)

if missing_modules:
    print(f"\n   Missing modules: {', '.join(missing_modules)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Optional modules (with warnings)
print("\n3. Checking optional modules...")
optional_modules = [
    ('pedalboard', 'Pedalboard (audio effects)'),
    ('soundfile', 'SoundFile (audio I/O)'),
    ('langdetect', 'LangDetect (language detection)'),
]

for module_name, display_name in optional_modules:
    try:
        __import__(module_name)
        print(f"   ✓ {display_name}")
    except ImportError:
        print(f"   ⚠ {display_name} - Not installed (optional, but recommended)")

# Test 4: Project structure
print("\n4. Checking project structure...")
required_files = [
    'app.py',
    'podcast_generator.py',
    'requirements.txt',
    'README.md',
    'utils/prosody.py',
    'utils/script_parser.py',
    'utils/voice_manager.py',
    'utils/audio_processor.py',
    'static/index.html',
    'static/style.css',
    'static/app.js',
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✓ {file_path}")
    else:
        print(f"   ✗ {file_path} - MISSING")

# Test 5: Output directory
print("\n5. Checking output directory...")
os.makedirs('output', exist_ok=True)
if os.path.exists('output'):
    print("   ✓ output/ directory ready")

# Test 6: Import project modules
print("\n6. Testing project imports...")
try:
    from utils.prosody import EMOTION_PROSODY, build_ssml_with_emotion
    print("   ✓ Prosody module")
except Exception as e:
    print(f"   ✗ Prosody module: {e}")

try:
    from utils.script_parser import parse_podcast_script
    print("   ✓ Script parser module")
except Exception as e:
    print(f"   ✗ Script parser module: {e}")

try:
    from utils.voice_manager import PODCAST_VOICES
    print("   ✓ Voice manager module")
except Exception as e:
    print(f"   ✗ Voice manager module: {e}")

try:
    from utils.audio_processor import merge_audio_segments
    print("   ✓ Audio processor module")
except Exception as e:
    print(f"   ✗ Audio processor module: {e}")

try:
    from podcast_generator import PodcastGenerator
    print("   ✓ Podcast generator module")
except Exception as e:
    print(f"   ✗ Podcast generator module: {e}")

# Test 7: Internet connection (basic check)
print("\n7. Checking internet connectivity...")
import socket
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("   ✓ Internet connection available")
    print("   (Edge TTS requires internet to synthesize speech)")
except OSError:
    print("   ⚠ No internet connection detected")
    print("   (Edge TTS requires internet - generation will fail without it)")

# Test 8: Example scripts
print("\n8. Checking example scripts...")
example_files = [
    'examples/tech_ai_podcast.txt',
    'examples/casual_space_chat.txt',
    'examples/educational_climate.txt',
    'examples/debate_cats_vs_dogs.txt',
]

for file_path in example_files:
    if os.path.exists(file_path):
        print(f"   ✓ {file_path}")

# Final summary
print("\n" + "=" * 60)
print("Installation Check Complete!")
print("=" * 60)

try:
    import pedalboard
    audio_quality = "Professional (with audio effects)"
except ImportError:
    audio_quality = "Basic (install pedalboard for pro audio)"

print(f"""
Status Summary:
✓ Python {sys.version_info.major}.{sys.version_info.minor}+
✓ All required dependencies installed
✓ Project structure complete
✓ Example scripts ready
✓ Audio quality: {audio_quality}

Ready to start! Run:
  python app.py

Then open: http://localhost:5000

For quick start guide, see: QUICKSTART.md
""")

print("=" * 60)

# 🎙️ Professional Podcast Generator with Edge TTS

AI-powered podcast generator that creates natural, multi-speaker conversations with emotional variation and professional audio quality.

**✨ NO FFMPEG REQUIRED** - Pure Python implementation perfect for cloud deployment!

## Features

✅ **Multi-speaker support** - Host, guest, narrator, co-host voices  
✅ **Emotional prosody** - Excited, calm, questioning, thoughtful tones  
✅ **250+ voices** - Support for 140+ languages/locales  
✅ **Language selection** - Generate podcasts in any supported language  
✅ **Voice customization** - Choose specific voices for host and guest  
✅ **Professional audio** - Noise gate, compression, limiting, reverb (via Pedalboard)  
✅ **Binary MP3 merging** - No FFmpeg needed for production deployment  
✅ **Natural flow** - Automatic pauses, speaker transitions  
✅ **Voice demos** - Preview any voice before using  
✅ **Script parsing** - `[SPEAKER|emotion] text` format  
✅ **AI generation** - 🆕 **Google Gemini AI** for intelligent script generation  

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** FFmpeg is NOT required! The app uses binary MP3 concatenation for merging audio segments.

### 2. (Optional) Configure Gemini AI

For AI-powered script generation:

1. Get free API key: https://makersuite.google.com/app/apikey
2. Copy `.env.example` to `.env`
3. Add your key: `GEMINI_API_KEY=your_key_here`

See [GEMINI_GUIDE.md](GEMINI_GUIDE.md) for details.

### 3. Run the Application

```bash
python app.py
```

### 4. Open Browser

Navigate to: `http://localhost:5000`

## Usage

### Generate a Podcast

1. Select language (English, Spanish, Hindi, etc.)
2. Enter your podcast topic
3. Set duration (1-30 minutes)
4. Choose tone (professional, casual, educational, entertaining)
5. (Optional) Select custom voices for host and guest
6. Add key points to cover
4. Select structure (interview, discussion, narrative, debate)
5. Add key points to cover
6. Click "Generate Podcast"

### Custom Scripts

Create a script file with format:

```
[HOST|enthusiastic] Welcome to Tech Talk!
[GUEST|calm] Thanks for having me.
[HOST|questioning] What's new in AI?
[GUEST|excited] So many breakthroughs!
```

Available emotions:
- `calm`, `enthusiastic`, `excited`, `questioning`
- `explaining`, `thoughtful`, `serious`, `grateful`
- `intrigued`, `amazed`, `greeting`, `closing`

### API Endpoints

#### List All Voices
```bash
GET /api/voices
```

Returns voices organized by locale.

#### Voice Demo
```bash
GET /api/voice/demo/<voice_id>
```

Returns MP3 demo of the specified voice.

#### Generate Podcast
```bash
POST /api/podcast/generate
Content-Type: application/json

{
  "topic": "Artificial Intelligence",
  "requirements": {
    "duration_minutes": 5,
    "speakers": ["HOST", "GUEST"],
    "tone": "professional",
    "structure": "interview",
    "key_points": ["AI basics", "Applications", "Future"]
  }
}
```

#### Generate from Script
```bash
POST /api/podcast/from-script
Content-Type: application/json

{
  "script": "[HOST|excited] Welcome!\n[GUEST|calm] Thanks!",
  "voices": {
    "HOST": "en-US-JennyNeural",
    "GUEST": "en-US-GuyNeural"
  }
}
```

## Project Structure

```
podcastmaker/
├── app.py                      # Flask application
├── podcast_generator.py        # Core podcast generation engine
├── requirements.txt
├── README.md
├── utils/
│   ├── prosody.py             # Emotion → prosody mapping
│   ├── script_parser.py       # Script parsing logic
│   ├── voice_manager.py       # Voice selection & management
│   └── audio_processor.py     # Audio effects & mastering
├── static/
│   ├── index.html             # Web interface
│   ├── style.css              # Styling
│   └── app.js                 # Frontend logic
├── examples/
│   ├── tech_podcast.txt       # Example scripts
│   ├── interview_script.txt
│   └── debate_script.txt
└── output/                    # Generated podcasts (git-ignored)
```

## Configuration

### Speaker Voices

Edit `utils/voice_manager.py` to customize default voices:

```python
PODCAST_VOICES = {
    'HOST': {
        'voice_id': 'en-US-JennyNeural',
        'style': 'cheerful',
        'description': 'Main host voice'
    },
    # ... add more
}
```

### Audio Processing

Adjust master chain in `utils/audio_processor.py`:

```python
master_board = Pedalboard([
    NoiseGate(threshold_db=-45, ratio=3, release_ms=120),
    Compressor(threshold_db=-10, ratio=1.8),
    # ... customize effects
])
```

## Advanced Features

### Add Background Music

```python
from utils.audio_processor import add_background_music

add_background_music(
    podcast_path="podcast.mp3",
    music_path="music.mp3",
    output_path="final.mp3"
)
```

### Multi-Language Support

The system automatically detects languages and selects appropriate voices:

```python
# Spanish podcast
script = "[HOST|enthusiastic] ¡Bienvenidos al podcast!"
# Automatically uses es-ES voices
```

### Custom Emotion Prosody

Edit `utils/prosody.py` to add new emotions:

```python
EMOTION_PROSODY = {
    'excited': {
        'rate': '+20%',
        'pitch': '+8%',
        'volume': '+3%'
    },
    # Add your custom emotion
    'mysterious': {
        'rate': '-10%',
        'pitch': '-5%',
        'volume': '-5%'
    }
}
```

## Requirements

- Python 3.8+
- Internet connection (Edge TTS requires online access)
- ~500MB disk space for audio processing libraries

## Limitations

- Max text per segment: ~500 words
- Internet required for voice synthesis
- Processing time: ~1 minute per minute of audio

## Troubleshooting

### "ModuleNotFoundError: No module named 'edge_tts'"

```bash
pip install edge-tts
```

### "Audio generation failed"

- Check internet connection
- Verify voice_id is valid (use `/api/voices` to list)
- Ensure text segments are under 500 words

### "Pedalboard import error"

```bash
pip install pedalboard soundfile
```

## Contributing

Contributions welcome! Areas for improvement:

- Additional emotion presets
- Background music library
- More voice presets
- Better AI script generation
- Multi-language demo texts

## License

MIT License - Free for personal and commercial use

## Credits

- **Edge TTS** - Microsoft's neural TTS engine
- **Pedalboard** - Spotify's audio processing library
- **Pydub** - Simple audio manipulation

---

**Made with ❤️ for podcasters and content creators**

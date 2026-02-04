# Quick Start Guide - Podcast Generator

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Verify installation:**
```bash
python -c "import edge_tts; print('Edge TTS installed!')"
```

3. **(Optional) Setup Gemini AI for intelligent scripts:**
```bash
# Copy the template
copy .env.example .env

# Edit .env and add your API key
# Get free key: https://makersuite.google.com/app/apikey
# GEMINI_API_KEY=your_key_here

# Test the API
python test_gemini.py
```

**Without Gemini:** System uses templates (still works great!)  
**With Gemini:** AI generates dynamic, topic-specific scripts

See [GEMINI_GUIDE.md](GEMINI_GUIDE.md) for full setup details.

## Running the Application

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## Using the Application

### Method 1: Generate from Topic (Easiest)

1. Go to "Generate Podcast" tab
2. Enter a topic (e.g., "Artificial Intelligence")
3. Set duration (1-30 minutes)
4. Choose tone (professional, casual, educational, entertaining)
5. Click "Generate Podcast"
6. Wait 1-3 minutes
7. Listen and download!

### Method 2: Custom Script (More Control)

1. Go to "Custom Script" tab
2. Write your script using format:
   ```
   [SPEAKER|emotion] Your text here
   ```
3. Click "Validate Script" to check it
4. Click "Generate Full Podcast"

### Method 3: Browse Voices First

1. Go to "Browse Voices" tab
2. Listen to different voices
3. Note voice IDs you like
4. Use them in custom scripts

## Script Format

```
[HOST|enthusiastic] Welcome to the show!
[GUEST|calm] Thanks for having me.
[HOST|questioning] What brings you here?
[GUEST|explaining] Well, it's an interesting story...
```

### Available Speakers:
- HOST
- GUEST
- CO-HOST
- NARRATOR
- EXPERT

### Available Emotions:
- calm, enthusiastic, excited
- questioning, explaining
- thoughtful, serious
- grateful, intrigued, amazed
- greeting, closing, warm
- optimistic, storytelling

## Example Scripts

Check the `examples/` folder for ready-to-use scripts:

- `tech_ai_podcast.txt` - Professional tech interview
- `casual_space_chat.txt` - Casual conversation
- `educational_climate.txt` - Educational lecture
- `debate_cats_vs_dogs.txt` - Fun debate

## API Endpoints

### Get All Voices
```bash
curl http://localhost:5000/api/voices
```

### Voice Demo
```bash
curl http://localhost:5000/api/voice/demo/en-US-AriaNeural -o demo.mp3
```

### Generate from Topic
```bash
curl -X POST http://localhost:5000/api/podcast/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"AI","requirements":{"duration_minutes":3,"tone":"casual"}}' \
  -o podcast.mp3
```

### Generate from Script
```bash
curl -X POST http://localhost:5000/api/podcast/from-script \
  -H "Content-Type: application/json" \
  -d '{"script":"[HOST|excited] Hello world!\n[GUEST|calm] Hi there!"}' \
  -o podcast.mp3
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "No audio generated"
- Check internet connection (Edge TTS requires online access)
- Verify script format is correct
- Try a shorter script first (< 2 minutes)

### "Port 5000 already in use"
Change port in app.py:
```python
app.run(host='0.0.0.0', port=8000, debug=True)
```

### Slow generation
- Normal: ~1 minute per minute of audio
- Longer scripts take more time
- Preview feature lets you test first 30s

## Tips for Best Results

✅ **DO:**
- Keep segments under 400 words
- Use varied emotions
- Add pauses between speakers
- Use descriptive speaker names
- Test with preview first

❌ **DON'T:**
- Use extreme prosody values
- Write very long monologues
- Mix too many voices
- Forget punctuation
- Skip validation

## Advanced Usage

### Custom Voice Assignment

```python
from podcast_generator import PodcastGenerator

generator = PodcastGenerator()

custom_voices = {
    'HOST': 'en-US-JennyNeural',
    'GUEST': 'en-GB-RyanNeural',
    'NARRATOR': 'en-AU-NatashaNeural'
}

await generator.generate_from_script(
    script_text,
    custom_voices=custom_voices
)
```

### Add Background Music

```python
from utils.audio_processor import add_background_music

add_background_music(
    podcast_path="podcast.mp3",
    music_path="music.mp3",
    output_path="final.mp3",
    music_volume_db=-20  # Quieter = lower number
)
```

### Process Existing Audio

```python
from utils.audio_processor import apply_master_processing

apply_master_processing(
    input_path="raw.mp3",
    output_path="mastered.mp3"
)
```

## System Requirements

- **Python**: 3.8 or higher
- **Internet**: Required for voice synthesis
- **Disk Space**: ~500MB for libraries
- **RAM**: 2GB minimum, 4GB recommended
- **OS**: Windows, macOS, or Linux

## Getting Help

- Check README.md for full documentation
- Review example scripts in examples/
- Test with validation endpoint first
- Start with short podcasts (2-3 minutes)

## What's Next?

1. Try the example scripts
2. Experiment with different emotions
3. Test various voices
4. Create your own podcast series!

---

**Happy Podcasting! 🎙️**

# 🤖 Google Gemini AI Integration Guide

## Overview

The podcast generator now uses **Google's Gemini AI** to create dynamic, intelligent podcast scripts instead of templates. This means your podcasts will be:

- ✅ **More natural** - AI understands context and creates flowing conversations
- ✅ **Topic-specific** - Content tailored to your exact subject
- ✅ **Engaging** - Varied emotions and natural dialogue
- ✅ **Intelligent** - Covers key points you specify

---

## Setup (3 Steps)

### Step 1: Get Your Free API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIzaSy...`)

### Step 2: Configure Your Environment

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
   
   Or on Linux/Mac:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz
   ```

### Step 3: Install the SDK

```bash
pip install -r requirements.txt
```

This installs `google-generativeai` package.

---

## How It Works

### Before (Template-Based)
```
Topic: "Artificial Intelligence"
↓
Generic template fills in {topic}
↓
Basic, predictable script
```

### After (Gemini AI)
```
Topic: "Artificial Intelligence"
Duration: 5 minutes
Tone: Professional
Key Points: ["Machine Learning", "Ethics", "Future"]
↓
Gemini AI generates intelligent script
↓
Natural, engaging, topic-specific podcast
```

---

## Usage Examples

### Example 1: Basic Generation

**Input:**
```json
{
  "topic": "Climate Change Solutions",
  "requirements": {
    "duration_minutes": 5,
    "tone": "educational"
  }
}
```

**What Gemini Creates:**
- Introduces climate change clearly
- Explains 3-5 practical solutions
- Uses HOST + GUEST format
- Natural questions and answers
- Appropriate emotional variation
- Proper closing

### Example 2: With Key Points

**Input:**
```json
{
  "topic": "Cryptocurrency",
  "requirements": {
    "duration_minutes": 7,
    "tone": "casual",
    "key_points": [
      "Bitcoin basics",
      "Blockchain technology",
      "Investment risks",
      "Future outlook"
    ]
  }
}
```

**What Gemini Creates:**
- Covers all 4 key points naturally
- Casual conversation style
- Appropriate depth for 7 minutes
- Engaging back-and-forth dialogue

### Example 3: Different Tones

**Professional:**
```
[HOST|greeting] Welcome to Tech Insights. Today's topic: Quantum Computing.
[GUEST|calm] Thank you. I'm Dr. Sarah Chen, quantum physicist at MIT.
[HOST|questioning] Let's begin with the fundamentals...
```

**Casual:**
```
[HOST|enthusiastic] Hey everyone! Today we're talking about quantum computers!
[CO-HOST|excited] Dude, this stuff is mind-blowing!
[HOST|questioning] So what even IS quantum computing?
```

**Educational:**
```
[NARRATOR|calm] Welcome to Science Explained. Today: Quantum Computing.
[NARRATOR|explaining] To understand quantum computers, we must first...
```

**Entertaining:**
```
[HOST|excited] Alright, buckle up! We're diving into quantum computers!
[GUEST|amazed] This is going to blow your mind!
```

---

## API Call Details

### What Gemini Receives

The system sends Gemini a structured prompt:

```
Generate a podcast script about: [YOUR TOPIC]

Requirements:
- Style: [professional/casual/educational/entertaining]
- Target length: approximately [WORDS] words
- Format: Use [SPEAKER|emotion] before each line
- Cover these key points: [YOUR KEY POINTS]

Available speakers: HOST, GUEST, CO-HOST, NARRATOR
Available emotions: enthusiastic, calm, questioning, explaining...
```

### What Gemini Returns

A complete podcast script in the correct format:

```
[HOST|enthusiastic] Welcome to our podcast!
[GUEST|calm] Thanks for having me.
[HOST|questioning] Let's explore [topic]...
[GUEST|explaining] Great question! [Detailed answer]
...
[HOST|closing] That's all for today!
```

### Fallback Behavior

If Gemini API fails or key is missing:
- ✅ System automatically falls back to template generation
- ✅ Warning shown in console
- ✅ Podcast still generates successfully
- ℹ️ Templates are less dynamic but always work offline

---

## Testing

### Test Your Setup

```bash
python demo.py
```

If Gemini is configured:
```
✓ Using Gemini AI for script generation
✓ Generated script with Gemini AI (1847 characters)
```

If not configured:
```
Warning: GEMINI_API_KEY not found, using template generation
✓ Using template generation
```

### Test via Web UI

1. Start server: `python app.py`
2. Open: http://localhost:5000
3. Enter topic: "Space Exploration"
4. Click "Generate Podcast"
5. Check console output:
   ```
   Generating script for topic: Space Exploration
   ✓ Generated script with Gemini AI (2134 characters)
   🎙️ Starting podcast generation...
   ```

### Test via API

```bash
curl -X POST http://localhost:5000/api/podcast/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning",
    "requirements": {
      "duration_minutes": 3,
      "tone": "casual",
      "key_points": ["Neural networks", "Real world uses"]
    }
  }' \
  --output ml_podcast.mp3
```

---

## Comparison: Template vs Gemini

### Template Generation
**Pros:**
- ✅ Works offline
- ✅ No API key needed
- ✅ Always available
- ✅ Predictable format

**Cons:**
- ❌ Generic content
- ❌ Limited variation
- ❌ Doesn't adapt to topic
- ❌ Feels templated

### Gemini AI Generation
**Pros:**
- ✅ Intelligent, natural content
- ✅ Topic-specific details
- ✅ Covers key points precisely
- ✅ Varied and engaging
- ✅ Contextually aware

**Cons:**
- ❌ Requires internet
- ❌ Needs API key
- ❌ Small latency (1-3 seconds)
- ❌ Rate limits apply

---

## Best Practices

### 1. Be Specific with Topics
❌ Bad: "Technology"
✅ Good: "How Blockchain Technology Works"

### 2. Use Key Points
```json
{
  "topic": "Healthy Eating",
  "key_points": [
    "Macronutrients basics",
    "Meal planning tips",
    "Common mistakes",
    "Budget-friendly options"
  ]
}
```

### 3. Choose Appropriate Duration
- 2-3 minutes: Quick topic overview
- 5-7 minutes: Detailed discussion
- 10+ minutes: In-depth exploration

### 4. Match Tone to Topic
- **Professional**: Business, science, academic
- **Casual**: Entertainment, lifestyle, hobbies
- **Educational**: Learning content, tutorials
- **Entertaining**: Debates, fun topics, pop culture

---

## Troubleshooting

### "GEMINI_API_KEY not found"

**Solution:**
1. Create `.env` file in project root
2. Add: `GEMINI_API_KEY=your_key_here`
3. Restart server

### "Gemini API error: 429"

**Issue:** Rate limit exceeded

**Solutions:**
- Wait a few seconds and retry
- Reduce frequency of requests
- Check quota at: https://makersuite.google.com

### "Invalid API key"

**Solution:**
- Verify key is correct
- Check for extra spaces in `.env`
- Regenerate key if needed

### "Script missing format"

**Rare Issue:** Gemini returns unformatted text

**Automatic Fix:** System adds `[HOST|enthusiastic]` wrapper

**Manual Fix:** Add speaker tags manually in custom script mode

---

## API Limits & Costs

### Free Tier (Gemini API)
- ✅ **60 requests per minute**
- ✅ **Free up to 1 million tokens/month**
- ✅ Perfect for personal use
- ✅ No credit card required

### Script Generation Costs
- **Typical script**: ~500-1000 tokens
- **Monthly limit**: ~1,000-2,000 podcasts
- **Cost**: **FREE** for most users

---

## Advanced Usage

### Custom Prompt Engineering

Edit `podcast_generator.py` to customize the Gemini prompt:

```python
def _generate_with_gemini(self, topic, duration_minutes, tone, key_points=None):
    # Customize this prompt for your needs
    prompt = f"""Generate a podcast script about: {topic}
    
    Special instructions:
    - Add humor where appropriate
    - Include 2-3 real-world examples
    - End with actionable takeaways
    
    [Rest of prompt...]
    """
```

### Multiple Model Support

The code uses `gemini-pro` by default. You can change this:

```python
# In _generate_with_gemini method
model = genai.GenerativeModel('gemini-pro')  # Default

# Or use other models:
# model = genai.GenerativeModel('gemini-ultra')  # More powerful
# model = genai.GenerativeModel('gemini-nano')   # Faster
```

---

## Examples of Generated Scripts

### Topic: "Coffee Culture Around the World"
**Tone:** Casual, **Duration:** 5 min

```
[HOST|enthusiastic] Hey coffee lovers! Welcome back to the show!
[CO-HOST|excited] Today we're taking a caffeinated journey around the world!
[HOST|questioning] So where should we start? Italy?
[CO-HOST|storytelling] Oh man, Italian coffee culture is intense! 
Picture this: You walk into a bar in Rome at 7am...
[HOST|intrigued] Tell me more!
[CO-HOST|explaining] Italians drink espresso standing at the bar. 
It's quick, strong, and never after 11am...
```

### Topic: "Introduction to Python Programming"
**Tone:** Educational, **Duration:** 7 min

```
[NARRATOR|calm] Welcome to Code Academy. Today: Introduction to Python.
[NARRATOR|explaining] Python is a high-level programming language 
known for its simplicity and readability.
[NARRATOR|questioning] Why is Python so popular?
[NARRATOR|explaining] First, its syntax is clean and intuitive...
```

---

## Summary

🎯 **What You Get:**
- Intelligent, topic-specific scripts
- Natural conversation flow
- Key points coverage
- Multiple tone options
- Automatic fallback to templates

🚀 **Setup Time:** 2 minutes
💰 **Cost:** Free (generous limits)
🌐 **Requirements:** Internet + API key

**Ready to create AI-powered podcasts!** 🎙️✨

For more help, see:
- `.env.example` - Configuration template
- `README.md` - Full documentation
- Google AI Studio: https://makersuite.google.com

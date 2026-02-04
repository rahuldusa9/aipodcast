"""
Quick Demo - Generate a podcast in 3 lines of code!
Run this after installing dependencies to see the system in action.
"""

import asyncio
import os
from podcast_generator import PodcastGenerator

# Simple demo script
demo_script = """
[HOST|enthusiastic] Welcome to our podcast! Today we're testing the AI podcast generator.

[GUEST|calm] Thanks for having me. This technology is really impressive.

[HOST|questioning] How does it work?

[GUEST|explaining] It uses Microsoft Edge TTS to synthesize natural-sounding speech with different emotions and speakers.

[HOST|excited] And it applies professional audio processing too!

[GUEST|optimistic] Exactly. Noise reduction, compression, reverb - everything you need for broadcast quality.

[HOST|grateful] Amazing! Thanks for the demo.

[GUEST|warm] My pleasure!

[HOST|closing] That's our quick demo. Subscribe for more!
"""

async def main():
    print("🎙️  Quick Demo - Generating podcast...")
    print("=" * 60)
    
    # Check Gemini configuration
    if os.getenv('GEMINI_API_KEY'):
        print("✓ Gemini AI configured - AI script generation available")
    else:
        print("ℹ️  Gemini AI not configured - Using templates")
        print("   Get free API key: https://makersuite.google.com/app/apikey")
        print("   See GEMINI_GUIDE.md for setup")
    
    print()
    
    # Create generator
    generator = PodcastGenerator()
    
    # Generate podcast
    output = await generator.generate_from_script(
        demo_script,
        output_filename="demo_podcast.mp3"
    )
    
    print("\n" + "=" * 60)
    print(f"✅ Demo complete! Your podcast is ready:")
    print(f"   {output}")
    print("\nListen to it and hear the multi-speaker conversation")
    print("with emotional variation and professional audio quality!")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())

"""
Podcast Generator Engine
Core logic for generating multi-speaker podcasts with Edge TTS
"""

import os
import asyncio
import edge_tts
import tempfile
from datetime import datetime
# pydub removed - no ffmpeg dependency
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.script_parser import parse_podcast_script, validate_script, split_long_segment
from utils.voice_manager import assign_voices_to_script, PODCAST_VOICES
from utils.prosody import build_ssml_with_emotion, get_prosody_for_emotion
from utils.audio_processor import (
    apply_audio_effects,
    apply_master_processing,
    merge_audio_segments,
    create_silence,
    get_audio_duration
)


class PodcastGenerator:
    """Professional podcast generator with Edge TTS"""
    
    def __init__(self, output_dir='output'):
        """
        Initialize podcast generator
        
        Args:
            output_dir (str): Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.temp_files = []
    
    async def generate_from_script(self, script_text, custom_voices=None, 
                                   output_filename=None, add_pauses=True, language='en-US'):
        """
        Generate podcast from script text
        
        Args:
            script_text (str): Podcast script in [SPEAKER|emotion] format
            custom_voices (dict): Optional custom voice mapping
            output_filename (str): Output filename (auto-generated if None)
            add_pauses (bool): Add pauses between speakers
            language (str): Language code for voice selection
            
        Returns:
            str: Path to generated podcast file
        """
        print("🎙️ Starting podcast generation...")
        
        # 1. Parse script
        print("📝 Parsing script...")
        segments = parse_podcast_script(script_text)
        
        if not segments:
            raise ValueError("No valid segments found in script")
        
        # Validate script
        is_valid, error_msg = validate_script(segments)
        if not is_valid:
            raise ValueError(f"Script validation failed: {error_msg}")
        
        print(f"   Found {len(segments)} segments")
        
        # 2. Assign voices
        print("🎤 Assigning voices...")
        segments = assign_voices_to_script(segments, custom_voices, language)
        
        # 3. Generate audio for each segment
        print("🔊 Generating audio segments...")
        segment_files = await self._generate_segments(segments, add_pauses)
        
        # 4. Merge segments
        print("🔗 Merging segments...")
        merged_path = tempfile.NamedTemporaryFile(
            delete=False, suffix='_merged.mp3', dir=self.output_dir
        ).name
        self.temp_files.append(merged_path)
        
        merge_audio_segments(segment_files, merged_path, crossfade_ms=50)
        
        # 5. Apply master processing
        print("✨ Applying master processing...")
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"podcast_{timestamp}.mp3"
        
        output_path = os.path.join(self.output_dir, output_filename)
        apply_master_processing(merged_path, output_path)
        
        # 6. Cleanup temp files
        self._cleanup_temp_files()
        
        duration = get_audio_duration(output_path)
        print(f"✅ Podcast generated successfully!")
        print(f"   Output: {output_path}")
        print(f"   Duration: {duration:.1f} seconds")
        
        return output_path
    
    async def _generate_segments(self, segments, add_pauses=True):
        """
        Generate audio for all segments
        
        Args:
            segments (list): Parsed segments with voice assignments
            add_pauses (bool): Add pauses between different speakers
            
        Returns:
            list: List of generated audio file paths
        """
        segment_files = []
        
        for i, segment in enumerate(segments):
            print(f"   Segment {i+1}/{len(segments)}: {segment['speaker']} ({segment['emotion']})")
            
            # Split long segments if needed
            split_segments = split_long_segment(segment, max_words=400)
            
            for sub_segment in split_segments:
                # Generate audio for segment
                audio_file = await self._generate_single_segment(
                    sub_segment['text'],
                    sub_segment['emotion'],
                    sub_segment['voice_id'],
                    segment_num=i
                )
                
                segment_files.append(audio_file)
            
            # Add pause between different speakers (skip if ffmpeg not available)
            if add_pauses and i < len(segments) - 1:
                next_speaker = segments[i + 1]['speaker']
                if next_speaker != segment['speaker']:
                    try:
                        # Different speaker = add 300ms pause
                        pause_file = tempfile.NamedTemporaryFile(
                            delete=False, suffix=f'_pause_{i}.mp3', dir=self.output_dir
                        ).name
                        self.temp_files.append(pause_file)
                        
                        pause_result = create_silence(300, pause_file)
                        if pause_result:  # Only add if creation succeeded
                            segment_files.append(pause_result)
                    except Exception as e:
                        print(f"Warning: Skipping pause due to: {e}")
        
        return segment_files
    
    async def _generate_single_segment(self, text, emotion, voice_id, segment_num=0):
        """
        Generate audio for a single segment
        
        Args:
            text (str): Text to speak
            emotion (str): Emotion to apply
            voice_id (str): Edge TTS voice ID
            segment_num (int): Segment number for filename
            
        Returns:
            str: Path to generated audio file
        """
        try:
            # Clean text to remove any metadata or technical terms
            original_text = text
            text = self._clean_text_for_speech(text)
            
            # Validate text is not empty after cleaning
            if not text or len(text.strip()) == 0:
                print(f"      Warning: Text empty after cleaning. Using original.")
                print(f"      Original: {original_text[:100]}")
                text = original_text
            
            print(f"      Generating audio for: {text[:50]}...")
            print(f"      Voice ID: {voice_id}")
            
            # Generate audio with Edge TTS (plain text - SSML can cause hanging)
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=f'_seg_{segment_num}.mp3', dir=self.output_dir
            ).name
            self.temp_files.append(temp_file)
            
            # Use plain text instead of SSML to avoid hanging issues
            communicate = edge_tts.Communicate(text, voice_id)
            
            # Add timeout protection
            import asyncio
            try:
                await asyncio.wait_for(communicate.save(temp_file), timeout=30.0)
            except asyncio.TimeoutError:
                print(f"      Timeout on segment {segment_num}, retrying...")
                # Retry once with a new communicate object
                communicate = edge_tts.Communicate(text, voice_id)
                await asyncio.wait_for(communicate.save(temp_file), timeout=30.0)
            
            print(f"      ✓ Audio saved to {os.path.basename(temp_file)}")
            
            # Skip audio effects (can cause hanging)
            # apply_audio_effects(temp_file, emotion)
            
            return temp_file
        except Exception as e:
            print(f"Error generating segment {segment_num}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _clean_text_for_speech(self, text):
        """
        Clean text to remove technical metadata and ensure natural speech
        
        Args:
            text (str): Raw text from script
            
        Returns:
            str: Cleaned text ready for TTS
        """
        import re
        
        # Remove markdown formatting (bold, italic, etc.)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)       # *italic*
        text = re.sub(r'__([^_]+)__', r'\1', text)       # __bold__
        text = re.sub(r'_([^_]+)_', r'\1', text)         # _italic_
        text = re.sub(r'~~([^~]+)~~', r'\1', text)       # ~~strikethrough~~
        
        # Remove XML/SSML tags completely (including their content)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove XML attributes and namespaces
        text = re.sub(r'xmlns[:\w]*\s*=\s*["\'][^"\']*["\']', '', text)
        
        # Remove any remaining speaker tags if present
        text = re.sub(r'\[([A-Z\-]+)\|(\w+)\]\s*', '', text)
        
        # Remove technical terms that might have leaked in
        technical_patterns = [
            r'xmlns[\w\s:="\'/.]*',
            r'voice\s+model[:\s]+[\w\-]+',
            r'prosody\s+rate[:\s]+[\+\-]?\d+%',
            r'prosody[:\s]+[\+\-]?\d+%',
            r'pitch[:\s]+[\+\-]?\d+%',
            r'volume[:\s]+[\+\-]?\d+dB',
            r'with\s+prosody\s+',
            r'using\s+voice\s+',
            r'rate\s+of\s+[\+\-]?\d+%',
            r'voice\s+name[:\s]+[\w\-]+',
            r'speak\s+version[:\s]+[\d\.]+',
        ]
        
        for pattern in technical_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        cleaned = text.strip()
        
        # If cleaning removed everything, return some fallback
        if not cleaned or len(cleaned) < 5:
            print(f"Warning: Text too short after cleaning: '{cleaned}'")
            return "Hello."  # Safe fallback
        
        return cleaned
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not delete temp file {temp_file}: {e}")
        
        self.temp_files = []
    
    def generate_template_script(self, topic, duration_minutes=5, tone='professional', key_points=None, language='en-US'):
        """
        Generate a podcast script using Google Gemini AI
        
        Args:
            topic (str): Podcast topic
            duration_minutes (int): Target duration
            tone (str): Tone (professional, casual, educational, entertaining)
            key_points (list): Optional list of key points to cover
            language (str): Target language code (e.g., 'en-US', 'es-ES', 'hi-IN')
            
        Returns:
            str: Generated script text
        """
        # Try to use Gemini API first
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if gemini_api_key:
            try:
                return self._generate_with_gemini(topic, duration_minutes, tone, key_points, language)
            except Exception as e:
                print(f"Warning: Gemini API failed ({e}), falling back to template")
        else:
            print("Warning: GEMINI_API_KEY not found, using template generation")
        
        # Fallback to template generation
        target_words = duration_minutes * 150
        
        if tone == 'professional':
            script = self._generate_professional_script(topic, target_words)
        elif tone == 'casual':
            script = self._generate_casual_script(topic, target_words)
        elif tone == 'educational':
            script = self._generate_educational_script(topic, target_words)
        else:  # entertaining
            script = self._generate_entertaining_script(topic, target_words)
        
        return script
    
    def _generate_with_gemini(self, topic, duration_minutes, tone, key_points=None, language='en-US'):
        """
        Generate podcast script using Google Gemini API
        
        Args:
            topic (str): Podcast topic
            duration_minutes (int): Target duration
            tone (str): Podcast tone
            key_points (list): Optional key points to cover
            language (str): Target language code
            
        Returns:
            str: Generated podcast script
        """
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        # Estimate words needed (150 words per minute)
        target_words = duration_minutes * 150
        
        # Build key points section
        key_points_text = ""
        if key_points and len(key_points) > 0:
            key_points_text = f"\n- Cover these key points: {', '.join(key_points)}"
        
        # Language instruction
        language_names = {
            'en-US': 'English',
            'es-ES': 'Spanish',
            'fr-FR': 'French',
            'de-DE': 'German',
            'it-IT': 'Italian',
            'pt-BR': 'Portuguese',
            'hi-IN': 'Hindi',
            'zh-CN': 'Chinese',
            'ja-JP': 'Japanese',
            'ko-KR': 'Korean',
            'ar-SA': 'Arabic',
            'ru-RU': 'Russian',
            'ta-IN': 'Tamil',
            'te-IN': 'Telugu',
            'ml-IN': 'Malayalam',
            'bn-IN': 'Bengali'
        }
        language_name = language_names.get(language, 'English')
        language_instruction = f"\n- Generate the script in {language_name} language" if language != 'en-US' else ""
        
        # Create prompt based on tone
        tone_instructions = {
            'professional': 'professional interview style with expert analysis',
            'casual': 'casual, friendly conversation between friends',
            'educational': 'educational lecture format with clear explanations',
            'entertaining': 'entertaining and engaging debate or discussion'
        }
        
        tone_style = tone_instructions.get(tone, 'conversational')
        
        prompt = f"""Generate a podcast script about: {topic}

Requirements:
- Style: {tone_style}
- Target length: approximately {target_words} words (for {duration_minutes} minutes at 150 words/minute)
- Format: Use [SPEAKER|emotion] before each line{key_points_text}{language_instruction}

Available speakers: HOST, GUEST, CO-HOST, NARRATOR
Available emotions: enthusiastic, calm, questioning, explaining, excited, thoughtful, serious, grateful, intrigued, amazed, greeting, closing, warm, optimistic, storytelling

Format example:
[HOST|enthusiastic] Welcome to our podcast! Today we're exploring {topic}.
[GUEST|calm] Thanks for having me. I'm excited to discuss this topic.
[HOST|questioning] Let's start with the basics...

CRITICAL INSTRUCTIONS:
- ONLY generate the dialogue text after each [SPEAKER|emotion] tag
- DO NOT include any technical information, voice model names, or prosody details in the dialogue
- DO NOT say things like "using voice model" or "with prosody rate"
- DO NOT use markdown formatting (no **bold**, *italic*, or other markdown)
- Write plain text only - no asterisks, underscores, or special formatting
- The dialogue should be natural conversation that people would actually say
- Keep it conversational and engaging
- Use varied emotions throughout
- Include engaging questions and answers
- End with a proper closing
- Keep segments under 400 words each

Generate ONLY the podcast dialogue script now (no explanations, no metadata, just the script):"""

        try:
            # Use Gemini to generate content
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            script = response.text
            
            # Ensure script has proper format
            if '[' not in script or '|' not in script:
                print("Warning: Gemini response missing script format, adding structure")
                script = f"[HOST|enthusiastic] {script}"
            
            print(f"✓ Generated script with Gemini AI ({len(script)} characters)")
            return script
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _generate_professional_script(self, topic, target_words):
        """Generate professional interview-style script"""
        script = f"""[HOST|greeting] Welcome to our podcast. Today, we're exploring {topic}.

[HOST|calm] I'm joined by our expert guest to discuss this fascinating subject.

[GUEST|greeting] Thank you for having me. I'm excited to share insights about {topic}.

[HOST|questioning] Let's start with the fundamentals. What exactly is {topic}?

[GUEST|explaining] {topic} is a complex and evolving field that encompasses multiple dimensions. At its core, it represents a significant area of innovation and development.

[HOST|intrigued] That's a great foundation. Can you provide a concrete example?

[GUEST|storytelling] Absolutely. Consider how {topic} impacts our daily lives through various applications and use cases.

[HOST|thoughtful] I see. What are the key challenges or considerations people should be aware of?

[GUEST|serious] There are several important factors. First, we need to consider the technical aspects. Second, the practical implications. And third, the broader societal impact.

[HOST|questioning] What does the future hold for {topic}?

[GUEST|optimistic] The future is incredibly promising. We're seeing rapid advancement and innovation across multiple fronts.

[HOST|grateful] This has been incredibly insightful. Thank you for sharing your expertise.

[GUEST|warm] My pleasure. Thank you for the thoughtful discussion.

[HOST|closing] That's all for today. Join us next time for more fascinating conversations."""
        
        return script
    
    def _generate_casual_script(self, topic, target_words):
        """Generate casual conversation-style script"""
        script = f"""[HOST|enthusiastic] Hey everyone! Welcome back to the show. Today we're talking about {topic}.

[CO-HOST|excited] Oh man, I've been looking forward to this one!

[HOST|questioning] So what got you interested in {topic}?

[CO-HOST|storytelling] Funny story actually. I stumbled upon it while...

[HOST|intrigued] No way! That's amazing.

[CO-HOST|explaining] Right? So basically, {topic} is all about...

[HOST|amazed] Wow, I had no idea it was that deep.

[CO-HOST|calm] Yeah, there's a lot more to it than people think.

[HOST|questioning] What's the coolest thing about {topic}?

[CO-HOST|excited] Oh, definitely how it connects to everyday life!

[HOST|grateful] Thanks for breaking that down! Super helpful.

[CO-HOST|warm] Anytime! This was fun.

[HOST|closing] Alright folks, that's it for today. Catch you next time!"""
        
        return script
    
    def _generate_educational_script(self, topic, target_words):
        """Generate educational lecture-style script"""
        script = f"""[NARRATOR|calm] Welcome to our educational series. Today's topic: {topic}.

[NARRATOR|explaining] To understand {topic}, we must first establish the foundational concepts.

[NARRATOR|thoughtful] Let's begin with a definition. {topic} refers to...

[NARRATOR|explaining] Now, consider the key components. First, we have... Second, there's... And third...

[NARRATOR|storytelling] To illustrate this with a real-world example...

[NARRATOR|serious] It's important to note the implications and limitations.

[NARRATOR|optimistic] However, the potential applications are extensive.

[NARRATOR|explaining] In summary, {topic} represents a significant area of study with far-reaching consequences.

[NARRATOR|closing] Thank you for learning with us today. Until next time."""
        
        return script
    
    def _generate_entertaining_script(self, topic, target_words):
        """Generate entertaining, engaging script"""
        script = f"""[HOST|excited] Alright, buckle up folks! Today we're diving into the wild world of {topic}!

[HOST|storytelling] Picture this: You're sitting there, minding your own business, when suddenly...

[GUEST|amazed] Wait, seriously? That's crazy!

[HOST|enthusiastic] I know, right? But here's where it gets even better.

[GUEST|intrigued] Tell me more!

[HOST|explaining] So {topic} is basically like... imagine if X met Y at a party.

[GUEST|excited] Ha! That's the perfect analogy.

[HOST|questioning] But seriously, what makes {topic} so special?

[GUEST|thoughtful] Well, beyond the entertainment value, there's actually some deep stuff here.

[HOST|amazed] Whoa, mind blown.

[GUEST|warm] That's what makes it so fascinating.

[HOST|grateful] This was awesome! Thanks for the chat.

[GUEST|enthusiastic] Anytime! This was a blast.

[HOST|closing] And that's a wrap! See you next time, folks!"""
        
        return script


async def generate_podcast(script_text, output_path=None, custom_voices=None):
    """
    Convenience function to generate podcast
    
    Args:
        script_text (str): Podcast script
        output_path (str): Output file path
        custom_voices (dict): Custom voice mapping
        
    Returns:
        str: Path to generated podcast
    """
    generator = PodcastGenerator()
    return await generator.generate_from_script(
        script_text,
        custom_voices=custom_voices,
        output_filename=output_path
    )


if __name__ == '__main__':
    # Test podcast generator
    test_script = """
[HOST|enthusiastic] Welcome to Tech Talk! I'm your host, Sarah.

[GUEST|greeting] And I'm Dr. James Chen, AI researcher.

[HOST|questioning] James, what's the most exciting development in AI?

[GUEST|excited] The emergence of multimodal AI systems! They can understand text, images, and audio together.

[HOST|intrigued] That sounds incredible. Can you give us an example?

[GUEST|explaining] Think about GPT-4 Vision. You can show it a photo and ask questions about what's in the image.

[HOST|amazed] Wow! What does this mean for the future?

[GUEST|optimistic] We're moving toward AI that understands the world more like humans do.

[HOST|grateful] Fascinating insights! Thanks for joining us, James.

[GUEST|warm] My pleasure, Sarah!

[HOST|closing] That's all for today! Don't forget to subscribe!
"""
    
    print("Testing Podcast Generator")
    print("=" * 60)
    
    async def test():
        generator = PodcastGenerator()
        output = await generator.generate_from_script(test_script, output_filename="test_podcast.mp3")
        print(f"\n✅ Test complete! Generated: {output}")
    
    asyncio.run(test())

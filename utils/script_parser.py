"""
Script Parser for Podcast Generation
Parses scripts in format: [SPEAKER|emotion] Text
"""

import re


def parse_podcast_script(script_text):
    """
    Parse podcast script with speaker labels and emotions
    
    Format: [SPEAKER|emotion] Text
    Example: [HOST|excited] Welcome to the show!
    
    Args:
        script_text (str): Raw script text
        
    Returns:
        list: List of segment dictionaries with speaker, emotion, text
    """
    segments = []
    
    # Regex pattern: [SPEAKER|emotion] Text
    # Captures until next [SPEAKER| or end of string
    pattern = r'\[([A-Z\-]+)\|(\w+)\]\s*(.+?)(?=\n\[|$)'
    
    matches = re.finditer(pattern, script_text, re.DOTALL)
    
    for match in matches:
        speaker = match.group(1).strip()  # HOST, GUEST, CO-HOST, etc.
        emotion = match.group(2).strip()  # excited, calm, etc.
        text = match.group(3).strip()     # The actual dialogue
        
        # Skip empty segments
        if not text:
            continue
        
        segments.append({
            'speaker': speaker,
            'emotion': emotion,
            'text': text
        })
    
    return segments


def validate_script(segments):
    """
    Validate parsed script segments
    
    Args:
        segments (list): Parsed segments
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not segments:
        return False, "Script is empty or invalid format"
    
    # Check for extremely long segments (>500 words)
    for i, segment in enumerate(segments):
        word_count = len(segment['text'].split())
        if word_count > 500:
            return False, f"Segment {i+1} ({segment['speaker']}) is too long ({word_count} words). Max 500 words per segment."
    
    # Check for valid speakers
    valid_speakers = ['HOST', 'GUEST', 'CO-HOST', 'NARRATOR', 'EXPERT']
    for i, segment in enumerate(segments):
        if segment['speaker'] not in valid_speakers:
            # Warning, but not error
            pass
    
    return True, None


def format_script_for_display(segments):
    """
    Format segments back into readable script
    
    Args:
        segments (list): Parsed segments
        
    Returns:
        str: Formatted script text
    """
    lines = []
    for segment in segments:
        lines.append(f"[{segment['speaker']}|{segment['emotion']}] {segment['text']}")
    
    return "\n\n".join(lines)


def split_long_segment(segment, max_words=400):
    """
    Split a segment that's too long into smaller chunks
    
    Args:
        segment (dict): Segment with text, speaker, emotion
        max_words (int): Maximum words per chunk
        
    Returns:
        list: List of smaller segments
    """
    words = segment['text'].split()
    
    if len(words) <= max_words:
        return [segment]
    
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        
        # Check if we've hit a sentence boundary near max_words
        if len(current_chunk) >= max_words and word.endswith(('.', '!', '?')):
            chunks.append({
                'speaker': segment['speaker'],
                'emotion': segment['emotion'],
                'text': ' '.join(current_chunk)
            })
            current_chunk = []
    
    # Add remaining words
    if current_chunk:
        chunks.append({
            'speaker': segment['speaker'],
            'emotion': segment['emotion'],
            'text': ' '.join(current_chunk)
        })
    
    return chunks


def estimate_duration(segments, words_per_minute=150):
    """
    Estimate podcast duration from segments
    
    Args:
        segments (list): Parsed segments
        words_per_minute (int): Average speaking rate
        
    Returns:
        float: Estimated duration in minutes
    """
    total_words = sum(len(segment['text'].split()) for segment in segments)
    
    # Add time for pauses between speakers (0.3s per transition)
    num_transitions = len(segments) - 1
    pause_time_minutes = (num_transitions * 0.3) / 60
    
    speech_time_minutes = total_words / words_per_minute
    
    return speech_time_minutes + pause_time_minutes


def get_script_statistics(segments):
    """
    Get statistics about the script
    
    Args:
        segments (list): Parsed segments
        
    Returns:
        dict: Statistics dictionary
    """
    total_words = sum(len(segment['text'].split()) for segment in segments)
    
    # Count by speaker
    speaker_stats = {}
    for segment in segments:
        speaker = segment['speaker']
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                'segments': 0,
                'words': 0
            }
        speaker_stats[speaker]['segments'] += 1
        speaker_stats[speaker]['words'] += len(segment['text'].split())
    
    # Count emotions
    emotion_stats = {}
    for segment in segments:
        emotion = segment['emotion']
        emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1
    
    return {
        'total_segments': len(segments),
        'total_words': total_words,
        'estimated_duration_minutes': estimate_duration(segments),
        'speakers': speaker_stats,
        'emotions': emotion_stats
    }


if __name__ == '__main__':
    # Test script parser
    test_script = """
[HOST|enthusiastic] Welcome to Tech Talk Daily! I'm your host, Sarah.

[GUEST|calm] And I'm Dr. James Chen, AI researcher at MIT.

[HOST|questioning] James, what's the biggest misconception about AI?

[GUEST|thoughtful] People think AI will replace humans entirely. But really, it's about augmentation.

[HOST|excited] That's fascinating! Tell us more about augmentation.

[GUEST|explaining] Well, think of AI as a super-powered tool that enhances human capabilities rather than replacing them.
"""
    
    print("Parsing test script...")
    segments = parse_podcast_script(test_script)
    
    print(f"\nParsed {len(segments)} segments:\n")
    
    for i, segment in enumerate(segments, 1):
        print(f"{i}. [{segment['speaker']}|{segment['emotion']}]")
        print(f"   {segment['text'][:60]}...")
    
    print("\n" + "="*60)
    print("Script Statistics:")
    stats = get_script_statistics(segments)
    print(f"Total segments: {stats['total_segments']}")
    print(f"Total words: {stats['total_words']}")
    print(f"Estimated duration: {stats['estimated_duration_minutes']:.1f} minutes")
    print(f"\nSpeakers:")
    for speaker, data in stats['speakers'].items():
        print(f"  {speaker}: {data['segments']} segments, {data['words']} words")
    print(f"\nEmotions used:")
    for emotion, count in stats['emotions'].items():
        print(f"  {emotion}: {count}x")

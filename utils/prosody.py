"""
Prosody Management for Emotional Speech
Maps emotions to SSML prosody parameters (rate, pitch, volume)
"""

EMOTION_PROSODY = {
    'calm': {
        'rate': '+0%',
        'pitch': '+0%',
        'volume': '+0dB',
        'description': 'Neutral, measured speech'
    },
    'enthusiastic': {
        'rate': '+15%',
        'pitch': '+5%',
        'volume': '+2dB',
        'description': 'Energetic and upbeat'
    },
    'excited': {
        'rate': '+20%',
        'pitch': '+8%',
        'volume': '+3dB',
        'description': 'Very energetic, high enthusiasm'
    },
    'sad': {
        'rate': '-15%',
        'pitch': '-5%',
        'volume': '-3dB',
        'description': 'Slower, lower, quieter'
    },
    'questioning': {
        'rate': '+5%',
        'pitch': '+3%',
        'volume': '+1dB',
        'description': 'Slightly higher pitch for questions'
    },
    'explaining': {
        'rate': '-5%',
        'pitch': '+0%',
        'volume': '+0dB',
        'description': 'Slightly slower for clarity'
    },
    'thoughtful': {
        'rate': '-10%',
        'pitch': '-2%',
        'volume': '+0dB',
        'description': 'Contemplative, measured pace'
    },
    'serious': {
        'rate': '-5%',
        'pitch': '-3%',
        'volume': '+1dB',
        'description': 'Lower pitch, authoritative'
    },
    'grateful': {
        'rate': '+0%',
        'pitch': '+2%',
        'volume': '+0dB',
        'description': 'Warm and appreciative'
    },
    'intrigued': {
        'rate': '+10%',
        'pitch': '+4%',
        'volume': '+1dB',
        'description': 'Curious and interested'
    },
    'amazed': {
        'rate': '+15%',
        'pitch': '+7%',
        'volume': '+2dB',
        'description': 'Surprised and impressed'
    },
    'greeting': {
        'rate': '+5%',
        'pitch': '+3%',
        'volume': '+1dB',
        'description': 'Welcoming and friendly'
    },
    'closing': {
        'rate': '+0%',
        'pitch': '+1%',
        'volume': '+0dB',
        'description': 'Warm conclusion'
    },
    'whisper': {
        'rate': '-25%',
        'pitch': '-2%',
        'volume': '-15dB',
        'description': 'Soft, intimate speech'
    },
    'storytelling': {
        'rate': '-8%',
        'pitch': '+1%',
        'volume': '+0dB',
        'description': 'Engaging narrative pace'
    },
    'urgent': {
        'rate': '+25%',
        'pitch': '+6%',
        'volume': '+4dB',
        'description': 'Fast, elevated, pressing'
    },
    'warm': {
        'rate': '+0%',
        'pitch': '+2%',
        'volume': '+0dB',
        'description': 'Friendly and comforting'
    },
    'optimistic': {
        'rate': '+10%',
        'pitch': '+5%',
        'volume': '+1dB',
        'description': 'Positive and hopeful'
    },
    'understanding': {
        'rate': '-5%',
        'pitch': '+1%',
        'volume': '+0dB',
        'description': 'Empathetic and patient'
    }
}


def get_prosody_for_emotion(emotion):
    """
    Get prosody settings for a given emotion
    
    Args:
        emotion (str): Emotion name (e.g., 'excited', 'calm')
        
    Returns:
        dict: Prosody parameters {rate, pitch, volume}
    """
    emotion_lower = emotion.lower()
    
    # Return emotion prosody if exists, otherwise neutral
    if emotion_lower in EMOTION_PROSODY:
        return EMOTION_PROSODY[emotion_lower]
    else:
        # Default to calm/neutral
        return EMOTION_PROSODY['calm']


def build_ssml_with_emotion(text, emotion, voice_id):
    """
    Build SSML string with prosody for emotion
    
    Args:
        text (str): Text to speak
        emotion (str): Emotion to apply
        voice_id (str): Edge TTS voice ID
        
    Returns:
        str: Complete SSML markup
    """
    prosody = get_prosody_for_emotion(emotion)
    
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{voice_id}">
        <prosody rate="{prosody['rate']}" pitch="{prosody['pitch']}" volume="{prosody['volume']}">
            {text}
        </prosody>
    </voice>
</speak>'''
    
    return ssml


def detect_emotion_from_text(text):
    """
    Simple keyword-based emotion detection from text
    
    Args:
        text (str): Input text
        
    Returns:
        str: Detected emotion
    """
    text_lower = text.lower()
    
    # Excitement indicators
    if any(word in text_lower for word in ['amazing', 'wow', 'incredible', 'fantastic', 'awesome', '!']):
        return 'excited'
    
    # Sadness indicators
    elif any(word in text_lower for word in ['sadly', 'unfortunately', 'tragic', 'disappointed']):
        return 'sad'
    
    # Question indicators
    elif '?' in text:
        return 'questioning'
    
    # Thoughtful indicators
    elif any(word in text_lower for word in ['think', 'consider', 'believe', 'perhaps', 'maybe']):
        return 'thoughtful'
    
    # Greeting indicators
    elif any(word in text_lower for word in ['hello', 'welcome', 'hi ', 'hey']):
        return 'greeting'
    
    # Closing indicators
    elif any(word in text_lower for word in ['goodbye', 'thanks for', 'see you', 'that\'s all']):
        return 'closing'
    
    # Grateful indicators
    elif any(word in text_lower for word in ['thank you', 'thanks', 'grateful', 'appreciate']):
        return 'grateful'
    
    # Default
    else:
        return 'calm'


def list_available_emotions():
    """
    Get list of all available emotions
    
    Returns:
        list: List of emotion dictionaries with name and description
    """
    return [
        {
            'name': emotion,
            'description': props['description'],
            'prosody': {
                'rate': props['rate'],
                'pitch': props['pitch'],
                'volume': props['volume']
            }
        }
        for emotion, props in EMOTION_PROSODY.items()
    ]


if __name__ == '__main__':
    # Test prosody system
    print("Available Emotions:")
    print("=" * 60)
    
    for emotion in list_available_emotions():
        print(f"\n{emotion['name'].upper()}")
        print(f"  Description: {emotion['description']}")
        print(f"  Rate: {emotion['prosody']['rate']}, Pitch: {emotion['prosody']['pitch']}, Volume: {emotion['prosody']['volume']}")
    
    print("\n" + "=" * 60)
    print("\nExample SSML:")
    print(build_ssml_with_emotion("Hello, welcome to our podcast!", "enthusiastic", "en-US-JennyNeural"))

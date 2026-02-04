"""
Voice Manager for Edge TTS
Manages voice selection, organization, and speaker assignments
"""

import edge_tts
import asyncio


# Default podcast voice assignments
PODCAST_VOICES = {
    'HOST': {
        'voice_id': 'en-US-JennyNeural',
        'style': 'cheerful',
        'gender': 'Female',
        'description': 'Main host voice - energetic and engaging'
    },
    'GUEST': {
        'voice_id': 'en-US-GuyNeural',
        'style': 'default',
        'gender': 'Male',
        'description': 'Guest expert voice - professional and clear'
    },
    'NARRATOR': {
        'voice_id': 'en-US-AriaNeural',
        'style': 'newscast',
        'gender': 'Female',
        'description': 'Narrator for transitions and storytelling'
    },
    'CO-HOST': {
        'voice_id': 'en-US-DavisNeural',
        'style': 'chat',
        'gender': 'Male',
        'description': 'Secondary host - casual and friendly'
    },
    'EXPERT': {
        'voice_id': 'en-US-JasonNeural',
        'style': 'default',
        'gender': 'Male',
        'description': 'Technical expert voice'
    }
}


async def list_all_voices():
    """
    Get all available voices from Edge TTS
    
    Returns:
        list: List of voice dictionaries
    """
    voices = await edge_tts.list_voices()
    return voices


def organize_voices_by_locale(voices):
    """
    Group voices by language/locale
    
    Args:
        voices (list): List of voice dictionaries from Edge TTS
        
    Returns:
        dict: Voices organized by locale
    """
    voices_dict = {}
    
    for voice in voices:
        locale = voice['Locale']
        if locale not in voices_dict:
            voices_dict[locale] = []
        
        # Extract display name (last part after ' - ')
        friendly_name = voice.get('FriendlyName', voice['Name'])
        display_name = friendly_name.split(' - ')[-1] if ' - ' in friendly_name else voice['Name']
        
        # Use ShortName as ID (e.g., 'en-US-AriaNeural') instead of full Name
        voice_id = voice.get('ShortName', voice['Name'])
        
        voices_dict[locale].append({
            'id': voice_id,
            'name': friendly_name,
            'display_name': display_name,
            'gender': voice['Gender'],
            'locale': locale
        })
    
    return voices_dict


def assign_voices_to_script(segments, custom_voices=None, language='en-US'):
    """
    Assign Edge TTS voices to each speaker in script segments
    
    Args:
        segments (list): Parsed script segments
        custom_voices (dict): Optional custom voice assignments
        language (str): Language code for default voices
        
    Returns:
        list: Segments with voice_id added
    """
    voice_map = custom_voices if custom_voices else PODCAST_VOICES
    
    # Get default voice based on language if no custom voices provided
    default_voices_by_lang = {
        'en-US': 'en-US-AriaNeural',
        'hi-IN': 'hi-IN-SwaraNeural',
        'es-ES': 'es-ES-ElviraNeural',
        'fr-FR': 'fr-FR-DeniseNeural',
        'de-DE': 'de-DE-KatjaNeural',
        'ja-JP': 'ja-JP-NanamiNeural',
        'zh-CN': 'zh-CN-XiaoxiaoNeural',
        'pt-BR': 'pt-BR-FranciscaNeural',
        'it-IT': 'it-IT-ElsaNeural',
        'ko-KR': 'ko-KR-SunHiNeural',
    }
    
    default_voice = default_voices_by_lang.get(language, 'en-US-AriaNeural')
    
    for segment in segments:
        speaker = segment['speaker']
        
        if speaker in voice_map:
            # Use mapped voice
            if isinstance(voice_map[speaker], dict):
                segment['voice_id'] = voice_map[speaker]['voice_id']
            else:
                # Simple string mapping
                segment['voice_id'] = voice_map[speaker]
        else:
            # Use language-appropriate default voice
            segment['voice_id'] = default_voice
    
    return segments


def get_voices_for_language(locale, voices=None):
    """
    Get all voices for a specific language/locale
    
    Args:
        locale (str): Language code (e.g., 'en-US', 'es-ES')
        voices (list): Optional pre-fetched voice list
        
    Returns:
        list: Voices for that locale
    """
    if voices is None:
        voices = asyncio.run(list_all_voices())
    
    organized = organize_voices_by_locale(voices)
    return organized.get(locale, [])


def detect_language_from_voice(voice_id):
    """
    Extract language code from voice ID
    
    Args:
        voice_id (str): Voice ID (e.g., 'en-US-AriaNeural')
        
    Returns:
        str: Language code (e.g., 'en-US')
    """
    # Voice IDs are formatted as: locale-name
    # e.g., 'en-US-AriaNeural'
    parts = voice_id.split('-')
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return 'en-US'  # Default


def get_demo_text_for_locale(locale):
    """
    Get appropriate demo text for a language
    
    Args:
        locale (str): Language code (e.g., 'en-US')
        
    Returns:
        str: Demo text in that language
    """
    # Extract base language (first part before -)
    lang = locale.split('-')[0].lower()
    
    demo_texts = {
        'en': "Hello! This is a demo of my voice. I can speak naturally with emotion and expression.",
        'es': "¡Hola! Esta es una demostración de mi voz. Puedo hablar de forma natural con emoción.",
        'fr': "Bonjour! Ceci est une démonstration de ma voix. Je peux parler naturellement avec émotion.",
        'de': "Hallo! Dies ist eine Demonstration meiner Stimme. Ich kann natürlich mit Emotion sprechen.",
        'ja': "こんにちは！これは私の声のデモです。自然に感情を込めて話すことができます。",
        'zh': "你好！这是我的声音演示。我可以自然地表达情感。",
        'ar': "مرحبا! هذا عرض توضيحي لصوتي. يمكنني التحدث بشكل طبيعي مع العاطفة.",
        'hi': "नमस्ते! यह मेरी आवाज़ का प्रदर्शन है। मैं भावना के साथ स्वाभाविक रूप से बोल सकता हूं।",
        'pt': "Olá! Esta é uma demonstração da minha voz. Posso falar naturalmente com emoção.",
        'ru': "Привет! Это демонстрация моего голоса. Я могу говорить естественно с эмоциями.",
        'it': "Ciao! Questa è una dimostrazione della mia voce. Posso parlare naturalmente con emozione.",
        'ko': "안녕하세요! 이것은 제 목소리 데모입니다. 감정을 담아 자연스럽게 말할 수 있습니다.",
        'nl': "Hallo! Dit is een demo van mijn stem. Ik kan natuurlijk spreken met emotie.",
        'pl': "Cześć! To jest demonstracja mojego głosu. Mogę mówić naturalnie z emocjami.",
        'sv': "Hej! Detta är en demonstration av min röst. Jag kan tala naturligt med känslor.",
        'tr': "Merhaba! Bu benim sesimin bir gösterimi. Duygularla doğal bir şekilde konuşabilirim.",
    }
    
    return demo_texts.get(lang, demo_texts['en'])


def recommend_voices_for_podcast(num_speakers=2, locale='en-US', voices=None):
    """
    Recommend voice combinations for a podcast
    
    Args:
        num_speakers (int): Number of speakers needed
        locale (str): Language locale
        voices (list): Optional pre-fetched voice list
        
    Returns:
        list: Recommended voice combinations
    """
    if voices is None:
        voices = asyncio.run(list_all_voices())
    
    locale_voices = get_voices_for_language(locale, voices)
    
    if not locale_voices:
        return []
    
    # Separate by gender for variety
    male_voices = [v for v in locale_voices if v['gender'] == 'Male']
    female_voices = [v for v in locale_voices if v['gender'] == 'Female']
    
    recommendations = []
    
    # Recommend alternating genders for natural conversation
    if num_speakers == 2:
        if female_voices and male_voices:
            recommendations.append({
                'HOST': female_voices[0]['id'],
                'GUEST': male_voices[0]['id']
            })
            if len(male_voices) > 1 and len(female_voices) > 1:
                recommendations.append({
                    'HOST': male_voices[0]['id'],
                    'GUEST': female_voices[1]['id']
                })
    
    elif num_speakers == 3:
        if len(female_voices) >= 2 and male_voices:
            recommendations.append({
                'HOST': female_voices[0]['id'],
                'CO-HOST': male_voices[0]['id'],
                'GUEST': female_voices[1]['id']
            })
    
    return recommendations


if __name__ == '__main__':
    # Test voice manager
    print("Testing Voice Manager...")
    print("=" * 60)
    
    print("\nDefault Podcast Voices:")
    for speaker, voice_info in PODCAST_VOICES.items():
        print(f"\n{speaker}:")
        print(f"  Voice: {voice_info['voice_id']}")
        print(f"  Gender: {voice_info['gender']}")
        print(f"  Description: {voice_info['description']}")
    
    print("\n" + "=" * 60)
    print("\nFetching available voices...")
    
    async def test_voices():
        voices = await list_all_voices()
        print(f"Total voices available: {len(voices)}")
        
        organized = organize_voices_by_locale(voices)
        print(f"Languages available: {len(organized)}")
        
        print("\nSample voices by locale:")
        for locale in list(organized.keys())[:5]:
            print(f"\n{locale}:")
            for voice in organized[locale][:3]:
                print(f"  - {voice['display_name']} ({voice['gender']})")
    
    asyncio.run(test_voices())

import asyncio
from utils.voice_manager import list_all_voices, organize_voices_by_locale

async def test():
    voices = await list_all_voices()
    org = organize_voices_by_locale(voices)
    
    # Check te-IN voices
    te_voices = org.get('te-IN', [])
    print("Telugu voices:")
    for v in te_voices[:3]:
        print(f"  ID: {v['id']}")
        print(f"  Display: {v['display_name']}")
        print(f"  Name: {v['name']}")
        print()

asyncio.run(test())

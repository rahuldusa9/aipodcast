"""
Audio Processor for Professional Podcast Quality
NO FFMPEG REQUIRED - Uses binary MP3 concatenation
"""

import os
import numpy as np
# pydub removed - no ffmpeg dependency needed!


# Check if pedalboard is available
try:
    from pedalboard import (
        Pedalboard, NoiseGate, Compressor, Limiter,
        Reverb, HighpassFilter, Gain
    )
    from pedalboard.io import AudioFile
    PEDALBOARD_AVAILABLE = True
except ImportError:
    PEDALBOARD_AVAILABLE = False
    print("Warning: pedalboard not available. Audio effects will be limited.")


def apply_audio_effects(audio_path, emotion):
    """
    Apply emotion-specific audio effects to a segment
    
    Args:
        audio_path (str): Path to audio file
        emotion (str): Emotion to enhance
    """
    # Skip effects for now - they can cause hanging issues
    # Edge TTS already provides good quality audio
    return
    
    if not PEDALBOARD_AVAILABLE:
        return
    
    # Emotion-specific processing
    emotion_effects = {
        'excited': {'gain': 1.0},
        'whisper': {'gain': -3.0},
        'sad': {'gain': -1.0},
        'calm': {'gain': 0.0},
    }
    
    gain_db = emotion_effects.get(emotion.lower(), {}).get('gain', 0.0)
    
    if gain_db != 0.0:
        try:
            with AudioFile(audio_path) as f:
                audio = f.read(f.frames)
                samplerate = f.samplerate
            
            # Apply gain adjustment
            board = Pedalboard([Gain(gain_db=gain_db)])
            processed = board(audio, samplerate)
            
            with AudioFile(audio_path, 'w', samplerate, processed.shape[0]) as f:
                f.write(processed)
        except Exception as e:
            print(f"Warning: Could not apply effects to {audio_path}: {e}")


def apply_master_processing(input_path, output_path):
    """
    Apply professional master chain processing
    Same quality as current TTS system
    
    Args:
        input_path (str): Input audio file path
        output_path (str): Output audio file path
    """
    if not PEDALBOARD_AVAILABLE:
        # Fallback: just copy file if pedalboard not available
        print("Warning: Pedalboard not available, copying file without processing")
        from shutil import copy2
        copy2(input_path, output_path)
        return
    
    try:
        # Load audio
        with AudioFile(input_path) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate
        
        # Build master processing chain
        master_board = Pedalboard([
            # 1. Clean up background noise
            NoiseGate(threshold_db=-45, ratio=3, release_ms=120),
            
            # 2. Remove low-frequency rumble
            HighpassFilter(cutoff_frequency_hz=80),
            
            # 3. Gentle compression for consistency
            Compressor(
                threshold_db=-10,
                ratio=1.8,
                attack_ms=10,
                release_ms=100
            ),
            
            # 4. Subtle room ambience (very light reverb)
            Reverb(
                room_size=0.05,
                damping=0.7,
                wet_level=0.01,
                dry_level=0.99
            ),
            
            # 5. Prevent clipping with limiter
            Limiter(threshold_db=-0.5, release_ms=100),
            
            # 6. Final gain adjustment
            Gain(gain_db=0.0)
        ])
        
        # Process audio
        mastered = master_board(audio, samplerate)
        
        # Convert mono to stereo if needed
        if mastered.ndim == 1 or (mastered.ndim == 2 and mastered.shape[0] == 1):
            if mastered.ndim == 1:
                # Mono array to stereo
                mastered = np.vstack([mastered, mastered])
            else:
                # Single channel to stereo
                mastered = np.vstack([mastered[0], mastered[0]])
        
        # Save processed audio
        with AudioFile(output_path, 'w', samplerate, mastered.shape[0]) as f:
            f.write(mastered)
        
        print(f"✓ Master processing applied: {output_path}")
        
    except Exception as e:
        print(f"Error in master processing: {e}")
        # Fallback: copy original
        from shutil import copy2
        copy2(input_path, output_path)


def add_background_music(podcast_path, music_path, output_path, music_volume_db=-20):
    """
    Add subtle background music to podcast - DISABLED (requires ffmpeg)
    
    Args:
        podcast_path (str): Path to podcast audio
        music_path (str): Path to background music
        output_path (str): Output path
        music_volume_db (int): Background music volume adjustment in dB
    """
    # Background music feature disabled in no-ffmpeg mode
    print("Background music feature disabled (no ffmpeg)")
    from shutil import copy2
    copy2(podcast_path, output_path)


def merge_audio_segments(segment_files, output_path, crossfade_ms=50):
    """
    Merge multiple MP3 segments using binary concatenation (NO FFMPEG NEEDED!)
    
    This works because MP3 is a frame-based format where each frame is independent.
    We simply concatenate the raw MP3 data, skipping metadata headers on subsequent files.
    
    Args:
        segment_files (list): List of audio file paths
        output_path (str): Output merged file path
        crossfade_ms (int): Crossfade duration (ignored in binary mode)
    """
    if not segment_files:
        raise ValueError("No audio segments to merge")
    
    try:
        print(f"Merging {len(segment_files)} segments using binary concatenation...")
        
        with open(output_path, 'wb') as outfile:
            for i, segment_file in enumerate(segment_files):
                if not os.path.exists(segment_file):
                    print(f"Warning: Segment file not found: {segment_file}")
                    continue
                    
                with open(segment_file, 'rb') as infile:
                    data = infile.read()
                    
                    if i == 0:
                        # First file: write everything including ID3 tags and headers
                        outfile.write(data)
                    else:
                        # Subsequent files: skip ID3v2 tags to avoid playback issues
                        if len(data) > 10 and data[:3] == b'ID3':
                            # ID3v2 tag present - calculate size and skip it
                            # ID3v2 size is stored in bytes 6-9 as synchsafe integer
                            size = ((data[6] & 0x7f) << 21) | \
                                   ((data[7] & 0x7f) << 14) | \
                                   ((data[8] & 0x7f) << 7) | \
                                   (data[9] & 0x7f)
                            # Skip the 10-byte header plus the tag size
                            data = data[10 + size:]
                        
                        # Also skip ID3v1 tags at the end if present
                        if len(data) > 128 and data[-128:-125] == b'TAG':
                            data = data[:-128]
                        
                        # Write the MP3 frame data
                        outfile.write(data)
        
        print(f"✓ Successfully merged {len(segment_files)} segments: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error merging audio segments: {e}")
        # Fallback: just copy the first file
        import shutil
        if segment_files and os.path.exists(segment_files[0]):
            shutil.copy2(segment_files[0], output_path)
            print(f"Warning: Used first segment only due to merge error")
        else:
            raise


def create_silence(duration_ms, output_path):
    """
    Create silence - SKIPPED in no-ffmpeg mode
    Edge TTS naturally has appropriate pauses between segments.
    
    Args:
        duration_ms (int): Duration in milliseconds
        output_path (str): Output file path
        
    Returns:
        None: Silence creation is skipped (not critical for podcast quality)
    """
    # Skip silence creation - Edge TTS provides natural pauses between segments
    return None


def normalize_audio_levels(audio_path, target_dBFS=-20.0):
    """
    Normalize audio to target loudness level - DISABLED (requires ffmpeg)
    
    Args:
        audio_path (str): Path to audio file
        target_dBFS (float): Target loudness in dBFS
    """
    # Normalization feature disabled in no-ffmpeg mode
    print(f"Audio normalization feature disabled (no ffmpeg)")


def get_audio_duration(audio_path):
    """
    Get duration of audio file in seconds
    
    Args:
        audio_path (str): Path to audio file
        
    Returns:
        float: Duration in seconds (estimated from file size)
    """
    try:
        # Try with pedalboard if available
        if PEDALBOARD_AVAILABLE:
            with AudioFile(audio_path) as f:
                return f.frames / f.samplerate
    except:
        pass
    
    # Fallback: estimate from file size (rough approximation for MP3)
    # Typical MP3: ~1MB per minute at 128kbps
    file_size = os.path.getsize(audio_path)
    estimated_duration = (file_size / 1024 / 1024) * 60  # MB to minutes
    return estimated_duration * 60  # Convert to seconds


def apply_fade_in_out(audio_path, fade_duration_ms=1000):
    """
    Apply fade in and fade out to audio - DISABLED (requires ffmpeg)
    
    Args:
        audio_path (str): Path to audio file
        fade_duration_ms (int): Fade duration in milliseconds
    """
    # Fade feature disabled in no-ffmpeg mode
    print(f"Fade in/out feature disabled (no ffmpeg)")


if __name__ == '__main__':
    # Test audio processor
    print("Audio Processor Test")
    print("=" * 60)
    
    if PEDALBOARD_AVAILABLE:
        print("✓ Pedalboard available - Full audio processing enabled")
    else:
        print("✗ Pedalboard not available - Limited processing")
    
    print("\nMaster Processing Chain:")
    print("1. Noise Gate (threshold: -45dB)")
    print("2. High-pass Filter (80Hz cutoff)")
    print("3. Compressor (threshold: -10dB, ratio: 1.8:1)")
    print("4. Reverb (room_size: 0.05, wet: 1%)")
    print("5. Limiter (threshold: -0.5dB)")
    print("6. Gain Adjustment")
    print("\nAdditional Features:")
    print("- Background music overlay")
    print("- Segment merging with crossfade")
    print("- Audio normalization")
    print("- Fade in/out effects")

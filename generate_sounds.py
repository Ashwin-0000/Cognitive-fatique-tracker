"""Generate simple notification sounds"""
import wave
import struct
import math
from pathlib import Path


def generate_tone(frequency: float, duration: float, sample_rate: int = 44100) -> bytes:
    """
    Generate a simple sine wave tone.
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
    
    Returns:
        WAV audio data as bytes
    """
    num_samples = int(sample_rate * duration)
    data = []
    
    for i in range(num_samples):
        # Generate sine wave with fade in/out to avoid clicks
        t = i / sample_rate
        fade = 1.0
        
        # Fade in (first 10ms)
        if t < 0.01:
            fade = t / 0.01
        # Fade out (last 10ms)
        elif t > duration - 0.01:
            fade = (duration - t) / 0.01
        
        sample = math.sin(2 * math.pi * frequency * t) * fade
        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        data.append(struct.pack('<h', sample_int))
    
    return b''.join(data)


def save_wav(filename: Path, audio_data: bytes, sample_rate: int = 44100):
    """Save audio data as WAV file"""
    with wave.open(str(filename), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)


def create_notification_sounds(output_dir: Path):
    """Create all notification sound files"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating notification sounds...")
    
    # Break alert: ascending tone (pleasant reminder)
    print("  Creating break_alert.wav...")
    audio = b''
    for freq in [523, 659, 784]:  # C, E, G (C major chord notes)
        audio += generate_tone(freq, 0.15)
    save_wav(output_dir / 'break_alert.wav', audio)
    
    # Fatigue alert: descending tone (attention-getting)
    print("  Creating fatigue_alert.wav...")
    audio = b''
    for freq in [880, 698, 587]:  # A, F, D (descending)
        audio += generate_tone(freq, 0.2)
    save_wav(output_dir / 'fatigue_alert.wav', audio)
    
    # Session start: uplifting chord
    print("  Creating session_start.wav...")
    audio = generate_tone(523, 0.1) + generate_tone(659, 0.1)  # C, E
    save_wav(output_dir / 'session_start.wav', audio)
    
    # Session end: completion tone
    print("  Creating session_end.wav...")
    audio = generate_tone(659, 0.1) + generate_tone(523, 0.15)  # E, C
    save_wav(output_dir / 'session_end.wav', audio)
    
    # Achievement: happy jingle
    print("  Creating achievement.wav...")
    audio = b''
    for freq in [523, 659, 784, 1047]:  # C, E, G, C (octave up)
        audio += generate_tone(freq, 0.1)
    save_wav(output_dir / 'achievement.wav', audio)
    
    print(f"✅ Created 5 notification sounds in {output_dir}")


if __name__ == "__main__":
    # Create sounds in assets/sounds directory
    sounds_dir = Path(__file__).parent / "assets" / "sounds"
    create_notification_sounds(sounds_dir)

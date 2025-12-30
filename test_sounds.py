"""Test sound playback"""
from src.utils.sound_manager import SoundManager
import time

print("🔊 Testing sound playback...")
print("=" * 50)

sound_manager = SoundManager()

if not sound_manager.is_available():
    print("❌ Sound playback NOT available!")
    print("Please install: pip install playsound3")
else:
    print("✅ Sound playback is available!")
    print()
    
    sounds_to_test = [
        ('break_alert', 'Break Alert'),
        ('fatigue_alert', 'Fatigue Alert'),
        ('session_start', 'Session Start'),
        ('session_end', 'Session End'),
        ('achievement', 'Achievement'),
    ]
    
    for sound_id, sound_name in sounds_to_test:
        print(f"Playing: {sound_name}...")
        sound_manager.play(sound_id, async_play=False)
        time.sleep(0.5)  # Brief pause between sounds
    
    print()
    print("✅ All sounds tested!")
    print("If you heard them, sounds are working perfectly!")

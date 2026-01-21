"""Sound notification manager for the Cognitive Fatigue Tracker"""
import os
from pathlib import Path
from typing import Optional
import threading
from src.utils.logger import default_logger as logger

# Try to import playsound, with fallback
try:
    from playsound3 import playsound
    SOUND_AVAILABLE = True
except ImportError:
    try:
        from playsound import playsound
        SOUND_AVAILABLE = True
    except ImportError:
        SOUND_AVAILABLE = False
        logger.warning("playsound not available, sound notifications disabled")


class SoundManager:
    """Manages sound notifications"""

    def __init__(self, sounds_dir: Optional[Path] = None):
        """
        Initialize sound manager.

        Args:
            sounds_dir: Directory containing sound files
        """
        if sounds_dir is None:
            sounds_dir = Path(__file__).parent.parent.parent / \
                "assets" / "sounds"

        self.sounds_dir = Path(sounds_dir)
        self.sounds_dir.mkdir(parents=True, exist_ok=True)

        self.enabled = True
        self.volume = 0.7  # 0.0 to 1.0

        # Sound file paths
        self.sounds = {
            'break_alert': self.sounds_dir / 'break_alert.wav',
            'fatigue_alert': self.sounds_dir / 'fatigue_alert.wav',
            'session_start': self.sounds_dir / 'session_start.wav',
            'session_end': self.sounds_dir / 'session_end.wav',
            'achievement': self.sounds_dir / 'achievement.wav'
        }

        # Create placeholder sounds if they don't exist
        self._ensure_sounds_exist()

        logger.info(
            f"Sound manager initialized (available: {SOUND_AVAILABLE})")

    def _ensure_sounds_exist(self):
        """Ensure sound files exist, create placeholders if needed"""
        # For now, we'll just log if sounds are missing
        # In a real implementation, you'd include actual .wav files
        for sound_name, sound_path in self.sounds.items():
            if not sound_path.exists():
                logger.warning(f"Sound file missing: {sound_path}")

    def play(self, sound_name: str, async_play: bool = True):
        """
        Play a sound.

        Args:
            sound_name: Name of the sound to play
            async_play: Whether to play asynchronously (non-blocking)
        """
        if not self.enabled or not SOUND_AVAILABLE:
            return

        if sound_name not in self.sounds:
            logger.warning(f"Unknown sound: {sound_name}")
            return

        sound_path = self.sounds[sound_name]
        if not sound_path.exists():
            logger.warning(f"Sound file not found: {sound_path}")
            return

        if async_play:
            # Play in background thread to not block
            thread = threading.Thread(
                target=self._play_sound,
                args=(sound_path,),
                daemon=True
            )
            thread.start()
        else:
            self._play_sound(sound_path)

    def _play_sound(self, sound_path: Path):
        """
        Internal method to play a sound file.

        Args:
            sound_path: Path to sound file
        """
        try:
            playsound(str(sound_path))
            logger.debug(f"Played sound: {sound_path.name}")
        except Exception as e:
            logger.error(f"Error playing sound {sound_path}: {e}")

    def play_break_alert(self):
        """Play break reminder sound"""
        self.play('break_alert')

    def play_fatigue_alert(self):
        """Play fatigue alert sound"""
        self.play('fatigue_alert')

    def play_session_start(self):
        """Play session start sound"""
        self.play('session_start')

    def play_session_end(self):
        """Play session end sound"""
        self.play('session_end')

    def play_achievement(self):
        """Play achievement sound"""
        self.play('achievement')

    def set_enabled(self, enabled: bool):
        """Enable or disable sound notifications"""
        self.enabled = enabled
        logger.info(
            f"Sound notifications {'enabled' if enabled else 'disabled'}")

    def set_volume(self, volume: float):
        """
        Set volume level.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        logger.info(f"Sound volume set to {self.volume:.0%}")

    def test_sound(self, sound_name: str = 'break_alert'):
        """
        Test a sound playback.

        Args:
            sound_name: Name of sound to test
        """
        logger.info(f"Testing sound: {sound_name}")
        self.play(sound_name, async_play=False)

    def is_available(self) -> bool:
        """Check if sound playback is available"""
        return SOUND_AVAILABLE

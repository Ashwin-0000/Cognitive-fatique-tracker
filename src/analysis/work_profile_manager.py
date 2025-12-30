"""Work profiles for different types of work sessions"""
from pathlib import Path
from typing import Dict, Optional
import json
from dataclasses import dataclass, asdict
from src.utils.logger import default_logger as logger


@dataclass
class WorkProfile:
    """Represents a work profile with custom settings"""
    name: str
    work_interval: int = 50  # minutes
    break_interval: int = 10
    fatigue_threshold_low: float = 30.0
    fatigue_threshold_moderate: float = 60.0
    fatigue_threshold_high: float = 80.0
    track_eye_strain: bool = True
    sound_enabled: bool = True
    icon: str = "💼"


class WorkProfileManager:
    """Manages different work profiles (Developer, Writer, Meeting, etc.)"""
    
    DEFAULT_PROFILES = {
        'developer': WorkProfile(
            name='Developer',
            work_interval=90,
            break_interval=15,
            icon='👨‍💻'
        ),
        'writer': WorkProfile(
            name='Writer',
            work_interval=60,
            break_interval=10,
            fatigue_threshold_low=25.0,
            fatigue_threshold_moderate=55.0,
            icon='✍️'
        ),
        'designer': WorkProfile(
            name='Designer',
            work_interval=75,
            break_interval=15,
            track_eye_strain=True,
            icon='🎨'
        ),
        'meetings': WorkProfile(
            name='Meetings',
            work_interval=45,
            break_interval=5,
            sound_enabled=False,  # Quiet during meetings
            icon='📞'
        ),
        'general': WorkProfile(
            name='General Work',
            work_interval=50,
            break_interval=10,
            icon='💼'
        )
    }
    
    def __init__(self, profiles_file: Optional[Path] = None):
        """
        Initialize work profile manager.
        
        Args:
            profiles_file: File to store custom profiles
        """
        if profiles_file is None:
            profiles_file = Path(__file__).parent.parent.parent / "data" / "work_profiles.json"
        
        self.profiles_file = Path(profiles_file)
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.profiles = self._load_profiles()
        self.active_profile = 'general'
        
        logger.info("Work profile manager initialized")
    
    def _load_profiles(self) -> Dict[str, WorkProfile]:
        """Load profiles from file"""
        profiles = self.DEFAULT_PROFILES.copy()
        
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    
                for profile_id, profile_data in data.items():
                    profiles[profile_id] = WorkProfile(**profile_data)
                    
            except Exception as e:
                logger.error(f"Error loading work profiles: {e}")
        
        return profiles
    
    def _save_profiles(self):
        """Save profiles to file"""
        try:
            data = {}
            for profile_id, profile in self.profiles.items():
                if profile_id not in self.DEFAULT_PROFILES:  # Only save custom profiles
                    data[profile_id] = asdict(profile)
            
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving work profiles: {e}")
    
    def get_profile(self, profile_id: str) -> Optional[WorkProfile]:
        """Get a work profile by ID"""
        return self.profiles.get(profile_id)
    
    def get_active_profile(self) -> WorkProfile:
        """Get the currently active profile"""
        return self.profiles.get(self.active_profile, self.DEFAULT_PROFILES['general'])
    
    def set_active_profile(self, profile_id: str) -> bool:
        """
        Set the active work profile.
        
        Args:
            profile_id: Profile ID to activate
        
        Returns:
            True if successful
        """
        if profile_id in self.profiles:
            self.active_profile = profile_id
            logger.info(f"Activated work profile: {self.profiles[profile_id].name}")
            return True
        return False
    
    def create_custom_profile(self, profile_id: str, profile: WorkProfile) -> bool:
        """
        Create a custom work profile.
        
        Args:
            profile_id: Unique profile ID
            profile: WorkProfile instance
        
        Returns:
            True if created successfully
        """
        if profile_id in self.DEFAULT_PROFILES:
            logger.warning(f"Cannot override default profile: {profile_id}")
            return False
        
        self.profiles[profile_id] = profile
        self._save_profiles()
        logger.info(f"Created custom profile: {profile.name}")
        return True
    
    def delete_custom_profile(self, profile_id: str) -> bool:
        """Delete a custom profile"""
        if profile_id in self.DEFAULT_PROFILES:
            return False
        
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            self._save_profiles()
            return True
        
        return False
    
    def get_all_profiles(self) -> Dict[str, WorkProfile]:
        """Get all available profiles"""
        return self.profiles

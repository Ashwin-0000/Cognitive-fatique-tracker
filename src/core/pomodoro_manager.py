"""Pomodoro timer presets for different work styles"""
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import json
from src.utils.logger import default_logger as logger


@dataclass
class PomodoroPreset:
    """Pomodoro timer preset configuration"""
    name: str
    work_minutes: int
    short_break_minutes: int
    long_break_minutes: int
    cycles_before_long_break: int
    icon: str = "🍅"


class PomodoroManager:
    """Manages Pomodoro timer presets"""
    
    PRESET_POMODOROS = {
        'classic': PomodoroPreset(
            name='Classic Pomodoro',
            work_minutes=25,
            short_break_minutes=5,
            long_break_minutes=15,
            cycles_before_long_break=4
        ),
        'extended': PomodoroPreset(
            name='Extended Focus',
            work_minutes=50,
            short_break_minutes=10,
            long_break_minutes=30,
            cycles_before_long_break=3
        ),
        'short_burst': PomodoroPreset(
            name='Short Bursts',
            work_minutes=15,
            short_break_minutes=3,
            long_break_minutes=10,
            cycles_before_long_break=5
        ),
        'deep_work': PomodoroPreset(
            name='Deep Work',
            work_minutes=90,
            short_break_minutes=20,
            long_break_minutes=45,
            cycles_before_long_break=2
        ),
        'quick_tasks': PomodoroPreset(
            name='Quick Tasks',
            work_minutes=10,
            short_break_minutes=2,
            long_break_minutes=5,
            cycles_before_long_break=6
        )
    }
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize Pomodoro manager.
        
        Args:
            config_file: File to store custom presets
        """
        if config_file is None:
            config_file = Path(__file__).parent.parent.parent / "config" / "pomodoro_presets.json"
        
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.custom_presets = self._load_custom_presets()
        self.active_preset = 'classic'
        self.current_cycle = 0
        
        logger.info("Pomodoro manager initialized")
    
    def _load_custom_presets(self) -> Dict[str, PomodoroPreset]:
        """Load custom presets from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return {
                        k: PomodoroPreset(**v) 
                        for k, v in data.items()
                    }
            except Exception as e:
                logger.error(f"Error loading Pomodoro presets: {e}")
        
        return {}
    
    def _save_custom_presets(self):
        """Save custom presets to file"""
        try:
            data = {
                k: {
                    'name': v.name,
                    'work_minutes': v.work_minutes,
                    'short_break_minutes': v.short_break_minutes,
                    'long_break_minutes': v.long_break_minutes,
                    'cycles_before_long_break': v.cycles_before_long_break,
                    'icon': v.icon
                }
                for k, v in self.custom_presets.items()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving Pomodoro presets: {e}")
    
    def get_preset(self, preset_id: str) -> Optional[PomodoroPreset]:
        """Get a Pomodoro preset by ID"""
        if preset_id in self.PRESET_POMODOROS:
            return self.PRESET_POMODOROS[preset_id]
        return self.custom_presets.get(preset_id)
    
    def get_all_presets(self) -> Dict[str, PomodoroPreset]:
        """Get all available presets"""
        all_presets = self.PRESET_POMODOROS.copy()
        all_presets.update(self.custom_presets)
        return all_presets
    
    def set_active_preset(self, preset_id: str) -> bool:
        """Set the active Pomodoro preset"""
        if self.get_preset(preset_id):
            self.active_preset = preset_id
            self.current_cycle = 0
            logger.info(f"Active Pomodoro preset: {preset_id}")
            return True
        return False
    
    def get_active_preset(self) -> PomodoroPreset:
        """Get the currently active preset"""
        return self.get_preset(self.active_preset) or self.PRESET_POMODOROS['classic']
    
    def create_custom_preset(self, preset_id: str, preset: PomodoroPreset) -> bool:
        """Create a custom Pomodoro preset"""
        if preset_id in self.PRESET_POMODOROS:
            return False
        
        self.custom_presets[preset_id] = preset
        self._save_custom_presets()
        return True
    
    def delete_custom_preset(self, preset_id: str) -> bool:
        """Delete a custom preset"""
        if preset_id in self.custom_presets:
            del self.custom_presets[preset_id]
            self._save_custom_presets()
            return True
        return False
    
    def get_next_break_duration(self) -> int:
        """Get duration for next break based on cycle count"""
        preset = self.get_active_preset()
        
        if (self.current_cycle + 1) % preset.cycles_before_long_break == 0:
            return preset.long_break_minutes
        else:
            return preset.short_break_minutes
    
    def complete_cycle(self):
        """Mark a work cycle as complete"""
        self.current_cycle += 1
        logger.info(f"Completed Pomodoro cycle {self.current_cycle}")
    
    def reset_cycles(self):
        """Reset cycle counter"""
        self.current_cycle = 0
        logger.info("Reset Pomodoro cycles")

"""Achievement system for tracking user milestones"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import json

from src.utils.logger import default_logger as logger


@dataclass
class Achievement:
    """Represents an achievement"""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0
    target: float = 100.0


class AchievementManager:
    """Manages user achievements and streaks"""

    ACHIEVEMENTS = [
        {
            'id': 'first_session',
            'name': 'Getting Started',
            'description': 'Complete your first session',
            'icon': '🚀',
            'target': 1
        },
        {
            'id': 'streak_7',
            'name': '7-Day Streak',
            'description': 'Use the app for 7 consecutive days',
            'icon': '🔥',
            'target': 7
        },
        {
            'id': 'streak_30',
            'name': '30-Day Champion',
            'description': 'Use the app for 30 consecutive days',
            'icon': '👑',
            'target': 30
        },
        {
            'id': 'break_master',
            'name': 'Break Master',
            'description': 'Take 50 breaks',
            'icon': '☕',
            'target': 50
        },
        {
            'id': 'marathon_worker',
            'name': 'Marathon Worker',
            'description': 'Work for 100 hours total',
            'icon': '💪',
            'target': 100
        },
        {
            'id': 'early_bird',
            'name': 'Early Bird',
            'description': 'Start 10 sessions before 8 AM',
            'icon': '🌅',
            'target': 10
        },
        {
            'id': 'night_owl',
            'name': 'Night Owl',
            'description': 'Start 10 sessions after 8 PM',
            'icon': '🦉',
            'target': 10
        }
    ]

    def __init__(self, achievements_file: Optional[Path] = None):
        """
        Initialize achievement manager.

        Args:
            achievements_file: File to store achievement data
        """
        if achievements_file is None:
            achievements_file = Path(
                __file__).parent.parent.parent / "data" / "achievements.json"

        self.achievements_file = Path(achievements_file)
        self.achievements_file.parent.mkdir(parents=True, exist_ok=True)

        self.achievements = self._load_achievements()

        logger.info("Achievement manager initialized")

    def _load_achievements(self) -> List[Achievement]:
        """Load achievements from file"""
        achievements = []

        # Load saved data
        saved_data = {}
        if self.achievements_file.exists():
            try:
                with open(self.achievements_file, 'r') as f:
                    saved_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading achievements: {e}")

        # Create achievement objects
        for ach_def in self.ACHIEVEMENTS:
            ach_id = ach_def['id']
            saved = saved_data.get(ach_id, {})

            achievement = Achievement(
                id=ach_id,
                name=ach_def['name'],
                description=ach_def['description'],
                icon=ach_def['icon'],
                unlocked=saved.get(
                    'unlocked',
                    False),
                unlocked_at=datetime.fromisoformat(
                    saved['unlocked_at']) if 'unlocked_at' in saved else None,
                progress=saved.get(
                    'progress',
                    0.0),
                target=ach_def['target'])
            achievements.append(achievement)

        return achievements

    def _save_achievements(self):
        """Save achievements to file"""
        try:
            data = {}
            for ach in self.achievements:
                data[ach.id] = {
                    'unlocked': ach.unlocked,
                    'unlocked_at': ach.unlocked_at.isoformat() if ach.unlocked_at else None,
                    'progress': ach.progress
                }

            with open(self.achievements_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving achievements: {e}")

    def update_progress(
            self,
            achievement_id: str,
            progress: float) -> Optional[Achievement]:
        """
        Update achievement progress.

        Args:
            achievement_id: Achievement ID
            progress: New progress value

        Returns:
            Achievement if newly unlocked, None otherwise
        """
        for ach in self.achievements:
            if ach.id == achievement_id and not ach.unlocked:
                ach.progress = progress

                if ach.progress >= ach.target:
                    ach.unlocked = True
                    ach.unlocked_at = datetime.now()
                    self._save_achievements()
                    logger.info(f"Achievement unlocked: {ach.name}")
                    return ach

                self._save_achievements()
                break

        return None

    def check_session_achievements(
            self,
            session_count: int,
            total_hours: float,
            total_breaks: int,
            start_hour: int) -> List[Achievement]:
        """
        Check and update session-based achievements.

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        # First session
        if session_count >= 1:
            ach = self.update_progress('first_session', session_count)
            if ach:
                newly_unlocked.append(ach)

        # Break master
        ach = self.update_progress('break_master', total_breaks)
        if ach:
            newly_unlocked.append(ach)

        # Marathon worker
        ach = self.update_progress('marathon_worker', total_hours)
        if ach:
            newly_unlocked.append(ach)

        # Early bird
        if start_hour < 8:
            for ach in self.achievements:
                if ach.id == 'early_bird' and not ach.unlocked:
                    ach.progress += 1
                    if ach.progress >= ach.target:
                        ach.unlocked = True
                        ach.unlocked_at = datetime.now()
                        newly_unlocked.append(ach)
                    self._save_achievements()
                    break

        # Night owl
        if start_hour >= 20:
            for ach in self.achievements:
                if ach.id == 'night_owl' and not ach.unlocked:
                    ach.progress += 1
                    if ach.progress >= ach.target:
                        ach.unlocked = True
                        ach.unlocked_at = datetime.now()
                        newly_unlocked.append(ach)
                    self._save_achievements()
                    break

        return newly_unlocked

    def check_streak_achievements(
            self, current_streak: int) -> List[Achievement]:
        """Check streak-based achievements"""
        newly_unlocked = []

        # 7-day streak
        if current_streak >= 7:
            ach = self.update_progress('streak_7', current_streak)
            if ach:
                newly_unlocked.append(ach)

        # 30-day streak
        if current_streak >= 30:
            ach = self.update_progress('streak_30', current_streak)
            if ach:
                newly_unlocked.append(ach)

        return newly_unlocked

    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements"""
        return self.achievements

    def get_unlocked_count(self) -> int:
        """Get number of unlocked achievements"""
        return sum(1 for ach in self.achievements if ach.unlocked)

    def get_completion_percentage(self) -> float:
        """Get overall completion percentage"""
        if not self.achievements:
            return 0.0
        return (self.get_unlocked_count() / len(self.achievements)) * 100

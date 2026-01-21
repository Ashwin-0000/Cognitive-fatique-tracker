"""Do Not Disturb mode to temporarily disable alerts"""
from datetime import datetime, timedelta
from typing import Optional
from src.utils.logger import default_logger as logger


class DNDManager:
    """Manages Do Not Disturb mode"""

    def __init__(self):
        """Initialize DND manager"""
        self.is_enabled = False
        self.end_time: Optional[datetime] = None

        logger.info("DND manager initialized")

    def enable_dnd(self, duration_minutes: Optional[int] = None):
        """
        Enable Do Not Disturb mode.

        Args:
            duration_minutes: Duration in minutes (None = indefinite)
        """
        self.is_enabled = True

        if duration_minutes:
            self.end_time = datetime.now() + timedelta(minutes=duration_minutes)
            logger.info(f"DND enabled for {duration_minutes} minutes")
        else:
            self.end_time = None
            logger.info("DND enabled indefinitely")

    def disable_dnd(self):
        """Disable Do Not Disturb mode"""
        self.is_enabled = False
        self.end_time = None
        logger.info("DND disabled")

    def toggle_dnd(self, duration_minutes: Optional[int] = None):
        """Toggle DND mode"""
        if self.is_enabled:
            self.disable_dnd()
        else:
            self.enable_dnd(duration_minutes)

    def check_and_update(self) -> bool:
        """
        Check if DND should auto-disable.

        Returns:
            True if DND is currently active
        """
        if self.is_enabled and self.end_time:
            if datetime.now() >= self.end_time:
                self.disable_dnd()
                return False

        return self.is_enabled

    def get_remaining_time(self) -> Optional[timedelta]:
        """Get remaining DND time"""
        if self.is_enabled and self.end_time:
            remaining = self.end_time - datetime.now()
            if remaining.total_seconds() > 0:
                return remaining
        return None

    def should_suppress_alerts(self) -> bool:
        """Check if alerts should be suppressed"""
        return self.check_and_update()

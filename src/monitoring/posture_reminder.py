"""Posture reminder system"""
from datetime import datetime, timedelta
from typing import Optional, Callable
from src.utils.logger import default_logger as logger


class PostureReminder:
    """Reminds users to check and correct their posture"""
    
    REMINDERS = [
        "💺 Posture Check: Sit up straight with your back against the chair.",
        "🧘 Posture Tip: Keep your feet flat on the floor.",
        "💪 Posture Alert: Shoulders relaxed, not hunched forward.",
        "👀 Posture Check: Screen should be at eye level.",
        "✋ Posture Reminder: Keep your wrists in a neutral position.",
        "🪑 Posture Tip: Use a chair with good lumbar support.",
        "📏 Posture Check: Maintain proper distance from screen (arm's length).",
        "🔄 Posture Alert: Change positions periodically to avoid stiffness."
    ]
    
    def __init__(
        self,
        reminder_interval_minutes: int = 30,
        on_reminder: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize posture reminder.
        
        Args:
            reminder_interval_minutes: Minutes between reminders
            on_reminder: Callback for when reminder is triggered
        """
        self.interval = timedelta(minutes=reminder_interval_minutes)
        self.on_reminder = on_reminder
        self.last_reminder_time: Optional[datetime] = None
        self.enabled = True
        self.reminder_count = 0
        
        logger.info(f"Posture reminder initialized (interval: {reminder_interval_minutes}min)")
    
    def check_and_remind(self) -> bool:
        """
        Check if it's time for a posture reminder.
        
        Returns:
            True if reminder was sent
        """
        if not self.enabled:
            return False
        
        now = datetime.now()
        
        # First reminder or interval elapsed
        if (self.last_reminder_time is None or 
            now - self.last_reminder_time >= self.interval):
            
            self._send_reminder()
            self.last_reminder_time = now
            self.reminder_count += 1
            return True
        
        return False
    
    def _send_reminder(self):
        """Send a posture reminder"""
        reminder_index = self.reminder_count % len(self.REMINDERS)
        reminder = self.REMINDERS[reminder_index]
        
        logger.info(f"Posture reminder: {reminder}")
        
        if self.on_reminder:
            try:
                self.on_reminder(reminder)
            except Exception as e:
                logger.error(f"Error sending posture reminder: {e}")
    
    def enable(self):
        """Enable posture reminders"""
        self.enabled = True
        logger.info("Posture reminders enabled")
    
    def disable(self):
        """Disable posture reminders"""
        self.enabled = False
        logger.info("Posture reminders disabled")
    
    def set_interval(self, minutes: int):
        """Set reminder interval"""
        self.interval = timedelta(minutes=minutes)
        logger.info(f"Posture reminder interval set to {minutes} minutes")
    
    def reset(self):
        """Reset reminder state"""
        self.last_reminder_time = None
        self.reminder_count = 0
        logger.info("Posture reminder reset")

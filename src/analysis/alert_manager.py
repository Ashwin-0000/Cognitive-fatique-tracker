"""Alert manager for break reminders and fatigue notifications"""
from datetime import datetime, timedelta
from typing import Optional, Callable
from src.models.fatigue_score import FatigueScore
from src.utils.logger import default_logger as logger

# Import sound manager
try:
    from src.utils.sound_manager import SoundManager
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    logger.warning("SoundManager not available")


class AlertManager:
    """Manages alerts and notifications for breaks and fatigue"""
    
    def __init__(
        self,
        on_alert: Optional[Callable[[str, str], None]] = None,
        cooldown_minutes: int = 10
    ):
        """
        Initialize alert manager.
        
        Args:
            on_alert: Callback function for alerts (title, message)
            cooldown_minutes: Minutes between repeated alerts
        """
        self.on_alert = on_alert
        self.cooldown_period = timedelta(minutes=cooldown_minutes)
        
        # Initialize sound manager
        self.sound_manager = SoundManager() if SOUND_AVAILABLE else None
        
        self._last_break_alert: Optional[datetime] = None
        self._last_fatigue_alert: Optional[datetime] = None
        self._last_critical_alert: Optional[datetime] = None
        
        self.break_alerts_enabled = True
        self.fatigue_alerts_enabled = True
    
    def check_break_reminder(self, time_until_break: timedelta, is_on_break: bool = False):
        """
        Check if break reminder should be shown.
        
        Args:
            time_until_break: Time remaining until recommended break
            is_on_break: Whether currently on break
        """
        if not self.break_alerts_enabled or is_on_break:
            return
        
        # Alert if it's time for a break and not in cooldown
        if time_until_break <= timedelta() and self._can_send_break_alert():
            self._send_alert(
                "Time for a Break! ⏰",
                "You've been working for a while. Take a short break to refresh.",
                alert_type='break'
            )
            self._last_break_alert = datetime.now()
    
    def check_fatigue_level(self, fatigue_score: FatigueScore):
        """
        Check fatigue level and send alerts if needed.
        
        Args:
            fatigue_score: Current fatigue score
        """
        if not self.fatigue_alerts_enabled:
            return
        
        level = fatigue_score.get_level()
        
        # Critical fatigue alert
        if level == "Critical" and self._can_send_critical_alert():
            self._send_alert(
                "🚨 Critical Fatigue Level!",
                f"Your fatigue score is {fatigue_score.score:.0f}. Please take a break immediately!",
                alert_type='critical'
            )
            self._last_critical_alert = datetime.now()
        
        # High fatigue alert
        elif level == "High" and self._can_send_fatigue_alert():
            self._send_alert(
                "⚠️ High Fatigue Detected",
                f"Your fatigue level is high ({fatigue_score.score:.0f}). Consider taking a break soon.",
                alert_type='fatigue'
            )
            self._last_fatigue_alert = datetime.now()
        
        # Moderate fatigue (less urgent)
        elif level == "Moderate" and self._can_send_fatigue_alert():
            # Only send if cooldown has passed
            now = datetime.now()
            if (self._last_fatigue_alert is None or 
                now - self._last_fatigue_alert > self.cooldown_period * 2):  # Longer cooldown
                self._send_alert(
                    "Moderate Fatigue 💡",
                    f"Fatigue level: {fatigue_score.score:.0f}. Plan a break in the near future.",
                    alert_type='info'
                )
                self._last_fatigue_alert = now
    
    def check_eye_strain(self, blink_rate: float):
        """
        Check for eye strain based on blink rate.
        
        Args:
            blink_rate: Current blink rate (blinks per minute)
        """
        if not self.fatigue_alerts_enabled or blink_rate <= 0:
            return
        
        # Critical eye strain (< 10 bpm)
        if blink_rate < 10 and self._can_send_critical_alert():
            self._send_alert(
                "👁️ Eye Strain Alert!",
                f"Your blink rate is very low ({blink_rate:.1f} bpm). "
                "Try the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds.",
                alert_type='eye_strain'
            )
            self._last_critical_alert = datetime.now()
        
        # Moderate eye strain (< 15 bpm)
        elif blink_rate < 15 and self._can_send_fatigue_alert():
            now = datetime.now()
            # Longer cooldown for moderate eye strain
            if (self._last_fatigue_alert is None or 
                now - self._last_fatigue_alert > self.cooldown_period * 2):
                self._send_alert(
                    "👁️ Low Blink Rate",
                    f"Your blink rate ({blink_rate:.1f} bpm) is below normal. "
                    "Remember to blink regularly and look away from the screen.",
                    alert_type='info'
                )
                self._last_fatigue_alert = now

    
    def send_break_complete_notification(self):
        """Notify when break is complete"""
        self._send_alert(
            "Break Complete! 🎯",
            "Your break is over. Ready to get back to work?",
            alert_type='info'
        )
    
    def send_session_start_notification(self):
        """Notify when new session starts"""
        self._send_alert(
            "Session Started 🚀",
            "New work session has begun. Stay focused and take breaks when needed!",
            alert_type='info'
        )
    
    def send_custom_alert(self, title: str, message: str):
        """
        Send a custom alert.
        
        Args:
            title: Alert title
            message: Alert message
        """
        self._send_alert(title, message, alert_type='custom')
    
    def _send_alert(self, title: str, message: str, alert_type: str = 'info'):
        """
        Send an alert through the callback.
        
        Args:
            title: Alert title
            message: Alert message
            alert_type: Type of alert (break, fatigue, critical, info, custom)
        """
        logger.info(f"Alert [{alert_type}]: {title} - {message}")
        
        # Play appropriate sound
        if self.sound_manager:
            if alert_type == 'break':
                self.sound_manager.play_break_alert()
            elif alert_type in ['fatigue', 'critical', 'eye_strain']:
                self.sound_manager.play_fatigue_alert()
        
        if self.on_alert:
            try:
                self.on_alert(title, message)
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
    
    def _can_send_break_alert(self) -> bool:
        """Check if break alert can be sent (not in cooldown)"""
        if self._last_break_alert is None:
            return True
        return datetime.now() - self._last_break_alert > self.cooldown_period
    
    def _can_send_fatigue_alert(self) -> bool:
        """Check if fatigue alert can be sent (not in cooldown)"""
        if self._last_fatigue_alert is None:
            return True
        return datetime.now() - self._last_fatigue_alert > self.cooldown_period
    
    def _can_send_critical_alert(self) -> bool:
        """Check if critical alert can be sent (shorter cooldown)"""
        if self._last_critical_alert is None:
            return True
        # Critical alerts have shorter cooldown (half the normal)
        return datetime.now() - self._last_critical_alert > (self.cooldown_period / 2)
    
    def enable_alerts(self, break_alerts: bool = True, fatigue_alerts: bool = True):
        """
        Enable or disable alerts.
        
        Args:
            break_alerts: Enable break reminder alerts
            fatigue_alerts: Enable fatigue level alerts
        """
        self.break_alerts_enabled = break_alerts
        self.fatigue_alerts_enabled = fatigue_alerts
        logger.info(f"Alerts configured: breaks={break_alerts}, fatigue={fatigue_alerts}")
    
    def reset_cooldowns(self):
        """Reset all alert cooldowns"""
        self._last_break_alert = None
        self._last_fatigue_alert = None
        self._last_critical_alert = None
        logger.debug("Reset alert cooldowns")
    
    def update_cooldown(self, minutes: int):
        """
        Update cooldown period.
        
        Args:
            minutes: New cooldown period in minutes
        """
        self.cooldown_period = timedelta(minutes=minutes)
        logger.info(f"Updated alert cooldown to {minutes} minutes")

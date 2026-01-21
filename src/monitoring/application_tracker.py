"""Application-specific tracking to monitor which apps are used"""
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import platform

# Platform-specific imports
if platform.system() == 'Windows':
    try:
        import win32gui
        import win32process
        import psutil
        TRACKING_AVAILABLE = True
    except ImportError:
        TRACKING_AVAILABLE = False
else:
    TRACKING_AVAILABLE = False

from src.utils.logger import default_logger as logger


class ApplicationTracker:
    """Tracks which applications are being used during work sessions"""

    def __init__(self):
        """Initialize application tracker"""
        self.is_tracking = False
        self.app_usage = defaultdict(float)  # app_name -> total_seconds
        self.current_app = None
        self.last_check_time = None

        logger.info(
            f"Application tracker initialized (available: {TRACKING_AVAILABLE})")

    def start_tracking(self):
        """Start tracking application usage"""
        self.is_tracking = True
        self.app_usage.clear()
        self.last_check_time = time.time()
        logger.info("Started application tracking")

    def stop_tracking(self):
        """Stop tracking application usage"""
        self.is_tracking = False
        logger.info("Stopped application tracking")

    def update(self) -> Optional[str]:
        """
        Update application tracking.

        Returns:
            Current active application name
        """
        if not self.is_tracking or not TRACKING_AVAILABLE:
            return None

        current_time = time.time()
        elapsed = current_time - self.last_check_time if self.last_check_time else 0

        # Get active window
        active_app = self._get_active_window()

        if active_app and elapsed > 0:
            self.app_usage[active_app] += elapsed
            self.current_app = active_app

        self.last_check_time = current_time
        return active_app

    def _get_active_window(self) -> Optional[str]:
        """Get the name of the active window/application"""
        if not TRACKING_AVAILABLE:
            return None

        try:
            if platform.system() == 'Windows':
                window = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
                return process.name()
        except Exception as e:
            logger.debug(f"Error getting active window: {e}")

        return None

    def get_usage_stats(self) -> Dict[str, float]:
        """
        Get application usage statistics.

        Returns:
            Dict mapping app names to usage time in seconds
        """
        return dict(self.app_usage)

    def get_top_apps(self, limit: int = 5) -> List[tuple]:
        """
        Get top applications by usage time.

        Args:
            limit: Number of top apps to return

        Returns:
            List of (app_name, seconds) tuples
        """
        sorted_apps = sorted(
            self.app_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_apps[:limit]

    def get_usage_percentage(self, app_name: str) -> float:
        """Get percentage of time spent in a specific app"""
        total_time = sum(self.app_usage.values())
        if total_time == 0:
            return 0.0

        app_time = self.app_usage.get(app_name, 0)
        return (app_time / total_time) * 100

    def reset_stats(self):
        """Reset all tracking statistics"""
        self.app_usage.clear()
        logger.info("Reset application tracking stats")

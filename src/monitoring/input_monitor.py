"""Input monitor for keyboard and mouse activity"""
import threading
from datetime import datetime, timedelta
from collections import deque
from typing import Callable, Optional
from pynput import keyboard, mouse
from src.models.activity_data import ActivityData
from src.utils.logger import default_logger as logger


class InputMonitor:
    """Monitors keyboard and mouse input activity"""

    def __init__(
        self,
        on_activity: Optional[Callable[[ActivityData], None]] = None,
        track_keyboard: bool = True,
        track_mouse_clicks: bool = True,
        track_mouse_movement: bool = False
    ):
        """
        Initialize input monitor.

        Args:
            on_activity: Callback function when activity is detected
            track_keyboard: Whether to track keyboard events
            track_mouse_clicks: Whether to track mouse clicks
            track_mouse_movement: Whether to track mouse movement
        """
        self.on_activity = on_activity
        self.track_keyboard = track_keyboard
        self.track_mouse_clicks = track_mouse_clicks
        self.track_mouse_movement = track_mouse_movement

        self.is_running = False
        self._keyboard_listener = None
        self._mouse_listener = None

        # Activity tracking
        self._activity_queue = deque(maxlen=10000)
        self._activity_count = 0
        self._last_activity_time = datetime.now()

        # Rate limiting for mouse movement
        self._last_mouse_move_time = datetime.now()
        self._mouse_move_threshold = timedelta(seconds=1)

    def start(self):
        """Start monitoring input"""
        if self.is_running:
            logger.warning("Input monitor already running")
            return

        self.is_running = True

        # Start keyboard listener
        if self.track_keyboard:
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_keyboard_event
            )
            self._keyboard_listener.start()
            logger.info("Started keyboard monitoring")

        # Start mouse listener
        if self.track_mouse_clicks or self.track_mouse_movement:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click if self.track_mouse_clicks else None,
                on_move=self._on_mouse_move if self.track_mouse_movement else None,
                on_scroll=self._on_mouse_scroll if self.track_mouse_clicks else None)
            self._mouse_listener.start()
            logger.info("Started mouse monitoring")

    def stop(self):
        """Stop monitoring input"""
        if not self.is_running:
            return

        self.is_running = False

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        logger.info("Stopped input monitoring")

    def _on_keyboard_event(self, key):
        """Handle keyboard event"""
        try:
            activity = ActivityData(
                event_type='keyboard',
                details={'key': str(key)}
            )
            self._record_activity(activity)
        except Exception as e:
            logger.error(f"Error handling keyboard event: {e}")

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click event"""
        if pressed:  # Only count press, not release
            try:
                activity = ActivityData(
                    event_type='mouse_click',
                    details={'x': x, 'y': y, 'button': str(button)}
                )
                self._record_activity(activity)
            except Exception as e:
                logger.error(f"Error handling mouse click: {e}")

    def _on_mouse_move(self, x, y):
        """Handle mouse movement event (rate-limited)"""
        now = datetime.now()
        if now - self._last_mouse_move_time > self._mouse_move_threshold:
            try:
                activity = ActivityData(
                    event_type='mouse_move',
                    details={'x': x, 'y': y}
                )
                self._record_activity(activity)
                self._last_mouse_move_time = now
            except Exception as e:
                logger.error(f"Error handling mouse move: {e}")

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll event"""
        try:
            activity = ActivityData(
                event_type='mouse_scroll',
                details={'x': x, 'y': y, 'dx': dx, 'dy': dy}
            )
            self._record_activity(activity)
        except Exception as e:
            logger.error(f"Error handling mouse scroll: {e}")

    def _record_activity(self, activity: ActivityData):
        """Record an activity event"""
        self._activity_queue.append(activity)
        self._activity_count += 1
        self._last_activity_time = activity.timestamp

        # Call callback if provided
        if self.on_activity:
            try:
                self.on_activity(activity)
            except Exception as e:
                logger.error(f"Error in activity callback: {e}")

    def get_activity_rate(self, window_seconds: int = 60) -> float:
        """
        Get activity rate (events per minute).

        Args:
            window_seconds: Time window to calculate rate

        Returns:
            Events per minute
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        recent_count = sum(
            1 for activity in self._activity_queue
            if activity.timestamp >= cutoff
        )

        return (recent_count / window_seconds) * 60

    def get_total_count(self) -> int:
        """Get total activity count"""
        return self._activity_count

    def get_last_activity_time(self) -> datetime:
        """Get timestamp of last activity"""
        return self._last_activity_time

    def get_idle_time(self) -> timedelta:
        """Get time since last activity"""
        return datetime.now() - self._last_activity_time

    def get_keyboard_count(self, window_seconds: int = 60) -> int:
        """
        Get keyboard event count in time window.

        Args:
            window_seconds: Time window to count events

        Returns:
            Number of keyboard events
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        return sum(
            1 for activity in self._activity_queue
            if activity.timestamp >= cutoff and activity.event_type == 'keyboard'
        )

    def get_mouse_click_count(self, window_seconds: int = 60) -> int:
        """
        Get mouse click count in time window.

        Args:
            window_seconds: Time window to count events

        Returns:
            Number of mouse clicks (including scrolls)
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        return sum(1 for activity in self._activity_queue if activity.timestamp >=
                   cutoff and activity.event_type in ['mouse_click', 'mouse_scroll'])

    def reset_count(self):
        """Reset activity counter"""
        self._activity_count = 0
        self._activity_queue.clear()
        logger.debug("Reset activity counter")

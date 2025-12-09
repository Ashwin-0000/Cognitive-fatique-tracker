"""Activity data model for tracking user input events"""
from datetime import datetime
from typing import Literal, Optional


class ActivityData:
    """Represents a single activity event (keyboard or mouse)"""
    
    def __init__(
        self,
        event_type: Literal['keyboard', 'mouse_click', 'mouse_move', 'mouse_scroll'],
        timestamp: Optional[datetime] = None,
        details: Optional[dict] = None
    ):
        """
        Initialize an activity event.
        
        Args:
            event_type: Type of activity event
            timestamp: When the event occurred (defaults to now)
            details: Additional event details (e.g., key pressed, mouse position)
        """
        self.event_type = event_type
        self.timestamp = timestamp or datetime.now()
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ActivityData':
        """Create ActivityData from dictionary"""
        return cls(
            event_type=data['event_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            details=data.get('details', {})
        )
    
    def __repr__(self) -> str:
        return f"ActivityData(type={self.event_type}, time={self.timestamp.strftime('%H:%M:%S')})"

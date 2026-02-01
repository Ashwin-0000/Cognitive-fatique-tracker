"""Session model for tracking work sessions"""
from datetime import datetime, timedelta
from typing import Optional, List


class Session:
    """Represents a work session with breaks"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None
    ):
        """
        Initialize a new session.

        Args:
            session_id: Unique session identifier
            start_time: When the session started (defaults to now)
        """
        self.session_id = session_id or self._generate_session_id()
        self.start_time = start_time or datetime.now()
        self.end_time: Optional[datetime] = None
        self.breaks: List[dict] = []  # List of {start, end, duration}
        self.is_active = True
        self.total_activity_count = 0
        self.keyboard_count = 0
        self.mouse_click_count = 0

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def add_break(
            self,
            start_time: datetime,
            end_time: Optional[datetime] = None):
        """Add a break to the session"""
        break_data = {'start': start_time, 'end': end_time, 'duration': (
            end_time - start_time).total_seconds() if end_time else None}
        self.breaks.append(break_data)

    def end_session(self, end_time: Optional[datetime] = None):
        """End the current session"""
        self.end_time = end_time or datetime.now()
        self.is_active = False

    def get_duration(self) -> timedelta:
        """Get total session duration"""
        end = self.end_time or datetime.now()
        return end - self.start_time

    def get_work_duration(self) -> timedelta:
        """Get work duration excluding breaks"""
        total_duration = self.get_duration()
        break_duration = sum(
            (b['duration'] or 0) for b in self.breaks if b['duration']
        )
        return total_duration - timedelta(seconds=break_duration)

    def get_stats(self) -> dict:
        """Get session statistics"""
        duration = self.get_duration()
        work_duration = self.get_work_duration()

        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_duration_minutes': duration.total_seconds() / 60,
            'work_duration_minutes': work_duration.total_seconds() / 60,
            'break_count': len(self.breaks),
            'total_activity_count': self.total_activity_count,
            'keyboard_count': self.keyboard_count,
            'mouse_click_count': self.mouse_click_count,
            'is_active': self.is_active
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'breaks': [
                {
                    'start': b['start'].isoformat(),
                    'end': b['end'].isoformat() if b['end'] else None,
                    'duration': b['duration']
                }
                for b in self.breaks
            ],
            'is_active': self.is_active,
            'total_activity_count': self.total_activity_count,
            'keyboard_count': self.keyboard_count,
            'mouse_click_count': self.mouse_click_count
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Create Session from dictionary"""
        session = cls(
            session_id=data['session_id'],
            start_time=datetime.fromisoformat(data['start_time'])
        )
        if data.get('end_time'):
            session.end_time = datetime.fromisoformat(data['end_time'])
        session.is_active = data.get('is_active', True)
        session.total_activity_count = data.get('total_activity_count', 0)
        session.keyboard_count = data.get('keyboard_count', 0)
        session.mouse_click_count = data.get('mouse_click_count', 0)

        for b in data.get('breaks', []):
            session.breaks.append({
                'start': datetime.fromisoformat(b['start']),
                'end': datetime.fromisoformat(b['end']) if b['end'] else None,
                'duration': b['duration']
            })

        return session

    def __repr__(self) -> str:
        duration = self.get_duration()
        return f"Session(id={self.session_id}, duration={duration.total_seconds()/60:.1f}min)"

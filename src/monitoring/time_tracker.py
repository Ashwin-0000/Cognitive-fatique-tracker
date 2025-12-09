"""Time tracker for work sessions and breaks"""
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable
from src.models.session import Session
from src.utils.logger import default_logger as logger


class TimeTracker:
    """Tracks work time and manages break intervals"""
    
    def __init__(
        self,
        work_interval_minutes: int = 50,
        break_interval_minutes: int = 10,
        on_work_complete: Optional[Callable] = None,
        on_break_complete: Optional[Callable] = None
    ):
        """
        Initialize time tracker.
        
        Args:
            work_interval_minutes: Duration of work interval
            break_interval_minutes: Duration of break interval
            on_work_complete: Callback when work interval completes
            on_break_complete: Callback when break interval completes
        """
        self.work_interval = timedelta(minutes=work_interval_minutes)
        self.break_interval = timedelta(minutes=break_interval_minutes)
        self.on_work_complete = on_work_complete
        self.on_break_complete = on_break_complete
        
        self.current_session: Optional[Session] = None
        self.is_on_break = False
        self.break_start_time: Optional[datetime] = None
        
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def start_session(self, session: Optional[Session] = None) -> Session:
        """
        Start a new work session.
        
        Args:
            session: Existing session to resume, or None to create new
        
        Returns:
            The active session
        """
        if session is None:
            session = Session()
        
        self.current_session = session
        self.is_on_break = False
        
        logger.info(f"Started session {session.session_id}")
        return session
    
    def end_session(self):
        """End the current session"""
        if self.current_session:
            self.current_session.end_session()
            logger.info(f"Ended session {self.current_session.session_id}")
            self.current_session = None
    
    def start_break(self):
        """Start a break"""
        if not self.current_session:
            logger.warning("Cannot start break without active session")
            return
        
        self.is_on_break = True
        self.break_start_time = datetime.now()
        logger.info("Started break")
    
    def end_break(self):
        """End the current break"""
        if not self.is_on_break or not self.break_start_time:
            return
        
        end_time = datetime.now()
        if self.current_session:
            self.current_session.add_break(self.break_start_time, end_time)
        
        self.is_on_break = False
        self.break_start_time = None
        logger.info("Ended break")
    
    def get_work_time(self) -> timedelta:
        """Get current work time (excluding breaks)"""
        if not self.current_session:
            return timedelta()
        return self.current_session.get_work_duration()
    
    def get_session_time(self) -> timedelta:
        """Get total session time (including breaks)"""
        if not self.current_session:
            return timedelta()
        return self.current_session.get_duration()
    
    def get_time_until_break(self) -> timedelta:
        """Get time remaining until recommended break"""
        if not self.current_session or self.is_on_break:
            return timedelta()
        
        work_time = self.get_work_time()
        remaining = self.work_interval - work_time
        return max(timedelta(), remaining)
    
    def should_take_break(self) -> bool:
        """Check if it's time for a break"""
        if not self.current_session or self.is_on_break:
            return False
        
        return self.get_work_time() >= self.work_interval
    
    def get_break_time_remaining(self) -> timedelta:
        """Get remaining break time"""
        if not self.is_on_break or not self.break_start_time:
            return timedelta()
        
        elapsed = datetime.now() - self.break_start_time
        remaining = self.break_interval - elapsed
        return max(timedelta(), remaining)
    
    def is_break_complete(self) -> bool:
        """Check if break is complete"""
        if not self.is_on_break:
            return False
        
        return self.get_break_time_remaining() == timedelta()
    
    def get_stats(self) -> dict:
        """Get current tracking statistics"""
        if not self.current_session:
            return {
                'has_session': False,
                'is_on_break': False
            }
        
        return {
            'has_session': True,
            'session_id': self.current_session.session_id,
            'is_on_break': self.is_on_break,
            'work_time_minutes': self.get_work_time().total_seconds() / 60,
            'session_time_minutes': self.get_session_time().total_seconds() / 60,
            'time_until_break_minutes': self.get_time_until_break().total_seconds() / 60,
            'should_take_break': self.should_take_break(),
            'break_count': len(self.current_session.breaks)
        }
    
    def update_intervals(self, work_minutes: int, break_minutes: int):
        """Update work and break intervals"""
        self.work_interval = timedelta(minutes=work_minutes)
        self.break_interval = timedelta(minutes=break_minutes)
        logger.info(f"Updated intervals: work={work_minutes}min, break={break_minutes}min")

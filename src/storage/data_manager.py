"""Data manager for persistent storage using SQLite"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from src.models.session import Session
from src.models.activity_data import ActivityData
from src.models.fatigue_score import FatigueScore
from src.utils.logger import default_logger as logger


class DataManager:
    """Manages data persistence using SQLite database"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize data manager.
        
        Args:
            db_path: Path to database file
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "fatigue_tracker.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                breaks TEXT,
                is_active INTEGER,
                total_activity_count INTEGER
            )
        """)
        
        # Activity data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Fatigue scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fatigue_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                score REAL NOT NULL,
                timestamp TEXT NOT NULL,
                factors TEXT,
                level TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Create indices for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activities_timestamp 
            ON activities(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fatigue_timestamp 
            ON fatigue_scores(timestamp)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    # Session operations
    def save_session(self, session: Session):
        """Save or update a session"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = session.to_dict()
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (session_id, start_time, end_time, breaks, is_active, total_activity_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['session_id'],
            data['start_time'],
            data['end_time'],
            json.dumps(data['breaks']),
            1 if data['is_active'] else 0,
            data['total_activity_count']
        ))
        
        conn.commit()
        conn.close()
        logger.debug(f"Saved session {session.session_id}")
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = {
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'breaks': json.loads(row['breaks']),
                'is_active': bool(row['is_active']),
                'total_activity_count': row['total_activity_count']
            }
            return Session.from_dict(data)
        return None
    
    def get_active_session(self) -> Optional[Session]:
        """Get the currently active session"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE is_active = 1 ORDER BY start_time DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = {
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'breaks': json.loads(row['breaks']),
                'is_active': bool(row['is_active']),
                'total_activity_count': row['total_activity_count']
            }
            return Session.from_dict(data)
        return None
    
    def get_recent_sessions(self, days: int = 7) -> List[Session]:
        """Get recent sessions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute(
            "SELECT * FROM sessions WHERE start_time >= ? ORDER BY start_time DESC",
            (cutoff,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            data = {
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'breaks': json.loads(row['breaks']),
                'is_active': bool(row['is_active']),
                'total_activity_count': row['total_activity_count']
            }
            sessions.append(Session.from_dict(data))
        
        return sessions
    
    # Activity operations
    def save_activity(self, activity: ActivityData, session_id: Optional[str] = None):
        """Save an activity event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = activity.to_dict()
        cursor.execute("""
            INSERT INTO activities (session_id, event_type, timestamp, details)
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            data['event_type'],
            data['timestamp'],
            json.dumps(data['details'])
        ))
        
        conn.commit()
        conn.close()
    
    def get_activities(self, session_id: str, limit: int = 1000) -> List[ActivityData]:
        """Get activities for a session"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM activities WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            data = {
                'event_type': row['event_type'],
                'timestamp': row['timestamp'],
                'details': json.loads(row['details'])
            }
            activities.append(ActivityData.from_dict(data))
        
        return activities
    
    # Fatigue score operations
    def save_fatigue_score(self, score: FatigueScore, session_id: Optional[str] = None):
        """Save a fatigue score"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = score.to_dict()
        cursor.execute("""
            INSERT INTO fatigue_scores (session_id, score, timestamp, factors, level)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            data['score'],
            data['timestamp'],
            json.dumps(data['factors']),
            data['level']
        ))
        
        conn.commit()
        conn.close()
    
    def get_fatigue_scores(self, session_id: str, limit: int = 1000) -> List[FatigueScore]:
        """Get fatigue scores for a session"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM fatigue_scores WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        scores = []
        for row in rows:
            data = {
                'score': row['score'],
                'timestamp': row['timestamp'],
                'factors': json.loads(row['factors'])
            }
            scores.append(FatigueScore.from_dict(data))
        
        return scores
    
    def get_recent_fatigue_scores(self, minutes: int = 60) -> List[FatigueScore]:
        """Get recent fatigue scores across all sessions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        cursor.execute(
            "SELECT * FROM fatigue_scores WHERE timestamp >= ? ORDER BY timestamp ASC",
            (cutoff,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        scores = []
        for row in rows:
            data = {
                'score': row['score'],
                'timestamp': row['timestamp'],
                'factors': json.loads(row['factors'])
            }
            scores.append(FatigueScore.from_dict(data))
        
        return scores
    
    # Cleanup operations
    def cleanup_old_data(self, days: int = 30):
        """Remove data older than specified days"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("DELETE FROM activities WHERE timestamp < ?", (cutoff,))
        cursor.execute("DELETE FROM fatigue_scores WHERE timestamp < ?", (cutoff,))
        cursor.execute("DELETE FROM sessions WHERE start_time < ?", (cutoff,))
        
        conn.commit()
        conn.close()
        logger.info(f"Cleaned up data older than {days} days")

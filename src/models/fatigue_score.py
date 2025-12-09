"""Fatigue score model for tracking cognitive fatigue levels"""
from datetime import datetime
from typing import Optional, List


class FatigueScore:
    """Represents a fatigue score measurement"""
    
    # Threshold definitions
    LOW_THRESHOLD = 30
    MEDIUM_THRESHOLD = 60
    HIGH_THRESHOLD = 80
    
    def __init__(
        self,
        score: float = 0.0,
        timestamp: Optional[datetime] = None,
        factors: Optional[dict] = None
    ):
        """
        Initialize a fatigue score.
        
        Args:
            score: Fatigue score (0-100, where 100 is maximum fatigue)
            timestamp: When the score was calculated
            factors: Contributing factors to the score
        """
        self.score = max(0.0, min(100.0, score))  # Clamp between 0-100
        self.timestamp = timestamp or datetime.now()
        self.factors = factors or {}
    
    def get_level(self) -> str:
        """Get fatigue level as a string"""
        if self.score < self.LOW_THRESHOLD:
            return "Low"
        elif self.score < self.MEDIUM_THRESHOLD:
            return "Moderate"
        elif self.score < self.HIGH_THRESHOLD:
            return "High"
        else:
            return "Critical"
    
    def get_color(self) -> str:
        """Get color representation for UI"""
        if self.score < self.LOW_THRESHOLD:
            return "#4CAF50"  # Green
        elif self.score < self.MEDIUM_THRESHOLD:
            return "#FFC107"  # Yellow
        elif self.score < self.HIGH_THRESHOLD:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red
    
    def needs_break(self) -> bool:
        """Check if user needs a break"""
        return self.score >= self.MEDIUM_THRESHOLD
    
    def is_critical(self) -> bool:
        """Check if fatigue is at critical level"""
        return self.score >= self.HIGH_THRESHOLD
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'score': self.score,
            'timestamp': self.timestamp.isoformat(),
            'factors': self.factors,
            'level': self.get_level()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FatigueScore':
        """Create FatigueScore from dictionary"""
        return cls(
            score=data['score'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            factors=data.get('factors', {})
        )
    
    def __repr__(self) -> str:
        return f"FatigueScore(score={self.score:.1f}, level={self.get_level()})"


class FatigueHistory:
    """Manages historical fatigue scores"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize fatigue history.
        
        Args:
            max_history: Maximum number of scores to keep in memory
        """
        self.scores: List[FatigueScore] = []
        self.max_history = max_history
    
    def add_score(self, score: FatigueScore):
        """Add a new score to history"""
        self.scores.append(score)
        # Keep only the most recent scores
        if len(self.scores) > self.max_history:
            self.scores = self.scores[-self.max_history:]
    
    def get_latest(self) -> Optional[FatigueScore]:
        """Get the most recent score"""
        return self.scores[-1] if self.scores else None
    
    def get_average(self, minutes: int = 60) -> float:
        """Get average score over the last N minutes"""
        if not self.scores:
            return 0.0
        
        now = datetime.now()
        recent_scores = [
            s.score for s in self.scores
            if (now - s.timestamp).total_seconds() <= minutes * 60
        ]
        
        return sum(recent_scores) / len(recent_scores) if recent_scores else 0.0
    
    def get_trend(self) -> str:
        """Get trend direction (increasing, decreasing, stable)"""
        if len(self.scores) < 5:
            return "stable"
        
        recent_5 = [s.score for s in self.scores[-5:]]
        first_avg = sum(recent_5[:2]) / 2
        last_avg = sum(recent_5[-2:]) / 2
        
        diff = last_avg - first_avg
        
        if diff > 5:
            return "increasing"
        elif diff < -5:
            return "decreasing"
        else:
            return "stable"
    
    def clear(self):
        """Clear history"""
        self.scores.clear()
    
    def __len__(self) -> int:
        return len(self.scores)

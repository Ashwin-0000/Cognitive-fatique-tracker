"""Eye data model for tracking blink rate and eye metrics"""
from datetime import datetime
from typing import Optional


class EyeData:
    """Represents eye tracking metrics at a point in time"""
    
    def __init__(
        self,
        blink_rate: float = 0.0,
        total_blinks: int = 0,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize eye data.
        
        Args:
            blink_rate: Blinks per minute
            total_blinks: Total blinks in session
            timestamp: When the data was captured
        """
        self.blink_rate = blink_rate
        self.total_blinks = total_blinks
        self.timestamp = timestamp or datetime.now()
    
    def is_normal(self) -> bool:
        """Check if blink rate is in normal range (15-20 bpm)"""
        return 15 <= self.blink_rate <= 20
    
    def is_low(self) -> bool:
        """Check if blink rate is low (< 15 bpm)"""
        return self.blink_rate < 15
    
    def is_critical(self) -> bool:
        """Check if blink rate is critically low (< 10 bpm)"""
        return self.blink_rate < 10
    
    def get_status(self) -> str:
        """Get status description"""
        if self.blink_rate >= 15:
            return "Normal"
        elif self.blink_rate >= 10:
            return "Low"
        else:
            return "Critical"
    
    def get_color(self) -> str:
        """Get color representation for UI"""
        if self.blink_rate >= 15:
            return "#4CAF50"  # Green
        elif self.blink_rate >= 10:
            return "#FFC107"  # Yellow
        else:
            return "#F44336"  # Red
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'blink_rate': self.blink_rate,
            'total_blinks': self.total_blinks,
            'timestamp': self.timestamp.isoformat(),
            'status': self.get_status()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EyeData':
        """Create EyeData from dictionary"""
        return cls(
            blink_rate=data['blink_rate'],
            total_blinks=data['total_blinks'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
    
    def __repr__(self) -> str:
        return f"EyeData(rate={self.blink_rate:.1f} bpm, status={self.get_status()})"

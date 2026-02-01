"""Unit tests for models"""
import unittest
from datetime import datetime, timedelta
from src.models.session import Session
from src.models.activity_data import ActivityData
from src.models.fatigue_score import FatigueScore, FatigueHistory


class TestSession(unittest.TestCase):
    """Test Session model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.session = Session()
    
    def test_session_initialization(self):
        """Test session is initialized correctly"""
        self.assertIsNotNone(self.session.session_id)
        self.assertIsNotNone(self.session.start_time)
        self.assertIsNone(self.session.end_time)
        self.assertEqual(self.session.total_activity_count, 0)
        self.assertEqual(self.session.break_count, 0)
    
    def test_session_duration(self):
        """Test session duration calculation"""
        self.session.end_session()
        stats = self.session.get_stats()
        self.assertGreater(stats['total_duration_minutes'], 0)
    
    def test_break_tracking(self):
        """Test break tracking"""
        initial_count = self.session.break_count
        self.session.total_break_duration = timedelta(minutes=10)
        self.session.break_count = 2
        
        self.assertEqual(self.session.break_count, initial_count + 2)


class TestActivityData(unittest.TestCase):
    """Test ActivityData model"""
    
    def test_activity_creation(self):
        """Test activity data creation"""
        activity = ActivityData(
            activity_type='keyboard',
            timestamp=datetime.now()
        )
        self.assertEqual(activity.activity_type, 'keyboard')
        self.assertIsNotNone(activity.timestamp)
    
    def test_activity_serialization(self):
        """Test to_dict and from_dict"""
        activity = ActivityData(
            activity_type='mouse_click',
            timestamp=datetime.now(),
            details={'button': 'left'}
        )
        
        data = activity.to_dict()
        restored = ActivityData.from_dict(data)
        
        self.assertEqual(activity.activity_type, restored.activity_type)
        self.assertEqual(activity.details, restored.details)


class TestFatigueScore(unittest.TestCase):
    """Test FatigueScore model"""
    
    def test_fatigue_levels(self):
        """Test fatigue level classification"""
        low_score = FatigueScore(score=20.0)
        self.assertEqual(low_score.get_level(), 'Low')
        
        moderate_score = FatigueScore(score=50.0)
        self.assertEqual(moderate_score.get_level(), 'Moderate')
        
        high_score = FatigueScore(score=75.0)
        self.assertEqual(high_score.get_level(), 'High')
        
        critical_score = FatigueScore(score=90.0)
        self.assertEqual(critical_score.get_level(), 'Critical')
    
    def test_fatigue_colors(self):
        """Test color coding"""
        score = FatigueScore(score=20.0)
        color = score.get_color()
        self.assertIsNotNone(color)
    
    def test_fatigue_history(self):
        """Test fatigue history tracking"""
        history = FatigueHistory()
        
        score1 = FatigueScore(score=30.0)
        score2 = FatigueScore(score=50.0)
        
        history.add_score(score1)
        history.add_score(score2)
        
        self.assertEqual(len(history.scores), 2)
        self.assertEqual(history.get_average(), 40.0)
        self.assertEqual(history.get_trend(), 'increasing')


if __name__ == '__main__':
    unittest.main()

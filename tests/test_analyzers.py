"""Unit tests for analyzers"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.analysis.fatigue_analyzer import FatigueAnalyzer
from src.analysis.alert_manager import AlertManager
from src.analysis.achievement_manager import AchievementManager
from src.analysis.statistics_analyzer import StatisticsAnalyzer


class TestFatigueAnalyzer(unittest.TestCase):
    """Test FatigueAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = FatigueAnalyzer(use_ml=False)
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertFalse(self.analyzer.use_ml)
    
    def test_score_calculation(self):
        """Test fatigue score calculation"""
        self.analyzer.start_session()
        
        score = self.analyzer.calculate_score(
            work_duration_minutes=30,
            activity_rate=15.0,
            time_since_break_minutes=30,
            is_on_break=False,
            blink_rate=15.0
        )
        
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score.score, 0)
        self.assertLessEqual(score.score, 100)
    
    def test_session_management(self):
        """Test session start/end"""
        self.analyzer.start_session()
        self.assertIsNotNone(self.analyzer.session_start_time)
        
        self.analyzer.reset()
        self.assertIsNone(self.analyzer.session_start_time)


class TestAlertManager(unittest.TestCase):
    """Test AlertManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.callback_called = False
        
        def alert_callback(title, message):
            self.callback_called = True
        
        self.alert_manager = AlertManager(on_alert=alert_callback)
    
    def test_alert_cooldown(self):
        """Test alert cooldown mechanism"""
        from src.models.fatigue_score import FatigueScore
        
        # First alert should trigger
        score = FatigueScore(score=90.0)
        self.alert_manager.check_fatigue_level(score)
        self.assertTrue(self.callback_called)
        
        # Reset flag
        self.callback_called = False
        
        # Second alert should not trigger (cooldown)
        self.alert_manager.check_fatigue_level(score)
        self.assertFalse(self.callback_called)


class TestAchievementManager(unittest.TestCase):
    """Test AchievementManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.achievement_manager = AchievementManager()
    
    def test_achievement_unlocking(self):
        """Test achievement unlocking"""
        unlocked = self.achievement_manager.update_progress('first_session', 1)
        self.assertIsNotNone(unlocked)
        self.assertTrue(unlocked.unlocked)
    
    def test_achievement_progress(self):
        """Test progress tracking"""
        self.achievement_manager.update_progress('break_master', 25)
        
        achievements = self.achievement_manager.get_all_achievements()
        break_master = next(a for a in achievements if a.id == 'break_master')
        
        self.assertEqual(break_master.progress, 25)
        self.assertFalse(break_master.unlocked)


if __name__ == '__main__':
    unittest.main()

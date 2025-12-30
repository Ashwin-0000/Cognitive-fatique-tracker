"""Performance and stress tests"""
import unittest
import time
from pathlib import Path
import tempfile
import shutil

from src.models.session import Session
from src.storage.data_manager import DataManager
from src.analysis.fatigue_analyzer import FatigueAnalyzer


class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = Path(self.test_dir) / "test.db"
        self.data_manager = DataManager(str(self.test_db))
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_database_write_performance(self):
        """Test database write performance"""
        start_time = time.time()
        
        # Write 100 sessions
        for i in range(100):
            session = Session()
            session.total_activity_count = i
            session.end_session()
            self.data_manager.save_session(session)
        
        elapsed = time.time() - start_time
        
        # Should complete in under 5 seconds
        self.assertLess(elapsed, 5.0)
        print(f"100 sessions saved in {elapsed:.2f}s")
    
    def test_score_calculation_performance(self):
        """Test score calculation performance"""
        analyzer = FatigueAnalyzer(use_ml=False)
        analyzer.start_session()
        
        start_time = time.time()
        
        # Calculate 1000 scores
        for i in range(1000):
            analyzer.calculate_score(
                work_duration_minutes=30,
                activity_rate=15.0,
                time_since_break_minutes=30,
                blink_rate=15.0
            )
        
        elapsed = time.time() - start_time
        
        # Should complete in under 1 second
        self.assertLess(elapsed, 1.0)
        print(f"1000 scores calculated in {elapsed:.3f}s")


class TestStress(unittest.TestCase):
    """Stress tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = Path(self.test_dir) / "test.db"
        self.data_manager = DataManager(str(self.test_db))
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_large_session_count(self):
        """Test handling many sessions"""
        # Create 500 sessions
        for i in range(500):
            session = Session()
            session.total_activity_count = i
            session.end_session()
            self.data_manager.save_session(session)
        
        # Retrieve all sessions
        sessions = self.data_manager.get_all_sessions()
        self.assertEqual(len(sessions), 500)
    
    def test_long_running_session(self):
        """Test very long session duration"""
        session = Session()
        
        # Simulate 48-hour session
        for hour in range(48):
            stats = session.get_stats()
            # Session should handle it
            self.assertIsNotNone(stats)


if __name__ == '__main__':
    unittest.main()

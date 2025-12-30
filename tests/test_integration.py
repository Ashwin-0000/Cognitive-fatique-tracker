"""Integration tests for complete workflows"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from src.models.session import Session
from src.storage.data_manager import DataManager
from src.analysis.fatigue_analyzer import FatigueAnalyzer
from src.analysis.statistics_analyzer import StatisticsAnalyzer


class TestCompleteWorkflow(unittest.TestCase):
    """Test complete application workflows"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db = Path(self.test_dir) / "test.db"
        
        self.data_manager = DataManager(str(self.test_db))
        self.analyzer = FatigueAnalyzer(use_ml=False)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_session_workflow(self):
        """Test complete session workflow"""
        # Start session
        session = Session()
        self.analyzer.start_session()
        
        # Simulate some activity
        for i in range(10):
            score = self.analyzer.calculate_score(
                work_duration_minutes=i * 5,
                activity_rate=15.0,
                time_since_break_minutes=i * 5,
                blink_rate=15.0
            )
            self.assertIsNotNone(score)
        
        # End session
        session.end_session()
        
        # Verify session data
        stats = session.get_stats()
        self.assertGreater(stats['total_duration_minutes'], 0)
    
    def test_data_persistence(self):
        """Test data saving and loading"""
        # Create and save session
        session = Session()
        session.total_activity_count = 100
        self.data_manager.save_session(session)
        
        # Load sessions
        sessions = self.data_manager.get_all_sessions()
        self.assertGreater(len(sessions), 0)
        
        # Verify data
        loaded = sessions[0]
        self.assertEqual(loaded.session_id, session.session_id)
    
    def test_statistics_calculation(self):
        """Test statistics calculation workflow"""
        # Create test sessions
        for i in range(5):
            session = Session()
            session.total_activity_count = 50 + i * 10
            session.end_session()
            self.data_manager.save_session(session)
        
        # Calculate statistics
        stats_analyzer = StatisticsAnalyzer(self.data_manager)
        weekly = stats_analyzer.get_weekly_stats()
        
        self.assertGreater(weekly['total_sessions'], 0)


class TestExportWorkflow(unittest.TestCase):
    """Test export workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = Path(self.test_dir) / "test.db"
        self.data_manager = DataManager(str(self.test_db))
        
        # Create test session
        session = Session()
        session.end_session()
        self.data_manager.save_session(session)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_csv_export(self):
        """Test CSV export"""
        from src.export.csv_exporter import CSVExporter
        
        exporter = CSVExporter(self.data_manager)
        output_file = Path(self.test_dir) / "test.csv"
        
        success = exporter.export_sessions(output_file)
        self.assertTrue(success)
        self.assertTrue(output_file.exists())


if __name__ == '__main__':
    unittest.main()

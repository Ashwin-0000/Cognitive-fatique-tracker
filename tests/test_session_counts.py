
import unittest
from datetime import datetime
from src.models.session import Session

class TestSessionCounts(unittest.TestCase):
    def test_session_initialization(self):
        session = Session()
        self.assertEqual(session.keyboard_count, 0)
        self.assertEqual(session.mouse_click_count, 0)
        self.assertEqual(session.total_activity_count, 0)

    def test_count_increments(self):
        session = Session()
        
        # Simulate activity
        session.keyboard_count += 5
        session.mouse_click_count += 3
        session.total_activity_count += 8
        
        stats = session.get_stats()
        self.assertEqual(stats['keyboard_count'], 5)
        self.assertEqual(stats['mouse_click_count'], 3)
        self.assertEqual(stats['total_activity_count'], 8)

    def test_serialization(self):
        session = Session()
        session.keyboard_count = 10
        session.mouse_click_count = 20
        session.total_activity_count = 30
        
        data = session.to_dict()
        self.assertEqual(data['keyboard_count'], 10)
        self.assertEqual(data['mouse_click_count'], 20)
        
        # Deserialize
        new_session = Session.from_dict(data)
        self.assertEqual(new_session.keyboard_count, 10)
        self.assertEqual(new_session.mouse_click_count, 20)
        self.assertEqual(new_session.total_activity_count, 30)

if __name__ == '__main__':
    unittest.main()

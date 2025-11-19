import unittest
from datetime import datetime, timedelta
from services.countdown_service import CountdownEvent

class TestCountdownService(unittest.TestCase):
    def test_yearly_countdown(self):
        today = datetime(2025, 11, 19)
        event = CountdownEvent(name="Christmas", date="2025-12-24", yearly=True, email="test@example.com")
        msg = event.get_countdown_message(today)
        self.assertIn("Days to Christmas", msg)
        self.assertTrue(int(msg.split(':')[-1].strip()) > 0)

    def test_one_time_countdown(self):
        today = datetime(2025, 11, 19)
        event = CountdownEvent(name="Wedding", date="2025-12-01", yearly=False, email="test@example.com", message_after="Married for: {days}")
        msg_before = event.get_countdown_message(today)
        self.assertIn("Days to Wedding", msg_before)
        after = datetime(2025, 12, 2)
        msg_after = event.get_countdown_message(after)
        self.assertIn("Married for:", msg_after)

    def test_disable_after_event(self):
        today = datetime(2025, 12, 2)
        event = CountdownEvent(name="Wedding", date="2025-12-01", yearly=False, email="test@example.com")
        msg = event.get_countdown_message(today)
        self.assertIsNone(msg)

if __name__ == "__main__":
    unittest.main()

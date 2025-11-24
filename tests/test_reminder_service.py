import pytest
from services.reminder_service import list_reminders, run_due_reminders_job

def test_list_reminders():
    # Should not raise
    list_reminders()

def test_run_due_reminders_job():
    class DummyConfig:
        pass
    run_due_reminders_job(DummyConfig(), dry_run=True)

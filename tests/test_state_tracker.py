"""Tests for state_tracker module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from state_tracker import StateTracker, _TASK_STATES


@pytest.fixture(autouse=True)
def clean_state():
    """Clear global state between tests."""
    _TASK_STATES.clear()
    yield
    _TASK_STATES.clear()


class TestStateTracker:
    def test_get_or_create(self):
        state = StateTracker.get_or_create("task1")
        assert state.task_id == "task1"
        # Second call returns same instance
        state2 = StateTracker.get_or_create("task1")
        assert state is state2

    def test_record_action(self):
        StateTracker.record_action("t1", "ClickAction", "#btn", "http://localhost:8000", 0)
        state = StateTracker.get_or_create("t1")
        assert len(state.history) == 1
        assert state.history[0].action_type == "ClickAction"

    def test_filled_fields(self):
        StateTracker.record_filled_field("t1", "username")
        StateTracker.record_filled_field("t1", "password")
        fields = StateTracker.get_filled_fields("t1")
        assert "username" in fields
        assert "password" in fields

    def test_login_tracking(self):
        assert StateTracker.is_login_done("t1") is False
        StateTracker.mark_login_done("t1")
        assert StateTracker.is_login_done("t1") is True

    def test_memory_persistence(self):
        StateTracker.update_memory("t1", "logged in", "search for item")
        mem, goal = StateTracker.get_memory("t1")
        assert mem == "logged in"
        assert goal == "search for item"

    def test_memory_nonexistent_task(self):
        mem, goal = StateTracker.get_memory("nonexistent")
        assert mem == ""
        assert goal == ""


class TestLoopDetection:
    def test_no_loop_with_few_actions(self):
        StateTracker.record_action("t1", "ClickAction", "#btn", "http://localhost:8000", 0)
        result = StateTracker.detect_loop("t1", "http://localhost:8000")
        assert result is None

    def test_detects_loop(self):
        url = "http://localhost:8000"
        StateTracker.record_action("t1", "ClickAction", "#btn", url, 0)
        StateTracker.record_action("t1", "ClickAction", "#btn", url, 1)
        result = StateTracker.detect_loop("t1", url)
        assert result is not None
        assert "LOOP DETECTED" in result

    def test_no_loop_for_scroll(self):
        url = "http://localhost:8000"
        StateTracker.record_action("t1", "ScrollAction", "", url, 0)
        StateTracker.record_action("t1", "ScrollAction", "", url, 1)
        result = StateTracker.detect_loop("t1", url)
        assert result is None


class TestStuckDetection:
    def test_not_stuck_with_few_actions(self):
        StateTracker.record_action("t1", "ClickAction", "#a", "http://localhost:8000", 0)
        result = StateTracker.detect_stuck("t1", "http://localhost:8000")
        assert result is None

    def test_detects_stuck(self):
        url = "http://localhost:8000"
        StateTracker.record_action("t1", "ClickAction", "#a", url, 0)
        StateTracker.record_action("t1", "ClickAction", "#a", url, 1)
        StateTracker.record_action("t1", "ClickAction", "#b", url, 2)
        result = StateTracker.detect_stuck("t1", url)
        assert result is not None
        assert "STUCK" in result

    def test_not_stuck_with_url_changes(self):
        StateTracker.record_action("t1", "ClickAction", "#a", "http://localhost:8000/p1", 0)
        StateTracker.record_action("t1", "ClickAction", "#a", "http://localhost:8000/p2", 1)
        StateTracker.record_action("t1", "ClickAction", "#a", "http://localhost:8000/p3", 2)
        result = StateTracker.detect_stuck("t1", "http://localhost:8000/p3")
        assert result is None


class TestRepeatDetection:
    def test_no_repeat_initially(self):
        assert StateTracker.get_repeat_count("t1") == 0

    def test_counts_repeats(self):
        url = "http://localhost:8000"
        StateTracker.get_or_create("t1").prev_url = url
        StateTracker.update_action_sig("t1", url, "click:0")
        assert StateTracker.get_repeat_count("t1") == 0
        StateTracker.update_action_sig("t1", url, "click:0")
        assert StateTracker.get_repeat_count("t1") == 1
        StateTracker.update_action_sig("t1", url, "click:0")
        assert StateTracker.get_repeat_count("t1") == 2

    def test_resets_on_different_action(self):
        url = "http://localhost:8000"
        StateTracker.get_or_create("t1").prev_url = url
        StateTracker.update_action_sig("t1", url, "click:0")
        StateTracker.update_action_sig("t1", url, "click:0")
        assert StateTracker.get_repeat_count("t1") == 1
        StateTracker.update_action_sig("t1", url, "click:1")
        assert StateTracker.get_repeat_count("t1") == 0


class TestAutoCleanup:
    def test_cleanup_oldest(self):
        for i in range(10):
            StateTracker.get_or_create(f"task_{i}")
        StateTracker.auto_cleanup(max_kept=5)
        assert len(_TASK_STATES) == 5

    def test_cleanup_specific(self):
        StateTracker.get_or_create("t1")
        assert "t1" in _TASK_STATES
        StateTracker.cleanup("t1")
        assert "t1" not in _TASK_STATES

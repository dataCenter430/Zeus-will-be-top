"""Tests for metrics module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from metrics import AgentMetrics


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton between tests."""
    AgentMetrics._instance = None
    yield
    AgentMetrics._instance = None


class TestAgentMetrics:
    def test_singleton(self):
        m1 = AgentMetrics()
        m2 = AgentMetrics()
        assert m1 is m2

    def test_record_resolution(self):
        m = AgentMetrics()
        m.record_resolution("kb_lookup", "autocinema", "FILM_DETAIL", 5.0)
        assert m.stage_counts["kb_lookup"] == 1
        assert m.website_counts["autocinema"] == 1
        assert m.task_type_counts["FILM_DETAIL"] == 1
        assert m.total_steps == 1

    def test_record_new_task(self):
        m = AgentMetrics()
        m.record_new_task()
        m.record_new_task()
        assert m.total_tasks == 2

    def test_record_kb_hit(self):
        m = AgentMetrics()
        m.record_kb_hit()
        assert m.knowledge_base_hits == 1

    def test_record_llm_usage(self):
        m = AgentMetrics()
        m.record_llm_usage(0.001, 5)
        assert m.total_llm_cost == 0.001
        assert m.total_llm_calls == 5

    def test_record_auto_learn(self):
        m = AgentMetrics()
        m.record_auto_learn()
        assert m.auto_learned_tasks == 1

    def test_set_kb_size(self):
        m = AgentMetrics()
        m.set_kb_size(65)
        assert m.knowledge_base_size == 65

    def test_snapshot(self):
        m = AgentMetrics()
        m.record_new_task()
        m.record_resolution("llm_decision", "autobooks", "SEARCH_BOOK", 150.0)
        m.record_llm_usage(0.0005, 2)
        m.set_kb_size(65)

        snap = m.snapshot()
        assert snap["total_tasks"] == 1
        assert snap["total_steps"] == 1
        assert snap["knowledge_base"]["size"] == 65
        assert snap["stage_resolution"]["llm_decision"] == 1
        assert snap["stage_percentages"]["llm_decision"] == 100.0
        assert snap["llm"]["total_calls"] == 2
        assert snap["llm"]["total_cost_usd"] == 0.0005
        assert "uptime_seconds" in snap

    def test_snapshot_empty(self):
        m = AgentMetrics()
        snap = m.snapshot()
        assert snap["total_tasks"] == 0
        assert snap["total_steps"] == 0

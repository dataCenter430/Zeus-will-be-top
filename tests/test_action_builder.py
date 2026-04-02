"""Tests for action_builder module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from action_builder import parse_llm_response, build_iwa_action, WAIT_ACTION
from models import Candidate, Selector


def _make_candidate(index: int, tag: str = "button", text: str = "Click me", **kwargs) -> Candidate:
    return Candidate(
        index=index,
        tag=tag,
        text=text,
        selector=Selector(type="css", value=f"#btn-{index}"),
        **kwargs,
    )


class TestParseLlmResponse:
    def test_valid_json(self):
        result = parse_llm_response('{"action": "click", "candidate_id": 0}')
        assert result == {"action": "click", "candidate_id": 0}

    def test_markdown_fenced(self):
        result = parse_llm_response('```json\n{"action": "click"}\n```')
        assert result == {"action": "click"}

    def test_brace_extraction(self):
        result = parse_llm_response('Here is the answer: {"action": "done"} end')
        assert result == {"action": "done"}

    def test_invalid_json(self):
        result = parse_llm_response("This is not JSON at all")
        assert result is None

    def test_empty_string(self):
        result = parse_llm_response("")
        assert result is None


class TestBuildIwaAction:
    def setup_method(self):
        self.candidates = [
            _make_candidate(0, "button", "Submit"),
            _make_candidate(1, "input", "Search", input_type="text", name="query"),
            _make_candidate(2, "select", "Category", options=["Action", "Comedy"]),
        ]
        self.url = "http://localhost:8000/?seed=123"
        self.seed = "123"

    def test_click_action(self):
        decision = {"action": "click", "candidate_id": 0}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "ClickAction"
        assert result["selector"]["value"] == "#btn-0"

    def test_type_action(self):
        decision = {"action": "type", "candidate_id": 1, "text": "hello"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "TypeAction"
        assert result["text"] == "hello"

    def test_select_option(self):
        decision = {"action": "select_option", "candidate_id": 2, "text": "Comedy"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "SelectDropDownOptionAction"
        assert result["text"] == "Comedy"

    def test_select_option_default_first(self):
        decision = {"action": "select_option", "candidate_id": 2}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "SelectDropDownOptionAction"
        assert result["text"] == "Action"  # first option

    def test_navigate_action(self):
        decision = {"action": "navigate", "url": "http://localhost:8000/page2"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "NavigateAction"
        assert "seed=123" in result["url"]

    def test_navigate_blocks_external(self):
        decision = {"action": "navigate", "url": "http://evil.com/steal"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result == WAIT_ACTION

    def test_scroll_down(self):
        decision = {"action": "scroll", "direction": "down"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "ScrollAction"
        assert result.get("down") is True

    def test_scroll_up(self):
        decision = {"action": "scroll", "direction": "up"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "ScrollAction"
        assert result.get("up") is True

    def test_done_action(self):
        decision = {"action": "done"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "IdleAction"

    def test_invalid_candidate_id(self):
        decision = {"action": "click", "candidate_id": 999}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result == WAIT_ACTION

    def test_missing_candidate_id(self):
        decision = {"action": "click"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result == WAIT_ACTION

    def test_unknown_action(self):
        decision = {"action": "fly_to_moon"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result == WAIT_ACTION

    def test_same_page_navigate_becomes_scroll(self):
        decision = {"action": "navigate", "url": "http://localhost:8000/?seed=123"}
        result = build_iwa_action(decision, self.candidates, self.url, self.seed)
        assert result["type"] == "ScrollAction"

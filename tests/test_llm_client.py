"""Tests for llm_client module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from llm_client import LLMClient, _get_cost_rates


class TestCostRates:
    def test_gpt4o_mini(self):
        p, c = _get_cost_rates("gpt-4o-mini")
        assert p == 0.15
        assert c == 0.60

    def test_claude_haiku(self):
        p, c = _get_cost_rates("claude-haiku-4-5-20251001")
        assert p == 0.25
        assert c == 1.25

    def test_claude_sonnet(self):
        p, c = _get_cost_rates("claude-sonnet-4-6")
        assert p == 3.00
        assert c == 15.00

    def test_unknown_model_fallback(self):
        p, c = _get_cost_rates("some-unknown-model")
        assert p == 0.15
        assert c == 0.60


class TestLLMClientInit:
    def test_default_openai_provider(self, monkeypatch):
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        client = LLMClient()
        assert client.provider == "openai"
        assert client.model == "gpt-4o-mini"
        assert client.total_cost == 0.0
        assert client.total_calls == 0

    def test_anthropic_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        client = LLMClient()
        assert client.provider == "anthropic"
        assert "claude" in client.model
        assert client.api_key == "test-key"

    def test_custom_openai_model(self, monkeypatch):
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        client = LLMClient()
        assert client.model == "gpt-4o"

    def test_custom_temperature(self, monkeypatch):
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.8")
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        client = LLMClient()
        assert client.temperature == 0.8

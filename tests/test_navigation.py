"""Tests for navigation module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from navigation import extract_seed, preserve_seed, normalize_url, is_localhost_url, same_page


class TestExtractSeed:
    def test_with_seed(self):
        assert extract_seed("http://localhost:8000/?seed=123") == "123"

    def test_without_seed(self):
        assert extract_seed("http://localhost:8000/") is None

    def test_empty_url(self):
        assert extract_seed("") is None

    def test_seed_with_other_params(self):
        assert extract_seed("http://localhost:8000/?foo=bar&seed=456") == "456"


class TestPreserveSeed:
    def test_adds_seed(self):
        result = preserve_seed(
            "http://localhost:8000/page",
            "http://localhost:8000/?seed=100"
        )
        assert "seed=100" in result

    def test_no_seed_to_preserve(self):
        result = preserve_seed(
            "http://localhost:8000/page",
            "http://localhost:8000/"
        )
        assert result == "http://localhost:8000/page"

    def test_already_has_correct_seed(self):
        target = "http://localhost:8000/page?seed=100"
        result = preserve_seed(target, "http://localhost:8000/?seed=100")
        assert result == target

    def test_replaces_different_seed(self):
        result = preserve_seed(
            "http://localhost:8000/page?seed=999",
            "http://localhost:8000/?seed=100"
        )
        assert "seed=100" in result


class TestNormalizeUrl:
    def test_localhost_unchanged(self):
        url = "http://localhost:8000/page"
        assert normalize_url(url) == url

    def test_127_unchanged(self):
        url = "http://127.0.0.1:8000/page"
        assert normalize_url(url) == url

    def test_other_host_to_localhost(self):
        result = normalize_url("http://example.com:8000/page")
        assert "localhost:8000" in result


class TestIsLocalhostUrl:
    def test_localhost(self):
        assert is_localhost_url("http://localhost:8000/") is True

    def test_127(self):
        assert is_localhost_url("http://127.0.0.1:8000/") is True

    def test_external(self):
        assert is_localhost_url("http://example.com/") is False

    def test_bad_scheme(self):
        assert is_localhost_url("ftp://localhost/") is False

    def test_javascript_scheme(self):
        assert is_localhost_url("javascript:void(0)") is False


class TestSamePage:
    def test_same(self):
        assert same_page(
            "http://localhost:8000/page?seed=1",
            "http://localhost:8000/page?seed=1"
        ) is True

    def test_different_path(self):
        assert same_page(
            "http://localhost:8000/page1",
            "http://localhost:8000/page2"
        ) is False

    def test_different_query(self):
        assert same_page(
            "http://localhost:8000/page?a=1",
            "http://localhost:8000/page?a=2"
        ) is False

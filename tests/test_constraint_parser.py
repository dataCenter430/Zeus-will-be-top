"""Tests for constraint_parser module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from constraint_parser import parse_constraints, format_constraints_block, extract_credentials


class TestParseConstraints:
    def test_equals_quoted(self):
        result = parse_constraints("title equals 'The Matrix'")
        assert len(result) == 1
        assert result[0].field == "title"
        assert result[0].operator == "equals"
        assert result[0].value == "The Matrix"

    def test_equals_unquoted(self):
        result = parse_constraints("rating equals 5")
        assert len(result) == 1
        assert result[0].operator == "equals"
        assert result[0].value == "5"

    def test_not_equals(self):
        result = parse_constraints("role does not equal 'Data Scientist'")
        assert len(result) == 1
        assert result[0].operator == "not_equals"
        assert result[0].value == "Data Scientist"

    def test_contains(self):
        result = parse_constraints("doctor_name CONTAINS 'Steven'")
        assert len(result) == 1
        assert result[0].operator == "contains"
        assert result[0].value == "Steven"

    def test_not_contains(self):
        result = parse_constraints("name does NOT CONTAIN 'xyz'")
        assert len(result) == 1
        assert result[0].operator == "not_contains"
        assert result[0].value == "xyz"

    def test_greater_than(self):
        result = parse_constraints("price greater than 50")
        assert len(result) == 1
        assert result[0].operator == "greater_than"
        assert result[0].value == "50"

    def test_less_than(self):
        result = parse_constraints("rating less than 3")
        assert len(result) == 1
        assert result[0].operator == "less_than"
        assert result[0].value == "3"

    def test_greater_equal_via_between(self):
        # The between pattern reliably produces >= and <= constraints
        result = parse_constraints("price between 10 and 50")
        ops = {c.operator for c in result}
        assert "greater_equal" in ops

    def test_less_equal_via_between(self):
        result = parse_constraints("price between 10 and 50")
        ops = {c.operator for c in result}
        assert "less_equal" in ops

    def test_greater_than_standalone(self):
        result = parse_constraints("rating greater than 4.0")
        assert any(c.operator == "greater_than" for c in result)

    def test_less_than_standalone(self):
        result = parse_constraints("price less than 100")
        assert any(c.operator == "less_than" for c in result)

    def test_between(self):
        result = parse_constraints("price between 10 and 50")
        assert len(result) == 2
        ops = {c.operator for c in result}
        assert "greater_equal" in ops
        assert "less_equal" in ops

    def test_in_list(self):
        result = parse_constraints("genre is one of [Action, Comedy, Drama]")
        assert len(result) == 1
        assert result[0].operator == "in"
        assert isinstance(result[0].value, list)
        assert len(result[0].value) == 3

    def test_not_in_list(self):
        result = parse_constraints("status is not one of [cancelled, expired]")
        assert len(result) == 1
        assert result[0].operator == "not_in"

    def test_multiple_constraints(self):
        prompt = (
            "Show the contact doctor form for a doctor where doctor_name CONTAINS 'Steven', "
            "speciality CONTAINS 'log', rating is GREATER THAN OR EQUAL TO 5.0, "
            "consultation_fee EQUALS '208'"
        )
        result = parse_constraints(prompt)
        assert len(result) >= 3
        fields = {c.field for c in result}
        assert "doctor_name" in fields
        assert "speciality" in fields
        assert "consultation_fee" in fields

    def test_no_constraints(self):
        result = parse_constraints("Go to the home page")
        assert len(result) == 0

    def test_deduplication(self):
        result = parse_constraints("title equals 'Test' and title equals 'Test'")
        # Should deduplicate identical constraints
        title_equals = [c for c in result if c.field == "title" and c.operator == "equals"]
        assert len(title_equals) == 1


class TestFormatConstraintsBlock:
    def test_empty(self):
        assert format_constraints_block([]) == ""

    def test_single(self):
        from models import Constraint
        constraints = [Constraint(field="title", operator="equals", value="Test")]
        result = format_constraints_block(constraints)
        assert "CONSTRAINTS" in result
        assert "title" in result
        assert "MUST EQUAL" in result

    def test_not_operator_formatting(self):
        from models import Constraint
        constraints = [Constraint(field="name", operator="not_contains", value="xyz")]
        result = format_constraints_block(constraints)
        assert "NOT CONTAIN" in result


class TestExtractCredentials:
    def test_basic_credentials(self):
        prompt = "Login with username equals 'admin' and password equals 'secret'"
        creds = extract_credentials(prompt)
        assert creds["username"] == "admin"
        assert creds["password"] == "secret"

    def test_web_agent_id_substitution(self):
        prompt = "Login with username equals 'user<web_agent_id>'"
        creds = extract_credentials(prompt)
        assert "<web_agent_id>" not in creds["username"]
        assert "user1" == creds["username"]

    def test_default_placeholders(self):
        prompt = "Go to the home page"
        creds = extract_credentials(prompt)
        assert "username" in creds
        assert "password" in creds

    def test_iwa_placeholders(self):
        prompt = "Login with <username> and <password>"
        creds = extract_credentials(prompt)
        assert creds["username"] == "<username>"
        assert creds["password"] == "<password>"

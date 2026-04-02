"""Tests for all new features added in this session.

Covers:
- filter_table / match_cards tools
- Auto constraint matching (pre-pass)
- Email credential fix in action_builder
- model_override in LLMClient
- Registration navigation shortcut
- Classifier: CONNECT_WALLET, VIEW_BLOCK, POST_STATUS patterns
- Playbook/hint cap increases in prompts
- _apply_constraint / _row_matches_all logic
"""
from __future__ import annotations
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Candidate, Selector, Constraint
from tool_use import (
    tool_filter_table,
    tool_match_cards,
    _apply_constraint,
    _row_matches_all,
)
from action_builder import _infer_credentials
from classifier import classify_task_type
from constraint_parser import parse_constraints
from prompts import build_user_prompt, build_system_prompt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candidate(idx: int, tag: str, text: str, context: str = "", href: str = "") -> Candidate:
    sel = Selector(type="attributeValueSelector", attribute="id", value=f"el-{idx}")
    return Candidate(index=idx, tag=tag, text=text, selector=sel, context=context, href=href)


# ---------------------------------------------------------------------------
# 1. _apply_constraint
# ---------------------------------------------------------------------------

class TestApplyConstraint:
    def test_equals_exact(self):
        assert _apply_constraint("dr. smith", "equals", "dr. smith") is True

    def test_equals_mismatch(self):
        assert _apply_constraint("dr. jones", "equals", "dr. smith") is False

    def test_not_equals(self):
        assert _apply_constraint("dr. jones", "not_equals", "dr. smith") is True
        assert _apply_constraint("dr. smith", "not_equals", "dr. smith") is False

    def test_contains(self):
        assert _apply_constraint("dr. smith cardiology", "contains", "smith") is True
        assert _apply_constraint("dr. jones", "contains", "smith") is False

    def test_not_contains(self):
        assert _apply_constraint("dr. jones", "not_contains", "smith") is True
        assert _apply_constraint("dr. smith", "not_contains", "smith") is False

    def test_greater_than_numeric(self):
        assert _apply_constraint("0.06", "greater_than", "0.04") is True
        assert _apply_constraint("0.03", "greater_than", "0.04") is False

    def test_less_than_numeric(self):
        assert _apply_constraint("10", "less_than", "20") is True
        assert _apply_constraint("25", "less_than", "20") is False

    def test_greater_equal(self):
        assert _apply_constraint("5", "greater_equal", "5") is True
        assert _apply_constraint("4", "greater_equal", "5") is False

    def test_less_equal(self):
        assert _apply_constraint("5", "less_equal", "5") is True
        assert _apply_constraint("6", "less_equal", "5") is False

    def test_number_embedded_in_text(self):
        # "Price: $45.00" should satisfy less_equal 50
        assert _apply_constraint("price: $45.00", "less_equal", "50") is True
        assert _apply_constraint("price: $55.00", "less_equal", "50") is False

    def test_unknown_operator_passes(self):
        # Unknown operators should not block
        assert _apply_constraint("anything", "unknown_op", "value") is True


# ---------------------------------------------------------------------------
# 2. _row_matches_all
# ---------------------------------------------------------------------------

class TestRowMatchesAll:
    def test_single_equals_match(self):
        row = {"doctor_name": "Dr. Smith", "specialty": "Cardiology"}
        assert _row_matches_all(row, [{"field": "doctor_name", "operator": "equals", "value": "Dr. Smith"}])

    def test_single_equals_no_match(self):
        row = {"doctor_name": "Dr. Jones"}
        assert not _row_matches_all(row, [{"field": "doctor_name", "operator": "equals", "value": "Dr. Smith"}])

    def test_multi_constraint_all_match(self):
        row = {"name": "Alpha Chain", "emission": "0.06", "validators": "12", "description": "Active"}
        constraints = [
            {"field": "name", "operator": "contains", "value": "alpha"},
            {"field": "emission", "operator": "greater_than", "value": "0.04"},
            {"field": "validators", "operator": "not_equals", "value": "5"},
            {"field": "description", "operator": "not_contains", "value": "deprecated"},
        ]
        assert _row_matches_all(row, constraints)

    def test_multi_constraint_one_fails(self):
        row = {"name": "Alpha Chain", "emission": "0.02", "validators": "12"}
        constraints = [
            {"field": "name", "operator": "contains", "value": "alpha"},
            {"field": "emission", "operator": "greater_than", "value": "0.04"},  # fails
        ]
        assert not _row_matches_all(row, constraints)

    def test_not_constraint_missing_field(self):
        # NOT constraint on a field not in row should pass (trivially satisfied)
        row = {"name": "Alpha"}
        assert _row_matches_all(row, [{"field": "missing_field", "operator": "not_equals", "value": "x"}])

    def test_fuzzy_field_matching(self):
        # "doctor_name" constraint matches "doctor name" column
        row = {"doctor name": "Dr. Smith"}
        assert _row_matches_all(row, [{"field": "doctor_name", "operator": "contains", "value": "smith"}])

    def test_empty_constraints_always_true(self):
        assert _row_matches_all({"any": "data"}, [])


# ---------------------------------------------------------------------------
# 3. tool_filter_table
# ---------------------------------------------------------------------------

class TestFilterTable:
    TABLE_HTML = """
    <table>
      <thead><tr><th>Name</th><th>Emission</th><th>Validators</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td>Alpha Chain</td><td>0.06</td><td>12</td><td>Active subnet</td><td><button>Favorite</button></td></tr>
        <tr><td>Beta Net</td><td>0.02</td><td>5</td><td>deprecated subnet</td><td><button>Favorite</button></td></tr>
        <tr><td>Gamma Alpha</td><td>0.05</td><td>8</td><td>Growing network</td><td><button>Favorite</button></td></tr>
      </tbody>
    </table>
    """

    def test_single_constraint_match(self):
        result = tool_filter_table(
            html=self.TABLE_HTML,
            constraints=[{"field": "name", "operator": "contains", "value": "alpha"}],
        )
        assert result["ok"] is True
        assert result["count"] == 2  # Alpha Chain, Gamma Alpha

    def test_multi_constraint_narrows(self):
        result = tool_filter_table(
            html=self.TABLE_HTML,
            constraints=[
                {"field": "name", "operator": "contains", "value": "alpha"},
                {"field": "emission", "operator": "greater_than", "value": "0.04"},
                {"field": "validators", "operator": "not_equals", "value": "5"},
                {"field": "description", "operator": "not_contains", "value": "deprecated"},
            ],
        )
        assert result["ok"] is True
        assert result["count"] == 2  # Alpha Chain and Gamma Alpha both match

    def test_no_match(self):
        result = tool_filter_table(
            html=self.TABLE_HTML,
            constraints=[{"field": "name", "operator": "equals", "value": "Nonexistent"}],
        )
        assert result["ok"] is True
        assert result["count"] == 0

    def test_empty_constraints_returns_all_rows(self):
        result = tool_filter_table(html=self.TABLE_HTML, constraints=[])
        assert result["ok"] is True
        assert result["count"] == 3

    def test_empty_html(self):
        result = tool_filter_table(html="", constraints=[{"field": "name", "operator": "equals", "value": "x"}])
        assert result["ok"] is True
        assert result["count"] == 0

    def test_returns_actions_in_row(self):
        result = tool_filter_table(
            html=self.TABLE_HTML,
            constraints=[{"field": "name", "operator": "equals", "value": "Alpha Chain"}],
        )
        assert result["count"] == 1
        match = result["matches"][0]
        assert "actions" in match
        assert any(a["text"] == "Favorite" for a in match["actions"])

    def test_card_fallback(self):
        card_html = """
        <div class="card">subnet_name: Alpha Net | emission: 0.07 | validators: 10
          <button>Favorite</button>
        </div>
        <div class="card">subnet_name: Beta Chain | emission: 0.01 | validators: 3
          <button>Favorite</button>
        </div>
        """
        result = tool_filter_table(
            html=card_html,
            constraints=[{"field": "emission", "operator": "greater_than", "value": "0.05"}],
        )
        assert result["ok"] is True
        assert result["count"] >= 1


# ---------------------------------------------------------------------------
# 4. tool_match_cards
# ---------------------------------------------------------------------------

class TestMatchCards:
    def _make_subnet_candidates(self):
        return [
            _make_candidate(0, "button", "Favorite", context="subnet_name: Alpha Chain | emission: 0.06 | validators: 12 | description: Active subnet"),
            _make_candidate(1, "button", "Favorite", context="subnet_name: Beta Net | emission: 0.02 | validators: 5 | description: deprecated subnet"),
            _make_candidate(2, "button", "Favorite", context="subnet_name: Gamma Alpha | emission: 0.05 | validators: 8 | description: Growing network"),
            _make_candidate(3, "button", "View Details", context="subnet_name: Alpha Chain | emission: 0.06 | validators: 12 | description: Active subnet"),
        ]

    def test_single_constraint(self):
        candidates = self._make_subnet_candidates()
        result = tool_match_cards(
            candidates=candidates,
            constraints=[{"field": "subnet_name", "operator": "contains", "value": "alpha"}],
        )
        assert result["ok"] is True
        assert result["count"] >= 1
        # Alpha Chain and Gamma Alpha both contain 'alpha'
        all_cids = [cid for m in result["matches"] for cid in m["candidate_ids"]]
        assert 0 in all_cids or 3 in all_cids  # Alpha Chain candidates

    def test_multi_constraint_filters_correctly(self):
        candidates = self._make_subnet_candidates()
        constraints = [
            {"field": "subnet_name", "operator": "contains", "value": "alpha"},
            {"field": "emission", "operator": "greater_than", "value": "0.04"},
            {"field": "validators", "operator": "not_equals", "value": "5"},
            {"field": "description", "operator": "not_contains", "value": "deprecated"},
        ]
        result = tool_match_cards(candidates=candidates, constraints=constraints)
        assert result["ok"] is True
        assert result["count"] >= 1
        # Beta Net (deprecated, validators=5) must be excluded
        for m in result["matches"]:
            assert "deprecated" not in m["card_text"].lower()
            assert "beta net" not in m["card_text"].lower()

    def test_no_match(self):
        candidates = self._make_subnet_candidates()
        result = tool_match_cards(
            candidates=candidates,
            constraints=[{"field": "subnet_name", "operator": "equals", "value": "Nonexistent Subnet"}],
        )
        assert result["ok"] is True
        assert result["count"] == 0

    def test_empty_candidates(self):
        result = tool_match_cards(candidates=[], constraints=[{"field": "x", "operator": "equals", "value": "y"}])
        assert result["ok"] is True
        assert result["count"] == 0

    def test_empty_constraints_returns_cards(self):
        candidates = self._make_subnet_candidates()
        result = tool_match_cards(candidates=candidates, constraints=[])
        assert result["ok"] is True
        assert result["count"] >= 1

    def test_returns_candidate_ids(self):
        candidates = self._make_subnet_candidates()
        result = tool_match_cards(
            candidates=candidates,
            constraints=[{"field": "description", "operator": "contains", "value": "Active"}],
        )
        assert result["count"] >= 1
        assert len(result["matches"][0]["candidate_ids"]) >= 1


# ---------------------------------------------------------------------------
# 5. Email credential fix in action_builder
# ---------------------------------------------------------------------------

class TestEmailCredentialFix:
    def _email_candidate(self) -> Candidate:
        sel = Selector(type="attributeValueSelector", attribute="id", value="email-field")
        return Candidate(index=0, tag="input", text="", selector=sel, input_type="email", name="email")

    def _username_candidate(self) -> Candidate:
        sel = Selector(type="attributeValueSelector", attribute="id", value="user-field")
        return Candidate(index=0, tag="input", text="", selector=sel, input_type="text", name="username")

    def _password_candidate(self) -> Candidate:
        sel = Selector(type="attributeValueSelector", attribute="id", value="pass-field")
        return Candidate(index=0, tag="input", text="", selector=sel, input_type="password", name="password")

    def test_email_field_gets_signup_email(self):
        result = _infer_credentials("", self._email_candidate())
        assert result == "<signup_email>", f"Expected <signup_email>, got {result!r}"

    def test_email_field_not_username(self):
        result = _infer_credentials("", self._email_candidate())
        assert result != "<username>", "Email field should NOT return <username>"

    def test_username_field_gets_username(self):
        result = _infer_credentials("", self._username_candidate())
        assert result == "<username>"

    def test_password_field_gets_password(self):
        result = _infer_credentials("", self._password_candidate())
        assert result == "<password>"

    def test_nonempty_text_passthrough(self):
        result = _infer_credentials("already_set@example.com", self._email_candidate())
        assert result == "already_set@example.com"


# ---------------------------------------------------------------------------
# 6. Classifier: new task types
# ---------------------------------------------------------------------------

class TestClassifierNewTypes:
    def test_connect_wallet(self):
        assert classify_task_type("Connect a wallet to the platform") == "CONNECT_WALLET"

    def test_connect_wallet_variant(self):
        assert classify_task_type("Please connect the wallet that equals 'Polkadot.js'") == "CONNECT_WALLET"

    def test_view_block(self):
        assert classify_task_type("Show details for a block where block_number equals 12345") == "VIEW_BLOCK"

    def test_view_block_variant(self):
        assert classify_task_type("View the block where the hash equals 'abc123'") == "VIEW_BLOCK"

    def test_post_status(self):
        assert classify_task_type("Post a status update on the feed") == "POST_STATUS"

    def test_post_status_with_constraint(self):
        assert classify_task_type("Post a status update where the content not equals 'hello'") == "POST_STATUS"

    def test_favorite_subnet(self):
        assert classify_task_type("Favorite the subnet where name contains 'Alpha'") == "FAVORITE_SUBNET"

    def test_disconnect_wallet_unchanged(self):
        assert classify_task_type("Disconnect the wallet from the platform") == "DISCONNECT_WALLET"

    def test_reserve_ride(self):
        assert classify_task_type("Reserve a ride where location contains 'Airport'") == "RESERVE_RIDE"

    def test_add_experience(self):
        assert classify_task_type("Add experience at a company where company equals 'Acme'") == "ADD_EXPERIENCE"


# ---------------------------------------------------------------------------
# 7. Prompts: cap increases and matched_items injection
# ---------------------------------------------------------------------------

class TestPromptsImprovements:
    def _base_kwargs(self):
        return dict(
            prompt="Test task",
            page_ir_text="[0] button: Click me",
            step_index=0,
            task_type="GENERAL",
            action_history=[],
            website="autocinema",
        )

    def test_playbook_cap_500(self):
        long_playbook = "PLAYBOOK: " + "x" * 600
        result = build_user_prompt(**self._base_kwargs(), playbook=long_playbook)
        # Should be capped at 500 chars + "..."
        assert "x" * 490 in result
        assert "x" * 510 not in result

    def test_hint_cap_280(self):
        long_hint = "SITE: " + "h" * 400
        result = build_user_prompt(**self._base_kwargs(), website_hint=long_hint)
        assert "h" * 270 in result
        assert "h" * 290 not in result

    def test_matched_items_injected(self):
        matched = "AUTO_MATCHED 1 item(s):\n  candidate_id=3 (Favorite): Alpha Chain"
        result = build_user_prompt(**self._base_kwargs(), matched_items=matched)
        assert "AUTO_MATCHED" in result
        assert "candidate_id=3" in result

    def test_matched_items_after_constraints(self):
        matched = "AUTO_MATCHED 1 item(s): Alpha Chain"
        constraints_block = "CONSTRAINTS:\n  [name] MUST EQUAL 'Alpha'"
        result = build_user_prompt(
            **self._base_kwargs(),
            constraints_block=constraints_block,
            matched_items=matched,
        )
        constraints_pos = result.index("CONSTRAINTS")
        matched_pos = result.index("AUTO_MATCHED")
        assert matched_pos > constraints_pos, "Matched items should appear after constraints"

    def test_matched_items_empty_no_injection(self):
        result = build_user_prompt(**self._base_kwargs(), matched_items="")
        assert "AUTO_MATCHED" not in result

    def test_matched_items_capped_at_600(self):
        long_matched = "AUTO_MATCHED: " + "x" * 700
        result = build_user_prompt(**self._base_kwargs(), matched_items=long_matched)
        assert "x" * 580 in result
        assert "x" * 610 not in result

    def test_system_prompt_has_new_tools(self):
        system = build_system_prompt()
        assert "match_cards" in system
        assert "filter_table" in system
        assert "STRATEGY" in system

    def test_system_prompt_has_operator_reference(self):
        system = build_system_prompt()
        assert "not_contains" in system
        assert "greater_than" in system


# ---------------------------------------------------------------------------
# 8. Registration shortcut navigation
# ---------------------------------------------------------------------------

class TestRegistrationShortcut:
    """Registration shortcut should navigate to register page if form not found."""

    def _make_nav_candidates(self):
        """Candidates that include a Register link but no form fields."""
        return [
            _make_candidate(0, "a", "Home", href="/"),
            _make_candidate(1, "a", "Register", href="/register"),
            _make_candidate(2, "a", "Login", href="/login"),
        ]

    def _make_form_candidates(self):
        """Candidates with actual registration form fields."""
        sel_u = Selector(type="attributeValueSelector", attribute="name", value="username")
        sel_p = Selector(type="attributeValueSelector", attribute="name", value="password")
        sel_s = Selector(type="attributeValueSelector", attribute="id", value="register-btn")
        from bs4 import BeautifulSoup
        return [
            Candidate(index=0, tag="input", text="", selector=sel_u, input_type="text", name="username"),
            Candidate(index=1, tag="input", text="", selector=sel_p, input_type="password", name="password"),
            Candidate(index=2, tag="button", text="Register", selector=sel_s),
        ]

    def test_navigates_to_register_when_no_form(self):
        from bs4 import BeautifulSoup
        from shortcuts import try_shortcut
        soup = BeautifulSoup("<html><body><a href='/register'>Register</a></body></html>", "lxml")
        candidates = self._make_nav_candidates()
        result = try_shortcut("registration", candidates, soup, step_index=0, creds={})
        assert result is not None, "Should return a click action for Register link"
        assert result[0]["type"] == "ClickAction"

    def test_fills_form_when_on_register_page(self):
        from bs4 import BeautifulSoup
        from shortcuts import try_shortcut
        html = "<html><body><input name='username'/><input type='password' name='password'/><button>Register</button></body></html>"
        soup = BeautifulSoup(html, "lxml")
        candidates = self._make_form_candidates()
        result = try_shortcut("registration", candidates, soup, step_index=0, creds={})
        assert result is not None
        type_actions = [a for a in result if a["type"] == "TypeAction"]
        assert len(type_actions) >= 2  # username + password


# ---------------------------------------------------------------------------
# 9. LLMClient model_override
# ---------------------------------------------------------------------------

class TestLLMClientModelOverride:
    def test_default_model_used_without_override(self):
        from llm_client import LLMClient
        client = LLMClient()
        assert client.model is not None

    def test_model_override_accepted(self):
        """Verify chat() accepts model_override without TypeError."""
        import inspect
        from llm_client import LLMClient
        sig = inspect.signature(LLMClient.chat)
        assert "model_override" in sig.parameters

    def test_chat_openai_accepts_override(self):
        import inspect
        from llm_client import LLMClient
        sig = inspect.signature(LLMClient._chat_openai)
        assert "model_override" in sig.parameters

    def test_track_cost_with_rates_exists(self):
        from llm_client import LLMClient
        assert hasattr(LLMClient, "_track_cost_with_rates")


# ---------------------------------------------------------------------------
# 10. Integration: parse_constraints -> tool_match_cards round-trip
# ---------------------------------------------------------------------------

class TestConstraintToMatchRoundTrip:
    """Full pipeline: parse prompt constraints → match_cards → find correct item."""

    def test_favorite_subnet_full_pipeline(self):
        prompt = ("Favorite the subnet where subnet_name contains 'Alpha' "
                  "and emission greater than 0.04 and validators not equals 5 "
                  "and description not contains 'deprecated'")
        constraints = parse_constraints(prompt)
        assert len(constraints) == 4

        candidates = [
            _make_candidate(0, "button", "Favorite",
                            context="subnet_name: Alpha Chain | emission: 0.06 | validators: 12 | description: Active"),
            _make_candidate(1, "button", "Favorite",
                            context="subnet_name: Beta Net | emission: 0.02 | validators: 5 | description: deprecated"),
            _make_candidate(2, "button", "Favorite",
                            context="subnet_name: Gamma Alpha | emission: 0.05 | validators: 8 | description: Growing"),
        ]
        constraint_dicts = [{"field": c.field, "operator": c.operator, "value": str(c.value)} for c in constraints]
        result = tool_match_cards(candidates=candidates, constraints=constraint_dicts)

        assert result["count"] >= 1
        # Beta Net must NOT be in results
        for m in result["matches"]:
            assert "beta net" not in m["card_text"].lower()
            assert "deprecated" not in m["card_text"].lower()

    def test_reserve_ride_full_pipeline(self):
        prompt = ("Reserve a ride where location contains 'Airport' "
                  "and price less_equal 30 and ride_name not equals 'Economy'")
        constraints = parse_constraints(prompt)
        assert len(constraints) >= 2

        candidates = [
            _make_candidate(0, "button", "Reserve",
                            context="ride_name: Premium | location: Airport North | price: 25"),
            _make_candidate(1, "button", "Reserve",
                            context="ride_name: Economy | location: Airport South | price: 15"),
            _make_candidate(2, "button", "Reserve",
                            context="ride_name: Luxury | location: City Center | price: 50"),
        ]
        constraint_dicts = [{"field": c.field, "operator": c.operator, "value": str(c.value)} for c in constraints]
        result = tool_match_cards(candidates=candidates, constraints=constraint_dicts)

        assert result["count"] >= 1
        # Economy must be excluded (not_equals)
        for m in result["matches"]:
            assert "economy" not in m["card_text"].lower()
        # City Center must be excluded (no 'airport')
        for m in result["matches"]:
            assert "city center" not in m["card_text"].lower()

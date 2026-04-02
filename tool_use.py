"""HTML inspection tools for LLM tool-use loop.

The LLM can request these tools to gather more information before deciding on an action.
Each tool returns a dict with ok=True/False and result data.
"""
from __future__ import annotations
import re
import json
from typing import Any
from bs4 import BeautifulSoup


def _norm_ws(s: str) -> str:
    return " ".join(s.split())


def _safe_truncate(s: str, n: int) -> str:
    s = str(s or "")
    return s if len(s) <= n else (s[:max(0, n - 3)] + "...")


def tool_search_text(*, html: str, query: str, max_matches: int = 20, context_chars: int = 80) -> dict[str, Any]:
    q = str(query or "")
    if not q:
        return {"ok": False, "error": "missing query"}
    try:
        pat = re.compile(re.escape(q), re.IGNORECASE)
    except Exception as e:
        return {"ok": False, "error": f"invalid pattern: {str(e)[:120]}"}

    hay = str(html or "")
    out = []
    for m in pat.finditer(hay):
        if len(out) >= max_matches:
            break
        a = max(0, m.start() - context_chars)
        b = min(len(hay), m.end() + context_chars)
        out.append({
            "start": m.start(),
            "end": m.end(),
            "snippet": _safe_truncate(hay[a:b].replace("\n", " ").replace("\r", " "), 2 * context_chars + 40),
        })
    return {"ok": True, "matches": out, "count": len(out)}


def tool_extract_forms(*, html: str, max_forms: int = 10, max_inputs: int = 25) -> dict[str, Any]:
    try:
        soup = BeautifulSoup(html or "", "lxml")
    except Exception as e:
        return {"ok": False, "error": f"parse failed: {str(e)[:160]}"}

    forms = []
    for f in soup.find_all("form")[:max_forms]:
        try:
            f_attrs = {k: str(v) if isinstance(v, str) else " ".join(v) for k, v in (f.attrs or {}).items()}
            inputs = []
            for el in f.find_all(["input", "textarea", "select", "button"])[:max_inputs]:
                try:
                    a = {k: str(v) if isinstance(v, str) else " ".join(v) for k, v in (el.attrs or {}).items()}
                    t = _norm_ws(el.get_text(" ", strip=True))
                    inputs.append({
                        "tag": el.name,
                        "type": (a.get("type") or "").lower(),
                        "id": a.get("id") or "",
                        "name": a.get("name") or "",
                        "placeholder": a.get("placeholder") or "",
                        "text": _safe_truncate(t, 160),
                    })
                except Exception:
                    continue
            forms.append({
                "id": f_attrs.get("id") or "",
                "name": f_attrs.get("name") or "",
                "action": f_attrs.get("action") or "",
                "controls": inputs,
            })
        except Exception:
            continue
    return {"ok": True, "forms": forms, "count": len(forms)}


def tool_list_links(*, html: str, base_url: str, max_links: int = 60) -> dict[str, Any]:
    try:
        soup = BeautifulSoup(html or "", "lxml")
    except Exception as e:
        return {"ok": False, "error": f"parse failed: {str(e)[:160]}"}

    from urllib.parse import urljoin
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    for a in soup.select("a[href]"):
        try:
            href = str(a.get("href") or "").strip()
            if not href or href.lower().startswith("javascript:"):
                continue
            text = _norm_ws(a.get_text(" ", strip=True))
            if not text:
                text = _norm_ws(str(a.get("aria-label") or ""))

            resolved = urljoin(base_url, href) if base_url else href
            sig = resolved + "|" + text
            if sig in seen:
                continue
            seen.add(sig)

            out.append({
                "href": _safe_truncate(href, 260),
                "url": _safe_truncate(resolved, 320),
                "text": _safe_truncate(text, 160),
            })
            if len(out) >= max_links:
                break
        except Exception:
            continue
    return {"ok": True, "count": len(out), "links": out}


def tool_list_cards(*, candidates: list, max_cards: int = 25, max_text: int = 900) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}

    for i, c in enumerate(candidates or []):
        try:
            if c.tag not in {"a", "button"}:
                if not (c.selector and c.selector.attribute == "href"):
                    continue

            key = (c.context or "").strip()
            if not key:
                key = "(no_context)"

            g = groups.get(key)
            if g is None:
                g = {"card_text": _safe_truncate(key, max_text), "candidate_ids": [], "actions": []}
                groups[key] = g

            g["candidate_ids"].append(i)
            if len(g["actions"]) < 6:
                g["actions"].append({
                    "candidate_id": i,
                    "tag": c.tag,
                    "text": _safe_truncate(c.text or "", 140),
                })
        except Exception:
            continue

    ranked = []
    for _k, g in groups.items():
        txt = str(g.get("card_text") or "")
        n_actions = len(g.get("actions") or [])
        L = len(txt)
        penalty = 0
        if L < 40:
            penalty += 400
        if L > 900:
            penalty += min(1200, L - 900)
        score = (1000 - penalty + min(L, 700), n_actions)
        ranked.append((score, g))

    ranked.sort(key=lambda x: x[0], reverse=True)
    cards = [g for _, g in ranked[:max_cards]]
    return {"ok": True, "count": len(cards), "cards": cards}


def _apply_constraint(text: str, operator: str, value: str) -> bool:
    """Check if text satisfies a single constraint."""
    t = text.lower().strip()
    v = str(value).lower().strip()
    if operator == "equals":
        return t == v or t.startswith(v + " ") or t.endswith(" " + v)
    elif operator == "not_equals":
        return not (t == v or t.startswith(v + " ") or t.endswith(" " + v))
    elif operator == "contains":
        return v in t
    elif operator == "not_contains":
        return v not in t
    elif operator in ("greater_than", "less_than", "greater_equal", "less_equal"):
        # Extract numbers from text and compare
        nums = re.findall(r'-?\d+(?:\.\d+)?', t.replace(',', ''))
        try:
            threshold = float(v.replace(',', ''))
            for n in nums:
                nf = float(n)
                if operator == "greater_than" and nf > threshold:
                    return True
                if operator == "less_than" and nf < threshold:
                    return True
                if operator == "greater_equal" and nf >= threshold:
                    return True
                if operator == "less_equal" and nf <= threshold:
                    return True
        except ValueError:
            pass
        return False
    return True


def _row_matches_all(row_data: dict[str, str], constraints: list[dict]) -> bool:
    """Return True if all constraints are satisfied by the row data."""
    for c in constraints:
        field = str(c.get("field", "")).lower().replace(" ", "_")
        op = str(c.get("operator", "equals"))
        val = str(c.get("value", ""))
        # Try to find a matching column in the row
        satisfied = False
        field_found = False
        for col_key, col_val in row_data.items():
            col_lower = col_key.lower().replace(" ", "_")
            # Match if field name is substring of column name or vice versa
            if field in col_lower or col_lower in field or field == "*":
                field_found = True
                if _apply_constraint(col_val, op, val):
                    satisfied = True
                    break
        # For NOT constraints, missing field means constraint is trivially satisfied
        # (but if the field WAS found and failed, it must NOT pass)
        if not satisfied and not field_found and op in ("not_equals", "not_contains", "not_in"):
            satisfied = True
        if not satisfied:
            return False
    return True


def tool_filter_table(*, html: str, constraints: list[dict] | None = None, max_rows: int = 100) -> dict[str, Any]:
    """Parse HTML tables and card lists, return rows/cards matching ALL constraints.

    constraints: list of {field, operator, value} dicts.
    Operators: equals, not_equals, contains, not_contains, greater_than, less_than, greater_equal, less_equal
    """
    try:
        soup = BeautifulSoup(html or "", "lxml")
    except Exception as e:
        return {"ok": False, "error": f"parse failed: {str(e)[:160]}"}

    constraints = constraints or []
    results: list[dict[str, Any]] = []

    # --- 1. Parse HTML <table> elements ---
    for tbl_idx, table in enumerate(soup.find_all("table")):
        # Extract headers
        headers: list[str] = []
        thead = table.find("thead")
        first_tr = table.find("tr")
        header_source = thead.find("tr") if thead else first_tr
        if header_source:
            for th in header_source.find_all(["th", "td"]):
                headers.append(_norm_ws(th.get_text(" ", strip=True)).lower().replace(" ", "_"))

        # Extract data rows (skip header row)
        tbody = table.find("tbody")
        if tbody:
            data_rows = tbody.find_all("tr")
        else:
            data_rows = table.find_all("tr")
        start = 1 if (not tbody and first_tr) else 0
        for row_idx, row in enumerate(data_rows[start:start + max_rows]):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            row_data: dict[str, str] = {}
            for j, cell in enumerate(cells):
                col_key = headers[j] if j < len(headers) else f"col{j}"
                row_data[col_key] = _norm_ws(cell.get_text(" ", strip=True))

            if _row_matches_all(row_data, constraints):
                # Collect clickable elements in the row
                row_actions = []
                for el in row.find_all(["a", "button"])[:4]:
                    el_text = _norm_ws(el.get_text(" ", strip=True))
                    el_href = str(el.get("href") or "")
                    el_id = str(el.get("id") or "")
                    row_actions.append({
                        "text": _safe_truncate(el_text, 60),
                        "href": _safe_truncate(el_href, 120),
                        "id": el_id,
                    })
                results.append({
                    "source": f"table_{tbl_idx}",
                    "row_index": row_idx,
                    "data": row_data,
                    "actions": row_actions,
                })

    # --- 2. Parse card/list-style layouts if no table results ---
    if not results:
        card_selectors = [
            ("div", re.compile(r'\b(card|item|listing|result|row|entry|subnet|validator|miner)\b', re.I)),
            ("li", None),
            ("article", None),
            ("tr", None),
        ]
        seen_texts: set[str] = set()
        for tag, cls_pat in card_selectors:
            if cls_pat:
                containers = soup.find_all(tag, class_=cls_pat)
            else:
                containers = soup.find_all(tag)
            for i, card in enumerate(containers[:max_rows]):
                text = _norm_ws(card.get_text(" ", strip=True))
                if len(text) < 30 or text in seen_texts:
                    continue
                seen_texts.add(text)
                # Build row_data from text (field: value style parsing)
                row_data = {"_text": text}
                # Try to find label:value patterns
                for kv in re.finditer(r'([\w\s]{2,25}):\s*([^\n|]{1,80})', text):
                    k = kv.group(1).strip().lower().replace(" ", "_")
                    v = kv.group(2).strip()
                    if k and v:
                        row_data[k] = v
                if _row_matches_all(row_data, constraints):
                    actions = []
                    for el in card.find_all(["a", "button"])[:4]:
                        el_text = _norm_ws(el.get_text(" ", strip=True))
                        el_href = str(el.get("href") or "")
                        actions.append({"text": _safe_truncate(el_text, 60), "href": _safe_truncate(el_href, 120)})
                    results.append({
                        "source": f"card_{i}",
                        "row_index": i,
                        "data": {"summary": _safe_truncate(text, 300)},
                        "actions": actions,
                    })
            if results:
                break

    return {
        "ok": True,
        "count": len(results),
        "matches": results[:20],
        "hint": "Use the data and actions fields to identify which candidate to interact with.",
    }


def tool_match_cards(
    *,
    candidates: list,
    constraints: list[dict] | None = None,
    html: str = "",
    max_results: int = 10,
) -> dict[str, Any]:
    """Find candidate cards/items matching ALL constraints.

    Groups candidates by their context (surrounding text), then filters groups
    that satisfy ALL constraints. Returns matching cards with candidate_ids.

    constraints: list of {field, operator, value} dicts.
    """
    constraints = constraints or []

    # Group candidates by their context text
    groups: dict[str, dict[str, Any]] = {}
    for i, c in enumerate(candidates or []):
        try:
            ctx = (c.context or "").strip()
            if not ctx:
                ctx = (c.text or f"candidate_{i}").strip()
            if ctx not in groups:
                groups[ctx] = {
                    "card_text": ctx,
                    "candidate_ids": [],
                    "actions": [],
                }
            groups[ctx]["candidate_ids"].append(i)
            if len(groups[ctx]["actions"]) < 5:
                act_text = _safe_truncate(c.text or "", 80)
                if act_text:
                    groups[ctx]["actions"].append({
                        "candidate_id": i,
                        "tag": c.tag,
                        "text": act_text,
                    })
        except Exception:
            continue

    # Filter groups by constraints
    matching: list[dict[str, Any]] = []
    for card_text, group in groups.items():
        if len(card_text) < 15:
            continue
        # Build row_data from card text for structured matching
        row_data: dict[str, str] = {"_text": card_text}
        # Extract "label: value" patterns
        for kv in re.finditer(r'([\w\s]{2,30}):\s*([^\n|]{1,100})', card_text):
            k = kv.group(1).strip().lower().replace(" ", "_")
            v = kv.group(2).strip()
            if k and v:
                row_data[k] = v

        if _row_matches_all(row_data, constraints):
            matching.append({
                "card_text": _safe_truncate(card_text, 500),
                "candidate_ids": group["candidate_ids"],
                "actions": group["actions"],
                "hint": f"Use candidate_id from actions to click/interact. First candidate_id: {group['candidate_ids'][0] if group['candidate_ids'] else 'n/a'}",
            })

    return {
        "ok": True,
        "count": len(matching),
        "matches": matching[:max_results],
        "total_cards": len(groups),
    }


TOOL_REGISTRY = {
    "search_text": tool_search_text,
    "extract_forms": tool_extract_forms,
    "list_links": tool_list_links,
    "list_cards": tool_list_cards,
    "filter_table": tool_filter_table,
    "match_cards": tool_match_cards,
}


def run_tool(tool: str, args: dict[str, Any], *, html: str, url: str, candidates: list) -> dict[str, Any]:
    t = str(tool or "").strip()
    fn = TOOL_REGISTRY.get(t)
    if fn is None:
        return {"ok": False, "error": f"unknown tool: {t}", "known": sorted(TOOL_REGISTRY.keys())}

    a = args if isinstance(args, dict) else {}
    if t == "list_cards":
        return fn(candidates=candidates, **{k: v for k, v in a.items() if k in {"max_cards", "max_text"}})
    if t == "list_links":
        return fn(html=html, base_url=str(url or ""), **{k: v for k, v in a.items() if k in {"max_links"}})
    if t in {"search_text", "extract_forms"}:
        return fn(html=html, **a)
    if t == "filter_table":
        return fn(html=html, constraints=a.get("constraints"), max_rows=a.get("max_rows", 100))
    if t == "match_cards":
        return fn(candidates=candidates, constraints=a.get("constraints"), html=html, max_results=a.get("max_results", 10))
    return {"ok": False, "error": f"tool not wired: {t}"}

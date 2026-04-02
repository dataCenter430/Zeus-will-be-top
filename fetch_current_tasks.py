"""Fetch current evaluation task IDs from the leaderboard API and merge into task_ids.json.

Usage:
    py -3 fetch_current_tasks.py

Fetches all tasks (failures + successes) for minerUid=28 and adds round-12
task IDs to data/task_ids.json so generate_baseline.py can build KB entries.
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

MINER_UID = 28
BASE = "https://api-leaderboard.autoppia.com/api/v1/tasks/search"
OUT_FILE = Path(__file__).parent / "data" / "task_ids.json"


def fetch_page(mode: str, page: int, limit: int = 100) -> list:
    url = f"{BASE}?minerUid={MINER_UID}&successMode={mode}&page={page}&limit={limit}&includeDetails=true"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                # Response format: {"success": True, "data": {"tasks": [...], "total": N}}
                if isinstance(data, dict):
                    inner = data.get("data", data)
                    if isinstance(inner, dict):
                        for key in ("tasks", "items", "results"):
                            if key in inner and isinstance(inner[key], list):
                                return inner[key]
                    if isinstance(inner, list):
                        return inner
                    for key in ("tasks", "items", "results"):
                        if key in data and isinstance(data[key], list):
                            return data[key]
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            print(f"  Attempt {attempt+1} failed for {mode} page {page}: {e}")
            time.sleep(2)
    return []


def extract_task_info(item: dict) -> tuple[str, dict] | None:
    """Extract (task_id, info_dict) from a leaderboard API item."""
    task = item.get("task") or item
    task_id = task.get("taskId") or item.get("taskId") or item.get("task_id")
    if not task_id:
        return None
    use_case = task.get("useCase") or item.get("useCase") or item.get("use_case") or ""
    prompt = task.get("prompt") or item.get("prompt") or ""
    website = task.get("website") or item.get("website") or ""
    # Score: 1.0 for success, 0.0 for failure
    success = item.get("success") or item.get("isSuccess") or item.get("is_success") or False
    score = 1.0 if success else 0.0
    if not (task_id and use_case and website):
        return None
    return task_id, {
        "prompt": prompt,
        "website": website,
        "useCase": use_case,
        "score": score,
    }


def main():
    # Load existing task_ids.json
    existing: dict = {}
    if OUT_FILE.exists():
        with open(OUT_FILE, encoding="utf-8") as f:
            existing = json.load(f)
    print(f"Existing task IDs: {len(existing)}")

    new_tasks: dict = {}

    # Fetch failures
    print("Fetching failures...")
    for page in range(1, 10):
        items = fetch_page("non_successful", page)
        if not items:
            print(f"  Page {page}: no items, stopping")
            break
        count = 0
        for item in items:
            result = extract_task_info(item)
            if result:
                tid, info = result
                if tid not in existing:
                    new_tasks[tid] = info
                    count += 1
        print(f"  Failures page {page}: {len(items)} items, {count} new")
        if len(items) < 100:
            break

    # Fetch successes
    print("Fetching successes...")
    for page in range(1, 5):
        items = fetch_page("successful", page)
        if not items:
            print(f"  Page {page}: no items, stopping")
            break
        count = 0
        for item in items:
            result = extract_task_info(item)
            if result:
                tid, info = result
                info["score"] = 1.0  # force score=1 for success
                if tid not in existing:
                    new_tasks[tid] = info
                    count += 1
        print(f"  Successes page {page}: {len(items)} items, {count} new")
        if len(items) < 100:
            break

    print(f"\nNew task IDs found: {len(new_tasks)}")

    if not new_tasks:
        print("No new tasks found. Exiting.")
        return

    # Show breakdown by round
    rounds: dict[str, int] = {}
    for tid in new_tasks:
        parts = tid.split("_")
        if len(parts) >= 6:
            round_key = f"round_{parts[3]}_{parts[4]}"
        else:
            round_key = "unknown"
        rounds[round_key] = rounds.get(round_key, 0) + 1
    print("Breakdown by round/hotkey:")
    for k, v in sorted(rounds.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v} tasks")

    # Merge into existing
    merged = {**existing, **new_tasks}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(merged)} total task IDs to {OUT_FILE}")
    print(f"  Old: {len(existing)}, Added: {len(new_tasks)}")


if __name__ == "__main__":
    main()

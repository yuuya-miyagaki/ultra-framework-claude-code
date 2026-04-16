#!/usr/bin/env python3
"""LEARNINGS.md search and summary tool."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Entry(NamedTuple):
    confidence: int
    category: str
    text: str


_CATEGORY_RE = re.compile(r"<!--\s*category:\s*(\w+)\s*-->")
_ENTRY_RE = re.compile(r"^-\s*\[confidence:(\d+)\]\s*(.+)$")


def parse_learnings(content: str) -> list[Entry]:
    """Parse LEARNINGS.md into structured entries."""
    entries: list[Entry] = []
    current_category = "unknown"
    for line in content.splitlines():
        cat_match = _CATEGORY_RE.search(line)
        if cat_match:
            current_category = cat_match.group(1)
            continue
        entry_match = _ENTRY_RE.match(line.strip())
        if entry_match:
            confidence = int(entry_match.group(1))
            text = entry_match.group(2).strip()
            entries.append(Entry(confidence=confidence, category=current_category, text=text))
    return entries


def filter_entries(
    entries: list[Entry],
    *,
    query: str | None = None,
    category: str | None = None,
    min_confidence: int | None = None,
) -> list[Entry]:
    """Apply AND-combined filters to entries."""
    result = entries
    if query:
        q = query.lower()
        result = [e for e in result if q in e.text.lower()]
    if category:
        c = category.lower()
        result = [e for e in result if e.category.lower() == c]
    if min_confidence is not None:
        result = [e for e in result if e.confidence >= min_confidence]
    return result


def format_entry(entry: Entry) -> str:
    return f"[confidence:{entry.confidence}] [{entry.category}] {entry.text}"


def format_summary(entries: list[Entry]) -> str:
    """Category-level summary with count and average confidence."""
    categories: dict[str, list[int]] = {}
    for e in entries:
        categories.setdefault(e.category, []).append(e.confidence)
    lines = ["=== LEARNINGS Summary ===", ""]
    for cat in sorted(categories):
        scores = categories[cat]
        avg = sum(scores) / len(scores)
        lines.append(f"  {cat}: {len(scores)} entries, avg confidence {avg:.1f}")
    lines.append(f"\nTotal: {len(entries)} entries")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search and summarize LEARNINGS.md")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--query", help="Text search (case-insensitive)")
    parser.add_argument("--category", help="Filter by category name")
    parser.add_argument("--min-confidence", type=int, help="Minimum confidence threshold")
    parser.add_argument("--summary", action="store_true", help="Show category summary")
    args = parser.parse_args()

    learnings_path = Path(args.root) / "docs" / "LEARNINGS.md"
    if not learnings_path.exists():
        print(f"ERROR: {learnings_path} not found", file=sys.stderr)
        return 1

    content = learnings_path.read_text(encoding="utf-8")
    entries = parse_learnings(content)
    filtered = filter_entries(
        entries,
        query=args.query,
        category=args.category,
        min_confidence=args.min_confidence,
    )

    if args.summary:
        print(format_summary(filtered))
    else:
        if not filtered:
            print("No matching entries found.")
        else:
            for e in filtered:
                print(format_entry(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())

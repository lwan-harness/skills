#!/usr/bin/env python3
"""Deterministically clean transcript/SRT terminology with ordered regex rules."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable


DEFAULT_RULES = [
    (r"\bQuad Code\b", "Claude Code"),
    (r"\bquad code\b", "Claude Code"),
    (r"\bClaud Code\b", "Claude Code"),
    (r"\bClaud code\b", "Claude Code"),
    (r"\bClaud\b", "Claude"),
    (r"\bQuadMDs\b", "CLAUDE.md files"),
    (r"\bQuadMD\b", "CLAUDE.md"),
    (r"\bQuads on the ray track\b", "Claude is on the right track"),
    (r"\bQuad\b", "Claude"),
    (r"\bquad\b", "Claude"),
    (r"\bCLI-MD\b", "CLAUDE.md"),
    (r"\bClaude\.md\b", "CLAUDE.md"),
    (r"\bClaudemds\b", "CLAUDE.md files"),
    (r"\bClaudemd\b", "CLAUDE.md"),
    (r"CLAUDE\.md's", "CLAUDE.md files"),
    (r"dot-clawed", ".claude"),
    (r"\bCLAUDE\.\s+You can also", "CLAUDE.md. You can also"),
    (r"not just CLAUDE but also", "not just CLAUDE.md but also"),
    (r"JetBrains IDs", "JetBrains IDEs"),
    (r"All you need is no JS", "All you need is Node.js"),
    (r"your code stays vocal", "your code stays local"),
    (r"stays vocal", "stays local"),
    (r"3,000 wine feature", "3,000 line feature"),
    (r"system promising", "system prompting"),
    (r"friend yourself", "find yourself"),
    (r"on your baff", "on your behalf"),
    (r"screenshoting", "screenshotting"),
    (r"global quickly", "global category"),
    (r"shirt with", "share it with"),
    (r"take a quick interview", "take a quick interlude"),
    (r"into a Doxmer", "into a doc"),
    (r"went test", "run tests"),
    (r"install with themselves", "install it themselves"),
]


def load_rules(path: Path | None) -> list[tuple[str, str]]:
    rules = list(DEFAULT_RULES)
    if path is None:
        return rules

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        rules.extend((re.escape(k), str(v)) for k, v in data.items())
        return rules

    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict) or "pattern" not in item or "replacement" not in item:
                raise SystemExit("Glossary list entries must contain pattern and replacement.")
            rules.append((str(item["pattern"]), str(item["replacement"])))
        return rules

    raise SystemExit("Glossary must be a JSON object or a list of {pattern, replacement}.")


def apply_rules(text: str, rules: Iterable[tuple[str, str]]) -> str:
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--glossary", type=Path, help="Optional JSON glossary.")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8", errors="replace")
    cleaned = apply_rules(text, load_rules(args.glossary))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(cleaned, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Wrap an SRT file as Feishu Doc XML with a preserved text code block."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET


def xml_text(value: str) -> str:
    return escape(value, quote=False)


def attr_text(value: str) -> str:
    return escape(value, quote=True)


def build_xml(srt: str, title: str, caption: str, source_name: str | None, note: str | None) -> str:
    code = "<br/>".join(xml_text(line) for line in srt.splitlines())
    parts = [f"<title>{xml_text(title)}</title>"]
    if source_name:
        parts.append(f"<p>来源文件：{xml_text(source_name)}</p>")
    if note:
        parts.append(f"<p>{xml_text(note)}</p>")
    parts.append(f'<pre lang="text" caption="{attr_text(caption)}"><code>{code}</code></pre>')
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-name")
    parser.add_argument("--note")
    args = parser.parse_args()

    xml = build_xml(
        args.srt.read_text(encoding="utf-8"),
        args.title,
        args.srt.name,
        args.source_name,
        args.note,
    )
    ET.fromstring("<root>" + xml + "</root>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

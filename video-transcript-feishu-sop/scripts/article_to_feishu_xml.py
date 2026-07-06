#!/usr/bin/env python3
"""Wrap a text article and optional SVG as Feishu Doc XML."""

from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET


def xml_text(value: str) -> str:
    return escape(value, quote=False)


def strip_xml_declaration(svg: str) -> str:
    return re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg).strip()


def text_to_blocks(text: str) -> str:
    blocks: list[str] = []
    paragraphs = re.split(r"\n\s*\n", text.strip())
    for para in paragraphs:
        lines = [line.strip() for line in para.splitlines() if line.strip()]
        if not lines:
            continue
        joined = " ".join(lines)
        if joined.startswith("## "):
            blocks.append(f"<h2>{xml_text(joined[3:].strip())}</h2>")
        elif joined.startswith("# "):
            blocks.append(f"<h1>{xml_text(joined[2:].strip())}</h1>")
        elif all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{xml_text(line[2:].strip())}</li>" for line in lines)
            blocks.append(f"<ul>{items}</ul>")
        else:
            blocks.append(f"<p>{xml_text(joined)}</p>")
    return "\n".join(blocks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--svg", type=Path)
    parser.add_argument("--article-format", choices=["text", "xml"], default="text")
    args = parser.parse_args()

    parts = [f"<title>{xml_text(args.title)}</title>"]
    if args.svg:
        svg = strip_xml_declaration(args.svg.read_text(encoding="utf-8"))
        ET.fromstring(svg)
        parts.append(f'<whiteboard type="svg">{svg}</whiteboard>')

    article = args.article.read_text(encoding="utf-8")
    if args.article_format == "xml":
        body = article.strip()
    else:
        body = text_to_blocks(article)
    if body:
        parts.append(body)

    xml = "\n".join(parts) + "\n"
    ET.fromstring("<root>" + xml + "</root>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

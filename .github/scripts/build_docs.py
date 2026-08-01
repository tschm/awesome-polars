#!/usr/bin/env python3
"""Render README.md into the docs/ tree mkdocs builds from.

docs/ is generated and gitignored, so README.md stays the single source of
truth for the list. The site's configuration is not generated — it lives in
mkdocs.yml at the repository root.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

# A bare <div> swallows the Markdown inside it. Tagging the wrappers the README
# uses for centring with `markdown` hands their content back to the parser
# (md_in_html) while keeping the alignment.
DIV_OPEN = re.compile(r"^(\s*<div\b)([^>]*)>\s*$")
# The README carries a hand-maintained table of contents; Material renders its
# own from the headings, so the static copy is redundant here.
TOC_START = re.compile(r"^- \[Awesome Polars\]\(#awesome-polars\)\s*$")


def render_readme() -> str:
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    skipping_toc = False

    for line in lines:
        if TOC_START.match(line):
            skipping_toc = True
            continue
        if skipping_toc:
            # The TOC runs until the first real heading after it.
            if line.startswith("#"):
                skipping_toc = False
            else:
                continue
        div = DIV_OPEN.match(line)
        if div:
            line = f"{div.group(1)}{div.group(2)} markdown>"
        out.append(line)

    return "\n".join(out).strip() + "\n"


def main() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()

    (DOCS / "index.md").write_text(render_readme(), encoding="utf-8")
    shutil.copytree(ROOT / "media", DOCS / "media")

    print(f"wrote {DOCS / 'index.md'} from README.md")


if __name__ == "__main__":
    main()

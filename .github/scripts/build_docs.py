#!/usr/bin/env python3
"""Generate the mkdocs sources for the Awesome Polars site.

Nothing this script writes is committed: ``docs/`` and ``mkdocs.yml`` are
created on the fly by the Pages workflow, built with mkdocs-material and then
thrown away. README.md stays the single source of truth.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

# "owner/repo" when running on GitHub Actions, otherwise fall back to upstream.
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "ddotta/awesome-polars")
OWNER, _, NAME = REPOSITORY.partition("/")

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


def mkdocs_config() -> str:
    return f"""\
site_name: Awesome Polars
site_description: >-
  A curated list of Polars docs, talks, tools, examples & articles
  the internet has to offer.
site_url: https://{OWNER}.github.io/{NAME}/
repo_url: https://github.com/{REPOSITORY}
repo_name: {REPOSITORY}
# Every page comes from README.md, so pin the edit link instead of letting
# MkDocs append the (generated) page path.
edit_uri_template: edit/main/README.md
copyright: Released under the CC BY 4.0 licence

theme:
  name: material
  logo: media/logo_awesome_polars.png
  favicon: media/logo_awesome_polars.png
  icon:
    repo: fontawesome/brands/github
  features:
    - content.action.edit
    - navigation.top
    - navigation.tracking
    - search.highlight
    - search.suggest
    - toc.follow
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: blue
      accent: amber
      toggle:
        icon: material/weather-night
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: blue
      accent: amber
      toggle:
        icon: material/weather-sunny
        name: Switch to light mode

markdown_extensions:
  - attr_list
  - md_in_html
  - toc:
      permalink: true
      toc_depth: 3

plugins:
  - search

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/{REPOSITORY}
      name: Awesome Polars on GitHub
    - icon: fontawesome/solid/bolt
      link: https://pola.rs/
      name: Polars

validation:
  links:
    anchors: warn
    unrecognized_links: warn
"""


def main() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()

    (DOCS / "index.md").write_text(render_readme(), encoding="utf-8")
    shutil.copytree(ROOT / "media", DOCS / "media")
    (ROOT / "mkdocs.yml").write_text(mkdocs_config(), encoding="utf-8")

    print(f"wrote {DOCS / 'index.md'} and {ROOT / 'mkdocs.yml'} for {REPOSITORY}")


if __name__ == "__main__":
    main()

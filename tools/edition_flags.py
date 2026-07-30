#!/usr/bin/env python3
"""Idempotent, fool-proof edits to a single edition's flags in _data/editions.yml.

Used by the lifecycle GitHub Actions so non-technical chairs never hand-edit YAML:

  confirm-acm <year>   Remove `proceedings_series: false` from the edition, so the
                       ACM ICPS line shows (linking to the ACM DLfM conference page
                       until that year's own proceedings page exists).
  add-page <year> <p>  Add page `p` (e.g. `proceedings`) to the edition's `pages:`
                       list, so its nav link / banner target switch on.

Both operations are IDEMPOTENT: if the edition is already in the requested state,
nothing is written and the script exits 0 with a "no change" message. All inputs
are validated (year must be a 4-digit year that exists in the registry); on any
problem the script exits non-zero with a clear message and writes nothing.

Usage:
  python3 tools/edition_flags.py confirm-acm <year>
  python3 tools/edition_flags.py add-page <year> <page>
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDITIONS = ROOT / "_data" / "editions.yml"

# pages the site knows how to render (mirrors the comment in editions.yml)
KNOWN_PAGES = {"call-for-papers", "programme", "proceedings",
               "registration", "venue", "local"}


def die(msg):
    sys.exit(f"error: {msg}")


def load_lines():
    if not EDITIONS.exists():
        die(f"{EDITIONS.relative_to(ROOT)} not found")
    return EDITIONS.read_text(encoding="utf-8").splitlines()


def block_range(lines, year):
    """Return (start, end) line indices for the `- year: <year>` entry, where
    end is exclusive (next `- year:` or EOF). Dies if the year is not found."""
    start = None
    for i, ln in enumerate(lines):
        if re.match(rf"^- year:\s*{year}\s*$", ln):
            start = i
            break
    if start is None:
        die(f"no edition for year {year} in {EDITIONS.relative_to(ROOT)} "
            f"(has rollover run for {year}?)")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^- year:\s*\d+", lines[j]):
            end = j
            break
    return start, end


def write(lines):
    EDITIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def confirm_acm(year):
    lines = load_lines()
    s, e = block_range(lines, year)
    for i in range(s, e):
        if re.match(r"^\s*proceedings_series:\s*false\s*$", lines[i]):
            del lines[i]
            write(lines)
            print(f"confirm-acm {year}: removed `proceedings_series: false` "
                  f"— the ACM ICPS line will now show.")
            return
    print(f"confirm-acm {year}: already confirmed "
          f"(no `proceedings_series: false` present) — no change.")


def add_page(year, page):
    if page not in KNOWN_PAGES:
        die(f"unknown page {page!r}; known pages: {', '.join(sorted(KNOWN_PAGES))}")
    lines = load_lines()
    s, e = block_range(lines, year)
    for i in range(s, e):
        m = re.match(r"^(\s*pages:\s*)\[(.*)\]\s*$", lines[i])
        if m:
            items = [p.strip() for p in m.group(2).split(",") if p.strip()]
            if page in items:
                print(f"add-page {year} {page}: already present in pages "
                      f"{items} — no change.")
                return
            items.append(page)
            lines[i] = f"{m.group(1)}[{', '.join(items)}]"
            write(lines)
            print(f"add-page {year} {page}: pages now {items}.")
            return
    die(f"edition {year} has no `pages:` line to update")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("confirm-acm", help="remove proceedings_series: false")
    p1.add_argument("year")
    p2 = sub.add_parser("add-page", help="add a page to the edition's pages list")
    p2.add_argument("year")
    p2.add_argument("page")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}", str(args.year)):
        die(f"year must be a 4-digit year, got {args.year!r}")

    if args.cmd == "confirm-acm":
        confirm_acm(args.year)
    elif args.cmd == "add-page":
        add_page(args.year, args.page)


if __name__ == "__main__":
    main()

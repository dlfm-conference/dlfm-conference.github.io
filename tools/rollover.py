#!/usr/bin/env python3
"""Roll the site over to the next conference year.

Scaffolds the new edition, registers it, and makes it the current year. Because
every edition lives permanently at /<year>/ and is already in the registry, the
OUTGOING year needs no changes — it moves into "Previous events" automatically
once it is no longer `current_year`.

What it does:
  1. Creates <next>/ from _templates/edition/ (landing, CFP, programme, proceedings)
  2. Creates empty _data/{committee,programme,proceedings,sponsors}/<next>.yml stubs
  3. Prepends a _data/editions.yml entry for <next> (ICPS line off, no
     proceedings page yet — see the two-stage activation below)
  4. Sets current_year: <next> in _config.yml

Edition lifecycle after rollover (both later stages are automatable):
  * rollover          -> ICPS line hidden (`proceedings_series: false`), no
                         Proceedings nav link (proceedings not in `pages`)
  * confirm ICPS      -> remove `proceedings_series: false` (line shows, links
                         to the ACM DLfM conference page as a fallback)
  * publish proceedings-> fill _data/proceedings/<next>.yml and add
                         `proceedings` to `pages` (line links to the page; the
                         Proceedings nav link appears while it is current_year)

Normally run via .github/workflows/rollover.yml (which opens a PR to review);
can also be run locally. Nothing is destructive — the previous year is untouched.

Usage:
  python3 tools/rollover.py <next_year> [--ordinal 14th] [--city "City, Country"] [--dates "..."]
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


def write(p, s):
    path = ROOT / p
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding="utf-8")


def bump_ordinal(o):
    m = re.match(r"(\d+)", o or "")
    if not m:
        return ""
    n = int(m.group(1)) + 1
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("next_year")
    ap.add_argument("--ordinal", default="")
    ap.add_argument("--city", default="")
    ap.add_argument("--dates", default="")
    args = ap.parse_args()
    ny = str(args.next_year).strip()
    if not re.fullmatch(r"\d{4}", ny):
        raise SystemExit(f"next_year must be a 4-digit year, got {ny!r}")
    if (ROOT / ny).exists():
        raise SystemExit(f"{ny}/ already exists — aborting.")

    cfg = read("_config.yml")
    current = re.search(r"current_year:\s*(\d+)", cfg).group(1)
    editions = read("_data/editions.yml")
    cur_ord = re.search(r'ordinal:\s*"([^"]*)"', editions)
    ordinal = args.ordinal or bump_ordinal(cur_ord.group(1) if cur_ord else "")

    # 1. scaffold the edition folder from templates
    for tpl in sorted((ROOT / "_templates" / "edition").glob("*.md")):
        write(f"{ny}/{tpl.name}", tpl.read_text(encoding="utf-8").replace("__YEAR__", ny))

    # 2. data stubs
    for path, body in {
        f"_data/committee/{ny}.yml": f"# DLfM {ny} organising team and programme committee.\nchairs: []\nmembers: []\n",
        f"_data/programme/{ny}.yml": f"# DLfM {ny} programme.\nsessions: []\n",
        f"_data/proceedings/{ny}.yml": f"# DLfM {ny} proceedings.\npapers: []\n",
        f"_data/sponsors/{ny}.yml": f"# DLfM {ny} sponsors — drop logos in assets/sponsors/{ny}/ and list them here.\n",
    }.items():
        write(path, body)

    # 3. prepend the editions.yml entry (before the first existing entry)
    lines = editions.splitlines()
    idx = next(i for i, l in enumerate(lines) if l.startswith("- year:"))
    lines[idx:idx] = [
        f"- year: {ny}",
        f'  ordinal: "{ordinal}"',
        f'  city: "{args.city}"',
        f'  dates: "{args.dates}"',
        # ICPS affiliation is uncertain until it resolves months after the
        # announcement — start with the ACM ICPS line OFF; the "confirm-acm"
        # step removes this once the affiliation is confirmed.
        "  proceedings_series: false",
        "  pages: [call-for-papers, programme]",
        "",
    ]
    write("_data/editions.yml", "\n".join(lines) + "\n")

    # 4. flip the pointer
    write("_config.yml", re.sub(r"current_year:\s*\d+", f"current_year: {ny}", cfg))

    print(f"Rolled over {current} -> {ny} ({ordinal or 'ordinal TBD'}).")
    print(f"  scaffolded {ny}/ (landing, cfp, programme, proceedings)")
    print(f"  added data stubs + editions.yml entry; current_year now {ny}")
    print(f"  {current} remains at /{current}/ and moves into Previous events.")
    print("Next: fill in landing prose, dates/city, committee, programme, sponsors.")


if __name__ == "__main__":
    main()

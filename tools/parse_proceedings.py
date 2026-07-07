#!/usr/bin/env python3
"""Parse a captured DLfM proceedings page into _data/proceedings/<year>.yml.

Handles both capture eras:
  - recent: ### [Title](https://doi.org/10.1145/...)
  - older:  ### <a href="https://dl.acm.org/authorize?N...">Title</a>
Each paper: heading (title + link), one-or-more `- author` bullets, then the
abstract paragraph(s). A "corrigendum" link is pulled into its own field.

Fidelity is verified afterwards by tools/verify_fidelity.py.

Usage: python3 tools/parse_proceedings.py <year>
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clean_inline(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def main():
    year = sys.argv[1]
    md = subprocess.run(["python3", str(ROOT / "tools/clean_pandoc_md.py"),
                         str(ROOT / f"_import/md/{year}/proceedings.md")],
                        capture_output=True, text=True).stdout
    md = re.sub(r"https?://web\.archive\.org/web/\d+/", "", md)
    lines = md.splitlines()

    proc = {"title": "", "note": "", "citation_url": "", "papers": []}
    cur = None
    CORR = re.compile(r"\[([^\]]*corrigendum[^\]]*)\]\((https?://[^)]+)\)", re.I)
    md_head = re.compile(r"^###\s+\[(.+?)\]\((\S+?)\)\s*$")
    a_head = re.compile(r'^###\s+<a\s+href="([^"]+)"[^>]*>(.*?)</a>\s*$', re.S)

    def flush():
        nonlocal cur
        if cur:
            cur["abstract"] = " ".join(cur["abstract"]).strip()
            proc["papers"].append(cur)
            cur = None

    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        m = md_head.match(s)
        a = a_head.match(s) if not m else None
        if m or a:
            flush()
            if m:
                title, url = m.group(1).strip(), m.group(2).strip()
            else:
                url, title = a.group(1).strip(), clean_inline(a.group(2))
            dm = re.search(r"(10\.\d{4,9}/\S+)", url)
            cur = {"title": title, "url": url, "doi": dm.group(1) if dm else "",
                   "authors": [], "abstract": [], "corr_text": "", "corr_url": ""}
            continue
        if cur is None:
            if s.startswith("# DLfM"):
                proc["title"] = s.lstrip("# ").strip()
            elif "Full Citation in the ACM" in s or "Full Text" in s:
                um = re.search(r'href="([^"]+)"', s) or re.search(r"(https?://\S+)", s)
                if um and not proc["citation_url"]:
                    proc["citation_url"] = um.group(1).rstrip('"')
            elif s.startswith("# ") and "Proceedings" in s:
                pass
            elif not s.startswith("<img") and not s.startswith("<a") and not proc["note"]:
                proc["note"] = clean_inline(s)
            continue
        cm = CORR.search(s)
        if cm:
            cur["corr_text"], cur["corr_url"] = cm.group(1).strip(), cm.group(2).strip()
            continue
        if s.startswith("- "):
            cur["authors"].append(clean_inline(s[2:]))
        elif not s.startswith("#"):
            cur["abstract"].append(re.sub(r"<!--.*?-->", "", s).strip())
    flush()

    out = ROOT / f"_data/proceedings/{year}.yml"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# DLfM {year} proceedings — parsed from the frozen capture;\n")
        f.write("# verified by tools/verify_fidelity.py.\n")
        f.write(f"title: |-\n  {proc['title']}\n")
        if proc["citation_url"]:
            f.write(f"citation_url: {proc['citation_url']}\n")
        if proc["note"]:
            f.write(f"note: |-\n  {proc['note']}\n")
        f.write("papers:\n")
        for p in proc["papers"]:
            f.write(f"  - title: |-\n      {p['title']}\n")
            f.write(f"    authors: |-\n      {', '.join(p['authors'])}\n")
            if p["url"]:
                f.write(f"    url: {p['url']}\n")
            if p["corr_url"]:
                f.write(f"    corrigendum_text: |-\n      {p['corr_text']}\n")
                f.write(f"    corrigendum_url: {p['corr_url']}\n")
            f.write(f"    abstract: |-\n      {p['abstract']}\n")
    print(f"{out.relative_to(ROOT)}: {len(proc['papers'])} papers, "
          f"citation={'yes' if proc['citation_url'] else 'no'}")


if __name__ == "__main__":
    main()

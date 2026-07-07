#!/usr/bin/env python3
"""Parse a captured DLfM programme page (HTML-table era, 2020–2025) into
_data/programme/<year>.yml: preamble note, oral sessions (with break rows) and
a poster list. Fidelity is verified afterwards by tools/verify_fidelity.py.

Usage: python3 tools/parse_programme.py <year>
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clean(x):
    x = re.sub(r"<[^>]+>", " ", x).replace("&amp;", "&").replace("&#39;", "'")
    return re.sub(r"\s+", " ", x).strip()


def esc(s):
    return s.replace("\\", "")


def main():
    year = sys.argv[1]
    md = subprocess.run(["python3", str(ROOT / "tools/clean_pandoc_md.py"),
                         str(ROOT / f"_import/md/{year}/programme.md")],
                        capture_output=True, text=True).stdout
    md = re.sub(r"https?://web\.archive\.org/web/\d+/", "", md)

    if "## Oral presentations" in md:
        pre, rest = md.split("## Oral presentations", 1)
    else:
        pre, rest = md.split("<table>", 1) if "<table>" in md else (md, "")
        rest = "<table>" + rest
    note = " ".join(clean(re.sub(r"^#+\s*", "", l)) for l in pre.splitlines()
                    if l.strip() and not re.match(r"^#\s*\d{4}", l.strip()))

    sessions = []
    tbl = rest.split("</table>")[0] if "</table>" in rest else rest
    for tr in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        texts = [clean(c) for c in cells]
        if not any(texts):
            continue
        if len(cells) == 2:
            t0, t1 = texts
            if re.search(r"Session\s*\d", t1):
                sessions.append({"title": t1, "time": t0, "items": []})
            else:
                sessions.append({"break": t1, "time": t0})
        elif len(cells) >= 3:
            typ = clean(re.search(r"<em>(.*?)</em>", cells[1]).group(1)) if "<em>" in cells[1] else ""
            title = clean(re.sub(r"<em>.*?</em>", "", cells[1]))
            item = {"time": texts[0], "type": typ, "title": title, "authors": texts[2]}
            if sessions and "items" in sessions[-1]:
                sessions[-1]["items"].append(item)
            else:
                sessions.append({"items": [item]})

    posters = {"note": "", "items": []}
    pm = re.search(r"###\s+(Poster[^\n]*)\n(.*)", md, re.S)
    if pm:
        posters["note"] = clean(pm.group(1))
        for row in pm.group(2).splitlines():
            m = re.match(r"\|\s*\[(.+?)\]\((.+?)\)\s*\|\s*(.+?)\s*\|", row)
            if m:
                fn = re.search(r"([\w-]+\.pdf)", m.group(2))
                posters["items"].append({"title": m.group(1).strip(),
                    "authors": clean(m.group(3)),
                    "pdf": "/assets/%s/posters/%s" % (year, fn.group(1)) if fn else ""})

    out = ROOT / f"_data/programme/{year}.yml"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# DLfM {year} programme — parsed from the frozen capture;\n")
        f.write("# verified by tools/verify_fidelity.py.\n")
        if note:
            f.write(f"note: |-\n  {esc(note)}\n")
        f.write("sessions:\n")
        for s in sessions:
            if "break" in s:
                f.write(f"  - break: |-\n      {esc(s['break'])}\n    time: \"{s['time']}\"\n")
            else:
                if s.get("title"):
                    f.write(f"  - title: |-\n      {esc(s['title'])}\n    time: \"{s.get('time','')}\"\n    items:\n")
                else:
                    f.write("  - items:\n")
                for it in s["items"]:
                    f.write(f"      - time: \"{it['time']}\"\n")
                    if it["type"]:
                        f.write(f"        type: |-\n          {it['type']}\n")
                    f.write(f"        title: |-\n          {esc(it['title'])}\n")
                    f.write(f"        authors: |-\n          {esc(it['authors'])}\n")
        if posters["items"]:
            f.write(f"posters:\n  note: |-\n    {esc(posters['note'])}\n  items:\n")
            for p in posters["items"]:
                f.write(f"    - title: |-\n        {esc(p['title'])}\n")
                f.write(f"      authors: |-\n        {esc(p['authors'])}\n")
                if p["pdf"]:
                    f.write(f"      pdf: {p['pdf']}\n")
    nt = sum(1 for s in sessions if s.get("title"))
    ni = sum(len(s.get("items", [])) for s in sessions)
    print(f"{out.relative_to(ROOT)}: {nt} sessions, {ni} items, {len(posters['items'])} posters")


if __name__ == "__main__":
    main()

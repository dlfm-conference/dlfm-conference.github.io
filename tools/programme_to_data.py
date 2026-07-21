#!/usr/bin/env python3
"""Convert a prose programme page (<year>/programme.md) into
_data/programme/<year>.yml — the schema rendered by _layouts/programme.html.

Handles the two capture eras seen in the archived pages:
  * markdown pipe tables  (2018, 2019, 2020, 2022)
  * HTML <table>          (2023, 2024)   [2021 is multi-day; handled separately]

Session headers carry an optional "Chair: X" (-> session.chair); talk titles that
link out (e.g. to a DOI) keep the link (-> item.url). The trailing sponsor-logo
block is dropped (chrome). Content is unchanged — verified by verify_fidelity.py.

Usage: python3 tools/programme_to_data.py <year>
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def esc(s):
    return s.replace("\\", "").strip()


def split_link(s):
    """Return (text-with-link-flattened, first-url). Surrounding text is kept."""
    m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", s)
    url = m.group(2).strip() if m else None
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s).strip()
    return text, url


def note_html(text):
    """Preamble note is injected as raw HTML, so turn markdown links into <a>."""
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text).strip()


TRIM = " .|·–—-"


def split_role(raw):
    """('Technological Advances. Chair: J. Downie') -> (title, value, kind).
    kind is 'chair' for an explicit Chair, 'by' for 'Title | Presenters', else None."""
    m = re.search(r"\bchairs?\b[:\s]*", raw, re.I)
    if m:
        return raw[:m.start()].strip(TRIM), raw[m.end():].strip(), "chair"
    if " | " in raw:
        title, _, rest = raw.partition(" | ")
        return title.strip(TRIM), rest.strip(), "by"
    return raw.strip(TRIM), None, None


BREAK_RE = re.compile(r"coffee|lunch|break|registration|welcome|closing|poster slam|"
                      r"social|reception|dinner|opening|wrap-?up", re.I)
TYPE_RE = re.compile(r"^(long|short|full|position|demo|invited)\s+paper$|^poster$", re.I)


def unescape(s):
    return s.replace("\\|", "|").replace("\\[", "[").replace("\\]", "]")


def pipe_cells(line):
    """Split a markdown table row on unescaped pipes, trimming the outer borders."""
    parts = re.split(r"(?<!\\)\|", line.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [unescape(p.strip()) for p in parts]


def split_link_any(cell):
    """Flatten an <a> or [](…) link in a cell; return (text, url)."""
    m = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', cell, re.S)
    if m:
        return strip_tags(m.group(2)), m.group(1)
    m2 = re.search(r"\[([^\]]+)\]\(([^)]+)\)", cell)
    if m2:
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
        return strip_tags(text), m2.group(2).strip()
    return strip_tags(cell), None


# ── pipe-table era (column order varies by year; detect roles by content) ─────
def parse_pipe(section):
    entries = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|?\s*$", line):        # |---|---| separator
            continue
        cells = pipe_cells(line)
        if not cells:
            continue
        time = strip_tags(cells[0].replace("**", ""))
        rest = [c for c in cells[1:]]
        if not any(c.strip() for c in rest):             # blank spacer row
            continue
        if rest and rest[0].startswith("**") and not any(c.strip() for c in rest[1:]):
            raw = strip_tags(rest[0].replace("**", ""))
            entries.append({"kind": "header", "raw": raw, "time": time, "items": []})
            continue
        # talk row: pull out the type cell, then title (linked/first) vs authors
        typ, content = "", []
        for c in rest:
            if not c.strip():
                continue
            if TYPE_RE.match(strip_tags(c)):
                typ = strip_tags(c)
            else:
                content.append(c)
        title, url, authors = "", None, ""
        linked = [c for c in content if re.search(r"\[[^\]]+\]\([^)]+\)|<a\b", c)]
        if linked:
            title, url = split_link_any(linked[0])
            others = [c for c in content if c is not linked[0]]
            authors = strip_tags(others[0]) if others else ""
        elif content:
            title = strip_tags(content[0])
            authors = strip_tags(content[1]) if len(content) > 1 else ""
        item = {"time": time, "type": typ, "title": title, "url": url, "authors": authors}
        if entries and entries[-1]["kind"] == "header":
            entries[-1]["items"].append(item)
        else:
            entries.append({"kind": "anon", "items": [item]})
    return finalise(entries)


# ── HTML-table era ──────────────────────────────────────────────────────────
def parse_html(section):
    tbl = section.split("</table>")[0]
    entries = []
    for tr in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if not cells:
            continue
        texts = [strip_tags(c) for c in cells]
        if not any(texts):
            continue
        colspan = any('colspan' in m for m in re.findall(r"<td([^>]*)>", tr))
        header = ("<strong>" in cells[-1] and
                  re.search(r"session\s*\d|chair", texts[-1], re.I))
        if header:
            raw = strip_tags(re.sub(r"</?strong>", "", cells[-1]))
            entries.append({"kind": "header", "raw": raw, "time": texts[0], "items": []})
        elif colspan and len(texts) >= 1:
            # colspan row without a strong session marker = break / notice
            entries.append({"kind": "header", "raw": texts[-1], "time": texts[0], "items": []})
        else:
            title, url = split_link_html(cells[1] if len(cells) > 1 else "")
            typ = ""
            em = re.search(r"<em>(.*?)</em>", cells[1] if len(cells) > 1 else "", re.S)
            if em:
                typ = strip_tags(em.group(1))
            item = {"time": texts[0], "type": typ, "title": title, "url": url,
                    "authors": texts[2] if len(texts) > 2 else ""}
            if entries and entries[-1]["kind"] == "header":
                entries[-1]["items"].append(item)
            else:
                entries.append({"kind": "anon", "items": [item]})
    return finalise(entries)


def split_link_html(cell):
    m = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', cell, re.S)
    if m:
        title = strip_tags(re.sub(r"<em>.*?</em>", "", m.group(2), flags=re.S))
        return title, m.group(1)
    return strip_tags(re.sub(r"<em>.*?</em>", "", cell, flags=re.S)), None


def finalise(entries):
    """Turn ordered header/anon entries into sessions + break markers."""
    sessions = []
    for e in entries:
        items = e.get("items", [])
        if e["kind"] == "anon":
            sessions.append({"anon": True, "items": items})
            continue
        raw = e["raw"]
        if not items and BREAK_RE.search(raw) and not re.search(r"session\s*\d", raw, re.I):
            sessions.append({"break": raw, "time": e["time"]})
        else:
            title, val, kind = split_role(raw)
            s = {"title": title, "time": e["time"], "items": items}
            if kind:
                s[kind] = val
            sessions.append(s)
    return sessions


# ── posters ──────────────────────────────────────────────────────────────────
def parse_posters(section, year):
    note = ""
    mh = re.match(r"#+\s*(.+)", section.strip())
    if mh:
        note = strip_tags(mh.group(1))
    items = []
    if "<table>" in section:
        tbl = section.split("<table>", 1)[1].split("</table>")[0]
        for tr in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
            if len(cells) < 2:
                continue
            title, url = split_link_html(cells[0])
            authors = strip_tags(cells[1])
            if not title:
                continue
            items.append({"title": title, "authors": authors, "pdf": local_pdf(url, year)})
    else:
        for line in section.splitlines():
            if not line.strip().startswith("|"):
                continue
            if re.match(r"^\|[\s:|-]+\|?\s*$", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2 or not any(cells):
                continue
            title, url = split_link(cells[0])
            items.append({"title": strip_tags(title), "authors": strip_tags(cells[1]),
                          "pdf": local_pdf(url, year)})
    return {"note": note, "items": items}


def local_pdf(url, year):
    if not url:
        return None
    if url.startswith("/assets"):
        return url
    m = re.search(r"([\w.-]+\.pdf)", url)
    if m and (ROOT / "assets" / year / "posters" / m.group(1)).exists():
        return f"/assets/{year}/posters/{m.group(1)}"
    return url          # not yet rehosted — keep the original link


# ── YAML emission ─────────────────────────────────────────────────────────────
def blk(indent, key, val):
    return f"{indent}{key}: |-\n{indent}  {esc(val)}\n"


def main():
    year = sys.argv[1]
    body = (ROOT / year / "programme.md").read_text(encoding="utf-8")
    body = re.split(r"^---\s*$", body, maxsplit=2, flags=re.M)[-1]
    # drop trailing sponsor / chrome block
    body = re.split(r"\n#*\s*DLfM \d{4} is kindly supported|is kindly supported by|"
                    r"\n\s*<img ", body)[0]

    # split preamble | oral | posters
    parts = re.split(r"^##\s*Oral presentations\s*$", body, maxsplit=1, flags=re.M)
    if len(parts) == 2:
        preamble, rest = parts
    else:
        # no "Oral presentations" heading: preamble ends at first table
        m = re.search(r"(^\|)|(<table>)", body, re.M)
        preamble, rest = (body[:m.start()], body[m.start():]) if m else (body, "")

    pm = re.split(r"^###\s*Poster", rest, maxsplit=1, flags=re.M)
    oral = pm[0]
    posters_sec = ("### Poster" + pm[1]) if len(pm) == 2 else ""

    note_lines = []
    for l in preamble.splitlines():
        s = l.strip()
        if not s or re.match(r"^#+\s", s) or re.match(r"^-\s*\[[^\]]+\]\(#", s):
            continue
        note_lines.append(re.sub(r"^[-*]\s+", "", s))
    note = note_html(" ".join(note_lines))

    sessions = parse_html(oral) if "<table>" in oral else parse_pipe(oral)
    posters = parse_posters(posters_sec, year) if posters_sec else None

    out = [f"# DLfM {year} programme — converted from the archived page;",
           "# rendered by _layouts/programme.html, verified by tools/verify_fidelity.py."]
    if note:
        out.append(f'note: "{note}"' if '"' not in note else f"note: '{note}'")
    out.append("sessions:")
    for s in sessions:
        if "break" in s:
            out.append(f'  - break: |-\n      {esc(note_html(s["break"]))}')
            out.append(f'    time: "{s["time"]}"')
            continue
        if s.get("anon"):
            out.append("  - items:")
        else:
            out.append(f'  - title: |-\n      {esc(s["title"])}')
            if s.get("chair"):
                out.append(f'    chair: |-\n      {esc(s["chair"])}')
            if s.get("by"):
                out.append(f'    by: |-\n      {esc(s["by"])}')
            if s.get("time"):
                out.append(f'    time: "{s["time"]}"')
            out.append("    items:")
        for it in s["items"]:
            out.append(f'      - time: "{it["time"]}"')
            if it["type"]:
                out.append(f'        type: |-\n          {esc(it["type"])}')
            out.append(f'        title: |-\n          {esc(it["title"])}')
            if it.get("url"):
                out.append(f'        url: "{it["url"]}"')
            if it["authors"]:
                out.append(f'        authors: |-\n          {esc(it["authors"])}')
    if posters and posters["items"]:
        out.append(f'posters:\n  note: |-\n    {esc(posters["note"])}\n  items:')
        for p in posters["items"]:
            out.append(f'    - title: |-\n        {esc(p["title"])}')
            if p["authors"]:
                out.append(f'      authors: |-\n        {esc(p["authors"])}')
            if p.get("pdf"):
                out.append(f'      pdf: {p["pdf"]}')

    (ROOT / "_data/programme" / f"{year}.yml").write_text("\n".join(out) + "\n", encoding="utf-8")
    ns = sum(1 for s in sessions if s.get("title"))
    ni = sum(len(s.get("items", [])) for s in sessions)
    nb = sum(1 for s in sessions if "break" in s)
    npost = len(posters["items"]) if posters else 0
    print(f"_data/programme/{year}.yml: {ns} sessions, {ni} items, {nb} breaks, {npost} posters")


if __name__ == "__main__":
    main()

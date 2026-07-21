#!/usr/bin/env python3
"""Build an archived edition LANDING page from a frozen capture, applying the
same structure as the current edition:
  - hero supplies title/date (so the leading <h1> + date subheading are dropped)
  - section headers normalised to Title Case
  - "Conference Organization" (chairs + programme committee) lifted into
    _data/committee/<year>.yml and rendered by the committee include
  - the trailing Host/Sponsors logo block is removed from prose (sponsors go in
    the hero via _data/sponsors/<year>.yml) and its logo URLs are reported so
    they can be downloaded

Content words are unchanged — verified by tools/verify_fidelity.py.

Usage: python3 tools/make_landing.py <year> "<title>"
"""
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import linkfix

ROOT = Path(__file__).resolve().parent.parent


def kramdown_id(t):
    t = re.sub(r"<[^>]+>", "", t).lower()
    t = re.sub(r"[^a-z0-9 -]", "", t)
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", t.strip())).strip("-")
MINOR = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of",
         "on", "or", "the", "to", "with", "via"}
ACR = {"AI", "ACM", "MIR", "ISMIR", "IAML", "DLFM", "RDF", "MEI", "OMR", "IEEE"}
CHAIR_ROLES = {"Programme Chair", "General Chair", "Proceedings Chair",
               "Local Chair", "Programme Co-Chair", "General Co-Chair"}
PLAIN_H2 = {"IMPORTANT DATES", "REGISTRATION", "SUBMISSIONS", "LOCATION",
            "TOPICS", "BACKGROUND"}


def tc(s):
    out = []
    for i, w in enumerate(s.split()):
        if w.strip(",:().").upper() in ACR:
            out.append(w)
        elif i > 0 and w.lower().strip(",:") in MINOR:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:].lower() if w.isupper() else w[:1].upper() + w[1:])
    return " ".join(out)


def q(x):
    x = re.sub(r"\\([\\|`*_{}\[\]()#+.!~'\"-])", r"\1", x)   # drop pandoc escapes
    x = x.replace("\\", "\\\\").replace('"', '\\"')          # then YAML-safe
    return '"' + x + '"'


def main():
    year, title = sys.argv[1], sys.argv[2]
    md = subprocess.run(["python3", str(ROOT / "tools/clean_pandoc_md.py"),
                         str(ROOT / f"_import/md/{year}/landing.md")],
                        capture_output=True, text=True).stdout
    md = linkfix.normalise(md)   # repoint old-CMS URLs + fix verbatim autolinks

    # split off Sponsors / Host Institution logo block (report its logos)
    logos = []
    m = re.search(r"\n#+\s*(Host Institution|Sponsors|Supported by)\b", md, re.I)
    if m:
        tail = md[m.start():]
        md = md[:m.start()]
        for im in re.finditer(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', tail):
            logos.append((im.group(1), im.group(2)))

    # split off Conference Organization -> committee data
    om = re.search(r"\n#+\s*(conference organi[sz]ation|organising committee|"
                   r"programme committee|committee)\b", md, re.I)
    chairs, members = [], []
    if om:
        org = md[om.start():]
        md = md[:om.start()]
        role, in_members = None, False
        for l in org.splitlines():
            s = l.strip()
            if not s:
                continue
            h = re.match(r"^#+\s+(.*)$", s)
            if h:                                     # heading resets context
                t = h.group(1).strip()
                if re.search(r"programme committ|committee member", t, re.I):
                    in_members, role = True, None
                elif re.search(r"chair", t, re.I):
                    in_members, role = False, t       # any chair role label
                else:
                    in_members, role = False, None    # parent / other heading
                continue
            if "<img" in s or s.startswith("<") or "](http" in s \
                    or re.search(r"steering committee|contact|e-?mail|@|supported by|<u>|<a\s|http",
                                 s, re.I):
                continue                              # skip logos / links / notes / contacts
            s = re.sub(r"^[-*]\s+", "", s)            # strip bullet
            name, _, aff = s.partition(",")
            if in_members:
                members.append((name.strip(), aff.strip()))
            elif role:                                # keep role across multiple names
                chairs.append((role, name.strip(), aff.strip()))
        if chairs or members:
            with open(ROOT / f"_data/committee/{year}.yml", "w", encoding="utf-8") as f:
                f.write(f"# DLfM {year} organising team and programme committee.\n")
                if chairs:
                    f.write("chairs:\n")
                    for r, n, a in chairs:
                        f.write(f"  - role: {r}\n    name: {q(n)}\n    affiliation: {q(a)}\n")
                if members:
                    f.write("\nmembers:\n")
                    for n, a in members:
                        f.write(f"  - name: {q(n)}\n    affiliation: {q(a)}\n")

    # Drop the leading H1; keep the whole run of leading #### subheadings
    # (date / venue / association) as lead paragraphs — NOT headings, so they
    # don't become spurious jump-bar entries. Title-case the real section headers.
    lines, body, dropped_h1, lead_in = md.splitlines(), [], False, False
    for l in lines:
        s = l.strip()
        if not dropped_h1:
            if s.startswith("# "):
                dropped_h1 = lead_in = True
                continue
            if s == "":
                body.append(l); continue
        if lead_in:
            if s == "":
                body.append(l); continue
            if s.startswith("#### "):
                body.append(re.sub(r"^#### ", "", l))   # subheading -> lead paragraph
                continue
            lead_in = False                             # first ## / content ends the lead-in
        m2 = re.match(r"^(#{2,5})\s+(.*)$", l)
        if m2:
            lvl = "##" if len(m2.group(1)) <= 4 else "###"
            body.append(f"{lvl} {tc(m2.group(2))}")
        elif s in PLAIN_H2 or s.rstrip(":") in PLAIN_H2 or (s.isupper() and 4 < len(s) < 40 and s[0].isalpha()):
            body.append(f"## {tc(s)}")
        else:
            body.append(l)

    # Rewrite in-page anchor links (#Dates, #Submissions…) to the target
    # heading's kramdown id, so they aren't broken.
    heads = [(kramdown_id(mm.group(1)), mm.group(1).lower())
             for line in body for mm in [re.match(r"^#{2,4} (.+)$", line)] if mm]
    text = "\n".join(body)
    for a in set(re.findall(r"\]\(#([^)]+)\)", text)):
        key = re.split(r"[ -]", urllib.parse.unquote(a).lower().strip())[0]
        tgt = next((hid for hid, ht in heads if key and key in ht), None)
        if tgt and tgt != a:
            text = text.replace(f"](#{a})", f"](#{tgt})")
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

    fm = (f"---\nlayout: landing\nrole: landing\nyear: {year}\n"
          f'title: "{title}"\n---\n\n* TOC\n{{:toc}}\n\n')
    (ROOT / year).mkdir(exist_ok=True)
    (ROOT / year / "index.md").write_text(fm + text, encoding="utf-8")
    print(f"wrote {year}/index.md ({len(text.split())} words); "
          f"committee {len(chairs)} chairs / {len(members)} members")
    if logos:
        print("SPONSOR/HOST logos to rehost:")
        for url, alt in logos:
            print(f"  {alt}  <-  {url.split('?')[0]}")


if __name__ == "__main__":
    main()

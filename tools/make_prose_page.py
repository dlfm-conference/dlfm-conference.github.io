#!/usr/bin/env python3
"""Build an archived edition prose page from a frozen capture.

Cleans the pandoc capture, strips Wayback prefixes, downloads any old-CMS assets
(PDFs/images/docs) into assets/<year>/files/ and repoints them locally, repoints
old-CMS year subpage links to the new site, drops the leading <h1> (the page
header supplies it), and writes the page with front matter. Content words are
unchanged — verified afterwards by tools/verify_fidelity.py.

Usage:
  python3 tools/make_prose_page.py <year> <src-slug> <out-slug> <layout> <role> <title>
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBPAGES = ["programme", "proceedings", "registration", "venue"]


def main():
    year, src, out_slug, layout, role, title = sys.argv[1:7]
    md = subprocess.run(["python3", str(ROOT / "tools/clean_pandoc_md.py"),
                         str(ROOT / f"_import/md/{year}/{src}.md")],
                        capture_output=True, text=True).stdout
    md = re.sub(r"https?://web\.archive\.org/web/\d+/", "", md)
    # drop the repeated site-wide Host/Sponsors logo block (chrome)
    md = re.split(r"\n#+\s*(?:Host Institution|Sponsors)\b", md)[0]

    # download + localise old-CMS assets
    files_dir = ROOT / "assets" / year / "files"
    asset_re = re.compile(r"https://dlfm\.web\.ox\.ac\.uk/[^\s\")]+?\.(?:pdf|docx?|jpe?g|png|gif|webp)",
                          re.I)
    seen = {}
    for url in dict.fromkeys(asset_re.findall(md)):
        base = re.sub(r"\?.*$", "", url.split("/")[-1])
        if url not in seen:
            files_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(["curl", "-sSL", "-o", str(files_dir / base), url], check=False)
            seen[url] = f"/assets/{year}/files/{base}"
    # rewrite full URLs (incl. any ?query) to local paths
    for url, local in seen.items():
        md = re.sub(re.escape(url) + r"[^\s\")]*", local, md)

    # repoint old-CMS year subpage links (/2024-programme -> /2024/programme/)
    for sp in SUBPAGES:
        md = md.replace(f"https://dlfm.web.ox.ac.uk/{year}-{sp}", f"/{year}/{sp}/")

    # drop the leading H1 (page header supplies the title)
    lines = md.splitlines()
    dropped = False
    body = []
    for ln in lines:
        if not dropped and ln.strip().startswith("# "):
            dropped = True
            continue
        body.append(ln)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(body)).strip() + "\n"

    fm = f"---\nlayout: {layout}\nrole: {role}\nyear: {year}\ntitle: {title}\n---\n\n"
    (ROOT / year).mkdir(exist_ok=True)
    (ROOT / year / f"{out_slug}.md").write_text(fm + text, encoding="utf-8")
    print(f"wrote {year}/{out_slug}.md ({len(text.split())} words, "
          f"{len(seen)} assets rehosted)")


if __name__ == "__main__":
    main()

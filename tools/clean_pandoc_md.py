#!/usr/bin/env python3
"""Strip Oxford Mosaic / Google-Docs cruft from a pandoc-GFM capture.

Reduces `_import/md/<year>/<page>.md` to clean Markdown a human can finish into
site content, WITHOUT touching the words (fidelity is still verified afterwards
by tools/verify_fidelity.py). It only removes markup noise:
  - wrapper <div>…</div> and <span>…</span> tags (keeping their text)
  - style="…" / class="…" / id="…" attributes
  - empty raw-HTML lines and runs of blank lines

Usage: python3 tools/clean_pandoc_md.py <in.md>   # writes cleaned Markdown to stdout
"""
import re
import sys

SUB = [
    (re.compile(r'</?(div|span)\b[^>]*>'), ''),        # drop div/span tags, keep text
    (re.compile(r'\s(style|class|id|data-[\w-]+)="[^"]*"'), ''),  # drop noisy attrs
    (re.compile(r'\s(style|class|id)=\'[^\']*\''), ''),
    (re.compile(r'<a\s+>'), ''),                        # anchors stripped bare of href
    (re.compile(r'&#39;'), "'"),
    (re.compile(r'&quot;'), '"'),
    (re.compile(r'&amp;'), '&'),
]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: clean_pandoc_md.py <in.md>")
    text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    for rx, repl in SUB:
        text = rx.sub(repl, text)
    # drop lines that are now empty raw-HTML remnants or lone punctuation
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s in ("", "<a>", "</a>", "\\", "|"):
            out.append("")
        else:
            out.append(line.rstrip())
    # collapse 3+ blank lines to one
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
    sys.stdout.write(text)


if __name__ == "__main__":
    main()

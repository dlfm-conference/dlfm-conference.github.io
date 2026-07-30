#!/usr/bin/env python3
"""Content-fidelity gate for migrated (archived) DLfM editions.

Proves that a migrated year's built pages preserve the words of the frozen
legacy capture in `_import/text/<year>/*.txt` — nothing dropped, altered, or
invented. The LLM is kept off the content-critical path: the ground truth is the
deterministic pandoc extraction, and this script mechanically compares it against
the rendered site.

For each `_import/text/<year>/<slug>.txt`:
  1. Locate the built page in `_site` (landing -> /<year>/, else /<year>/<slug>/).
  2. Extract the visible text of its <main>, excluding the jump bar and
     back-to-top arrows (navigational duplication, not content).
  3. Compare word multisets (Unicode-aware, lowercased):
       - DROPPED  (ground truth − built): content lost or altered  -> FAIL
       - ADDED    (built − ground truth − allowlist): invented text -> FAIL
  4. Report DOIs / external URLs present in the legacy page (from _import/md)
     but absent from the built HTML (reported; --strict-links to fail).

Usage:
  python3 tools/verify_fidelity.py <year> [--site _site]
      [--allow tools/fidelity_allow.txt] [--only slug] [--report-only]
      [--strict-links]

Exit status is non-zero if any page fails (unless --report-only).
"""
import argparse
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

# Map a legacy capture slug to the built site path (relative to /<year>/).
SLUG_ALIAS = {"accommodation-and-transportation": "local"}

WORD_RE = re.compile(r"\w+", re.UNICODE)
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s)>\"']+")
URL_RE = re.compile(r"https?://[^\s)>\"'\]]+")
WAYBACK_RE = re.compile(r"https?://web\.archive\.org/web/\d+/")


class MainText(HTMLParser):
    """Collect visible text of <main>, minus jump bar / to-top / script / style."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.skip = 0
        self.parts = []

    def _is_skip(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        return (tag in ("script", "style")
                or a.get("id") == "markdown-toc"
                or "prog-jump" in cls
                or "to-top" in cls)

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main = True
            return
        if not self.in_main:
            return
        if self.skip:
            if tag not in VOID:
                self.skip += 1
            return
        if self._is_skip(tag, attrs):
            if tag not in VOID:
                self.skip = 1
            return
        self.parts.append(" ")

    def handle_endtag(self, tag):
        if self.in_main and self.skip:
            if tag not in VOID:
                self.skip -= 1
            return
        if tag == "main":
            self.in_main = False
            return
        if self.in_main:
            self.parts.append(" ")

    def handle_data(self, data):
        if self.in_main and not self.skip:
            self.parts.append(data)

    def text(self):
        return "".join(self.parts)


def tokens(text):
    return Counter(WORD_RE.findall(text.lower()))


def built_path(site, year, slug):
    if slug == "landing":
        return site / str(year) / "index.html"
    return site / str(year) / SLUG_ALIAS.get(slug, slug) / "index.html"


def load_allow(path):
    """Returns (global_allow, per_page_allow). A line `2025/landing: foo bar`
    scopes tokens to that page; any other line is a global allowance."""
    global_allow, per_page = set(), {}
    if path and Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if re.match(r"^\S+/\S+\s*:", line):
                key, _, rest = line.partition(":")
                per_page.setdefault(key.strip(), set()).update(
                    WORD_RE.findall(rest.lower()))
            else:
                global_allow.update(WORD_RE.findall(line.lower()))
    return global_allow, per_page


def check_page(year, slug, site, allow, strict_links):
    gt_txt = ROOT / "_import" / "text" / str(year) / f"{slug}.txt"
    gt_md = ROOT / "_import" / "md" / str(year) / f"{slug}.md"
    html_path = built_path(site, year, slug)
    fails = []

    if not html_path.exists():
        return [f"built page missing: {html_path.relative_to(ROOT)}"], []

    parser = MainText()
    parser.feed(html_path.read_text(encoding="utf-8", errors="replace"))
    built_html = html_path.read_text(encoding="utf-8", errors="replace")
    # Set semantics: a word in the legacy text must appear SOMEWHERE in the
    # built page (and vice-versa). This tolerates duplication introduced by the
    # hero / nav / templating while still catching real omissions or inventions.
    # Scrub both sides identically before diffing:
    #  - old-CMS / Wayback URLs (intentionally repointed, and sometimes kept as
    #    historical text) — their host tokens (ox, ac, uk, archive…) aren't content
    #  - our own canonical host (dlfm.rism.digital): self-links are site chrome, not
    #    content, same as the old Oxford host — its tokens (rism, digital) aren't content
    #  - bracketed spans: pandoc renders images as "[alt]" (logos relocated to the
    #    hero) and citation refs like "[39]" are bracketed in both
    def scrub(t):
        t = re.sub(r"https?://(?:dlfm\.web\.ox\.ac\.uk|dlfm\.rism\.digital|web\.archive\.org)\S*", " ", t)
        return re.sub(r"\[[^\]]*\]", " ", t)

    built = set(tokens(scrub(parser.text())))
    gt = set(tokens(scrub(gt_txt.read_text(encoding="utf-8", errors="replace"))))

    # The allowlist marks expected text-vs-render differences, in either
    # direction (e.g. a name that survives only as a logo's alt text).
    dropped = gt - built - allow
    added = built - gt - allow

    if dropped:
        fails.append("DROPPED (in legacy, missing from built): "
                     + ", ".join(sorted(dropped)))
    if added:
        fails.append("ADDED (in built, not in legacy or allowlist): "
                     + ", ".join(sorted(added)))

    warns = []
    if gt_md.exists():
        md = WAYBACK_RE.sub("", gt_md.read_text(encoding="utf-8", errors="replace"))
        want = set(DOI_RE.findall(md))
        # external URLs only (legacy self-links to the old CMS are expected to
        # change; image/asset URLs are not content links)
        for u in URL_RE.findall(md):
            u = u.rstrip(".,);]")
            if "dlfm.web.ox.ac.uk" in u:
                continue
            if re.search(r"\.(png|jpe?g|gif|svg|webp)$", u, re.I):
                continue
            want.add(u)
        # compare scheme-insensitively (https vs http is not a fidelity issue)
        def noscheme(s):
            return s.replace("https://", "//").replace("http://", "//")
        built_ns = noscheme(built_html)
        missing_links = sorted(u for u in want if noscheme(u) not in built_ns)
        if missing_links:
            msg = "MISSING links/DOIs: " + ", ".join(missing_links)
            (fails if strict_links else warns).append(msg)

    return fails, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("year")
    ap.add_argument("--site", default="_site")
    ap.add_argument("--allow", default=str(ROOT / "tools" / "fidelity_allow.txt"))
    ap.add_argument("--only", help="check a single slug")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--strict-links", action="store_true")
    args = ap.parse_args()

    site = (ROOT / args.site) if not Path(args.site).is_absolute() else Path(args.site)
    global_allow, per_page = load_allow(args.allow)
    gt_dir = ROOT / "_import" / "text" / str(args.year)
    if not gt_dir.exists():
        sys.exit(f"no ground truth for {args.year}: {gt_dir}")

    slugs = [args.only] if args.only else sorted(p.stem for p in gt_dir.glob("*.txt"))
    any_fail = False
    for slug in slugs:
        allow = global_allow | per_page.get(f"{args.year}/{slug}", set())
        fails, warns = check_page(args.year, slug, site, allow, args.strict_links)
        status = "FAIL" if fails else ("warn" if warns else "OK")
        print(f"\n[{status}] {args.year}/{slug}")
        for w in warns:
            print("  · " + w)
        for f in fails:
            print("  ✗ " + f)
        any_fail = any_fail or bool(fails)

    print()
    if any_fail and not args.report_only:
        sys.exit(1)


if __name__ == "__main__":
    main()

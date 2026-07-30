#!/usr/bin/env python3
"""Generate or enrich _data/proceedings/<year>.yml from an ACM proceedings DOI.

Two modes:

* GENERATE (default; used by the "publish proceedings" Action for a NEW year):
  Policy P2 (faithfulness-first) — writes the *authoritative skeleton* only: each
  paper's exact title, ordered authors (with ORCID iDs where ACM/Crossref carry
  them), and DOI, all verbatim from Crossref. It writes NO abstracts: the verbatim
  text lives on the Cloudflare-walled ACM page (unfetchable unattended) and
  OpenAlex reconstructions are silently truncated ~25% of the time. Each paper
  links to its ACM DOI, where the canonical abstract lives; verbatim abstracts are
  a later maintainer-run top-up.

* ENRICH (`--enrich`; for years that ALREADY have a proceedings file, e.g. to add
  ORCID iDs): loads the existing file and changes ONLY the authors — turning each
  `authors` string into a structured list of {name, orcid}, attaching ORCIDs from
  Crossref by position. Existing author *names*, titles, abstracts and every other
  field are preserved byte-for-byte in meaning, so gate-verified years stay green.
  If the existing name count for a paper doesn't match Crossref, that paper's names
  are left exactly as-is with no ORCIDs (and a warning is printed) rather than risk
  a mis-alignment. Requires PyYAML (only this mode does).

Enumeration (robust for any year): ACM paper DOIs are `<volumeDOI>.<suffix>`, the
suffixes contiguous within a volume but not always starting at volume+1. We seed
from a Crossref `query.container-title` search (filtered to this volume's DOI
prefix), fall back to probing volume+1, then walk contiguously past both ends as a
completeness backstop. Result is cross-checked (contiguous span vs count).

Idempotent: same inputs -> byte-identical output.

Usage:
  python3 tools/proceedings_from_doi.py <year> <acm_proceedings_doi> [--out PATH]
  python3 tools/proceedings_from_doi.py <year> <acm_proceedings_doi> --enrich [--out PATH]
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAILTO = "weigl@mdw.ac.at"
UA = "dlfm-website-proceedings/1.0 (+https://dlfm.rism.digital)"
CROSSREF = "https://api.crossref.org"
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DOI_IN_URL = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+")


def die(msg):
    sys.exit(f"error: {msg}")


def rel(p):
    """Repo-relative display path, or the plain path if it's outside the repo."""
    try:
        return p.relative_to(ROOT)
    except ValueError:
        return p


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def crossref_work(doi):
    url = f"{CROSSREF}/works/{urllib.parse.quote(doi)}?mailto={MAILTO}"
    try:
        return get_json(url)["message"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def norm_orcid(o):
    if not o:
        return None
    o = o.strip().replace("http://", "https://")
    if not o.startswith("https://orcid.org/"):
        m = re.search(r"(\d{4}-\d{4}-\d{4}-[\dX]{3}[\dX])", o)
        o = "https://orcid.org/" + m.group(1) if m else o
    return o.rstrip("/")


def crossref_authors(work):
    """Ordered list of {name, orcid?} from a Crossref work."""
    out = []
    for a in work.get("author", []):
        name = " ".join(p for p in (a.get("given", ""), a.get("family", "")) if p).strip()
        if not name:
            continue
        rec = {"name": name}
        oc = norm_orcid(a.get("ORCID"))
        if oc:
            rec["orcid"] = oc
        out.append(rec)
    return out


def enumerate_papers(vol_doi, vol_title):
    prefix = vol_doi + "."
    volnum = vol_doi.rsplit("/", 1)[-1]
    suffixes = set()
    # (1) seed from container-title search
    try:
        q = urllib.parse.urlencode({
            "query.container-title": vol_title, "filter": "type:proceedings-article",
            "rows": "500", "select": "DOI", "mailto": MAILTO})
        for it in get_json(f"{CROSSREF}/works?{q}")["message"]["items"]:
            d = it["DOI"]
            if d.startswith(prefix) and d[len(prefix):].isdigit():
                suffixes.add(int(d[len(prefix):]))
    except Exception as e:
        print(f"  note: container-title search failed ({e}); relying on DOI walk.",
              file=sys.stderr)
    # (2) fallback seed: probe volume+1 (common contiguous case)
    if volnum.isdigit() and crossref_work(f"{prefix}{int(volnum)+1}") is not None:
        suffixes.add(int(volnum) + 1)
    if not suffixes:
        die(f"could not locate any papers for volume {vol_doi}. The volume may be "
            f"too new for Crossref, or this isn't the proceedings DOI.")

    lo, hi = min(suffixes), max(suffixes)
    MISS_STOP = 3

    def exists(n):
        time.sleep(0.3)
        return crossref_work(f"{prefix}{n}") is not None

    n, misses = lo - 1, 0
    while misses < MISS_STOP and n > lo - 50:
        if exists(n):
            suffixes.add(n); misses = 0
        else:
            misses += 1
        n -= 1
    n, misses = hi + 1, 0
    while misses < MISS_STOP:
        if exists(n):
            suffixes.add(n); misses = 0
        else:
            misses += 1
        n += 1

    ordered = sorted(suffixes)
    gaps = [x for x in range(ordered[0], ordered[-1] + 1) if x not in suffixes]
    if gaps:
        print(f"  note: {len(gaps)} interior DOI gap(s) in "
              f"[{ordered[0]}..{ordered[-1]}] (ACM skips numbers).", file=sys.stderr)
    return [f"{prefix}{n}" for n in ordered]


def volume_title(year, raw):
    raw = (raw or "").strip()
    if raw.lower().startswith("dlfm"):
        return raw
    return f"DLfM '{str(year)[2:]}: {raw}"


# ── YAML emission (house style: `|-` block scalars, structured authors) ──────
def yqstr(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def block_scalar(key, value, indent, dash=False):
    lead = " " * (indent - 2) + "- " if dash else " " * indent
    body = " " * (indent + 2)
    out = [f"{lead}{key}: |-"]
    out += [body + ln for ln in str(value).split("\n")]
    return "\n".join(out)


def emit_authors(authors, indent):
    """authors: a string (legacy) or a list of {name, orcid?}."""
    if isinstance(authors, str):
        return block_scalar("authors", authors, indent)
    pad = " " * indent
    item = " " * (indent + 2)
    lines = [f"{pad}authors:"]
    for a in authors:
        lines.append(f"{item}- name: {yqstr(a['name'])}")
        if a.get("orcid"):
            lines.append(f"{item}  orcid: {a['orcid']}")
    return "\n".join(lines)


# Field emission order; TEXT fields use `|-` block scalars (safe for any chars),
# everything else is a plain scalar. Unknown keys are preserved (appended in
# encounter order) so enrich never silently drops a field it doesn't know about.
TOP_ORDER = ["title", "intro", "note", "publisher", "citation_url", "citation_doi", "doi"]
PAPER_ORDER = ["title", "authors", "url", "doi", "pages",
               "corrigendum_url", "corrigendum_text", "abstract", "abstract_source"]
TEXT_FIELDS = {"title", "intro", "note", "publisher", "corrigendum_text", "abstract"}


def emit_field(key, value, indent, dash=False):
    if key == "authors":
        return emit_authors(value, indent)
    if key in TEXT_FIELDS or (isinstance(value, str) and "\n" in value):
        return block_scalar(key, value, indent, dash=dash)
    lead = " " * (indent - 2) + "- " if dash else " " * indent
    return f"{lead}{key}: {value}"


def emit(year, top, papers, doi, generated_from):
    lines = []
    if generated_from:
        lines += [
            f"# DLfM {year} proceedings — paper list/authors/DOIs from Crossref (verbatim).",
            f"# Abstracts omitted pending a verbatim top-up from the ACM DL.",
            f"# Generated by tools/proceedings_from_doi.py from {generated_from}.",
        ]
    for k in TOP_ORDER + [k for k in top if k not in TOP_ORDER and k != "papers"]:
        if k in top and top[k] is not None:
            lines.append(emit_field(k, top[k], 0))
    lines.append("papers:")
    for p in papers:
        keys = PAPER_ORDER + [k for k in p if k not in PAPER_ORDER]
        if generated_from and "abstract" not in p and "abstract_source" not in p:
            p = {**p, "abstract_source": "none"}
            keys = PAPER_ORDER + [k for k in p if k not in PAPER_ORDER]
        first = True
        for k in keys:
            if k not in p or p[k] in (None, "", []):
                continue
            lines.append(emit_field(k, p[k], 4, dash=first and k == "title"))
            if first and k == "title":
                first = False
    return "\n".join(lines) + "\n"


def split_names(s):
    return [n for n in re.split(r",\s*|\s+and\s+", s.strip()) if n]


def do_generate(year, doi, out, force=False):
    if out.exists() and re.search(r"^\s*abstract:\s*\|", out.read_text(encoding="utf-8"), re.M) and not force:
        die(f"{rel(out)} already has abstracts — refusing to overwrite. "
            f"Use --enrich to add ORCIDs, or --force to regenerate the skeleton.")
    vol = crossref_work(doi)
    if vol is None:
        die(f"Crossref has no record for {doi}")
    if vol.get("type") != "proceedings":
        print(f"  warning: {doi} is type {vol.get('type')!r}, expected 'proceedings'.",
              file=sys.stderr)
    raw = (vol.get("title") or [""])[0]
    print(f"volume: {volume_title(year, raw)!r}", file=sys.stderr)
    dois = enumerate_papers(doi, raw)
    print(f"enumerated {len(dois)} papers", file=sys.stderr)
    papers = []
    for pd in dois:
        time.sleep(0.3)
        w = crossref_work(pd)
        if w is None:
            print(f"  warning: {pd} vanished on re-fetch — skipping", file=sys.stderr)
            continue
        papers.append({
            "title": (w.get("title") or ["(untitled)"])[0].strip(),
            "authors": crossref_authors(w),
            "url": f"https://dl.acm.org/doi/{pd}",
        })
    if not papers:
        die("no papers resolved — refusing to write an empty proceedings file")
    n_orcid = sum(1 for p in papers for a in p["authors"] if a.get("orcid"))
    n_auth = sum(len(p["authors"]) for p in papers)
    top = {"title": volume_title(year, raw),
           "citation_url": f"https://dl.acm.org/doi/proceedings/{doi}"}
    out.write_text(emit(year, top, papers, doi, generated_from=doi), encoding="utf-8")
    print(f"wrote {rel(out)} — {len(papers)} papers, "
          f"{n_orcid}/{n_auth} authors with ORCID, no abstracts (P2).")


def do_enrich(year, doi, out):
    try:
        import yaml
    except ImportError:
        die("--enrich needs PyYAML (pip install pyyaml) to read the existing file")
    if not out.exists():
        die(f"{rel(out)} does not exist — use generate mode, not --enrich")
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    papers = data.get("papers") or []
    # map DOI -> Crossref ORCIDs
    changed = kept = 0
    for p in papers:
        url = p.get("url", "")
        m = DOI_IN_URL.search(url)
        if not m:
            continue
        time.sleep(0.3)
        w = crossref_work(m.group(0))
        if w is None:
            print(f"  warning: no Crossref record for {m.group(0)} — leaving as-is",
                  file=sys.stderr)
            continue
        cross = crossref_authors(w)
        existing = p.get("authors")
        names = existing if isinstance(existing, list) else split_names(existing or "")
        names = [n["name"] if isinstance(n, dict) else n for n in names]
        if len(names) != len(cross):
            print(f"  warning: author count {len(names)}≠{len(cross)} (Crossref) for "
                  f"{m.group(0)} — keeping existing names, no ORCIDs", file=sys.stderr)
            kept += 1
            continue
        merged = []
        for nm, cr in zip(names, cross):
            rec = {"name": nm}                     # PRESERVE existing name text
            if cr.get("orcid"):
                rec["orcid"] = cr["orcid"]
            merged.append(rec)
        p["authors"] = merged
        if any(a.get("orcid") for a in merged):
            changed += 1
    if changed == 0:
        print(f"{rel(out)}: no ORCIDs available from Crossref — left unchanged "
              f"({kept} paper(s) had a count mismatch).")
        return
    top = {k: v for k, v in data.items() if k != "papers"}
    out.write_text(emit(year, top, papers, data.get("doi"), generated_from=None),
                   encoding="utf-8")
    n_orcid = sum(1 for p in papers for a in (p.get("authors") or [])
                  if isinstance(a, dict) and a.get("orcid"))
    print(f"enriched {rel(out)} — {changed} papers gained ORCIDs "
          f"({n_orcid} author links total); {kept} left as-is (count mismatch).")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("year")
    ap.add_argument("doi", help="ACM *proceedings* DOI, e.g. 10.1145/3469013")
    ap.add_argument("--enrich", action="store_true",
                    help="add ORCIDs to an existing file, preserving names/abstracts")
    ap.add_argument("--force", action="store_true",
                    help="in generate mode, overwrite even if the file has abstracts")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if not re.fullmatch(r"\d{4}", str(args.year)):
        die(f"year must be a 4-digit year, got {args.year!r}")
    doi = args.doi.strip().removeprefix("https://doi.org/").removeprefix("doi.org/")
    if not DOI_RE.match(doi):
        die(f"doi does not look like a DOI: {args.doi!r}")
    out = Path(args.out) if args.out else ROOT / "_data" / "proceedings" / f"{args.year}.yml"
    if args.enrich:
        do_enrich(args.year, doi, out)
    else:
        do_generate(args.year, doi, out, force=args.force)


if __name__ == "__main__":
    main()

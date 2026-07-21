# DLfM website — implementation plan

Porting the DLfM conference site (currently Oxford Mosaic/Drupal at
`dlfm.web.ox.ac.uk`) to a Jekyll / GitHub Pages site at `dlfm.rism.digital`.

Guiding principle: **everything that changes year-to-year is Markdown or YAML.**
A publicity chair can set up a new year, edit every page, and retire the old one
without touching HTML. Developers own the theme (`_layouts`/`_includes`) and
rarely touch it.

---

## 1. Content model

Each conference year is an **edition**: a folder of Markdown pages plus year-keyed
data files. No year is structurally special — the "current" year is just the one
`_config.yml` points at.

```
_config.yml                current_year: 2026        ← the single pointer rollover flips
_data/
  editions.yml             registry → "Previous events" menu (year, city, dates, pages present)
  committee/2026.yml       people grouped by role
  sponsors/2026.yml        [{name, logo, url}]
  programme/2026.yml       sessions → items (time, title, authors, type, pdf)
  proceedings/2026.yml     papers  → {title, authors, doi, pages, pdf}
conf/2026/
  index.md                 landing: front matter (dates, venue, deadlines, news) + prose
  call-for-papers.md
  programme.md             thin: renders _data/programme/2026.yml
  proceedings.md           thin: renders _data/proceedings/2026.yml
  registration.md          OPTIONAL (present only if the year had one)
  venue.md / local.md      OPTIONAL
conf/2025/ …               frozen; permanent URLs /2025/…
about.md
assets/
  logo/  sponsors/  <year>/posters/  <year>/papers/
_layouts/  _includes/      theme (dev-owned)
_templates/edition/        blank scaffolds copied by the rollover Action
tools/                     extract_main.py (done), verify_fidelity.py, migrate helpers
.github/workflows/         rollover.yml, fidelity.yml, pages build
```

**Optional pages** are driven by their presence + a flag in `editions.yml`, so the
nav only shows what exists (matches the varying page sets we found: 2025 has
registration + venue + accommodation; 2020/21 were virtual; 2014–17 are landing-only).

### Data schemas (draft)

```yaml
# _data/proceedings/2025.yml
publisher: "ACM Digital Library (ICPS)"
doi_proceedings: "10.1145/nnnnnnn"
papers:
  - title: "…"
    authors: ["Given Family", "…"]
    pages: "1–10"
    doi: "10.1145/…"
    pdf: /assets/2025/papers/slug.pdf   # optional; else link out to ACM
```

```yaml
# _data/programme/2025.yml
date: 2025-07-10
sessions:
  - title: "Session 1: …"
    chair: "…"
    items:
      - time: "09:30"
        type: paper|poster|keynote|break
        title: "…"
        authors: ["…"]
        pdf: /assets/2025/posters/slug.pdf   # posters link their PDF
```

```yaml
# _data/editions.yml  (rollover appends to this)
- year: 2026
  ordinal: 13th
  city: "Thessaloniki, Greece"
  dates: "2 July 2026"
  pages: [programme]           # proceedings added when published
- year: 2025
  ordinal: 12th
  city: "…"
  pages: [programme, proceedings, registration, venue]
```

Committee and sponsors are pure data → rendered by includes, so adding a person is
one YAML block and a sponsor is one line + a logo file.

---

## 2. URLs: current year at root **and** `/<year>/`

Requirement: `/programme/` **and** `/2026/programme/` both serve the current year;
past years live permanently at `/2025/…`. Rollover must not move or 404 any URL.

**Approach (recommended): canonical content at `/<year>/`, current year co-rendered at root from a single source.**
- Tabular pages (programme, proceedings, committee, sponsors) render from
  `_data/<type>/<year>.yml`, so a root page and a `/<year>/` page render identically
  from the same YAML — genuine single source.
- Prose pages (landing, CFP, local) keep their prose in a per-year include partial
  (`_includes/prose/2026-landing.md`); both the root page and the `/<year>/` page
  `{% include %}` it. Still Markdown, still one source of truth.
- Root pages read `site.current_year`, so **rollover is a pure pointer-flip**: bump
  `current_year` and the root URLs follow. No existing files are edited or moved.
- `<link rel="canonical">` on root pages points at `/<year>/…` to avoid duplicate-content.

**Lighter alternative** if you'd rather not co-render: root URLs are redirects to
`/<year>/…` driven by `current_year` (meta-refresh + canonical). Simpler theme, but
`/programme/` bounces rather than serves. *Decision needed — see §8.*

---

## 3. Content migration (with the fidelity gate)

Pipeline, LLM kept off the content-critical path:

1. **Capture** — done. `_import/raw/<year>/<page>.html` (verbatim, frozen).
2. **Extract** — `tools/extract_main.py` → main-content fragment (deterministic).
3. **Baseline** — pandoc → `_import/text` (visible words) + `_import/md` (GFM w/ URLs). Done.
4. **Structure** — place prose into pages/includes; reshape tables into YAML. The only
   step with edit risk.
5. **Verify** — `tools/verify_fidelity.py` (see §4) proves no words/names/titles/DOIs
   were dropped, added, or altered vs. the frozen baseline.

Per page type:
- **landing** → prose to include; dates/venue/deadlines/news to front matter.
- **cfp** → prose to Markdown.
- **programme** → `_data/programme/<year>.yml`; poster PDFs downloaded + relinked.
- **proceedings** → `_data/proceedings/<year>.yml`; paper PDFs downloaded where hosted here.
- **registration/venue/local** → prose Markdown (optional pages).

**Assets:** ~100 referenced content PDFs/images (some via Mosaic-mangled URLs like
`yang2022introducingpdf` → `yang2022introducing.pdf`). A helper resolves + downloads
them into `assets/<year>/…` and rewrites links. `/sites/all/` theme assets are ignored.

---

## 4. Fidelity CI gate — `verify_fidelity.py`

For each migrated (past) edition page:
- Normalize both frozen `_import/text/<year>/<page>.txt` and the built page to token
  streams (lowercase, punctuation→space, collapse whitespace).
- **Fail** if any ground-truth token/name/title/DOI is missing from the build
  (dropped or altered content), or if the build adds tokens not present in ground
  truth or a small allowlist of intentional template text (added content).
- For proceedings/programme, additionally assert every author/title/DOI string from
  the baseline appears verbatim in the YAML.
- Emits a per-page side-by-side diff artifact for human review in a diff editor.

Wired into `.github/workflows/fidelity.yml` → PRs that alter a frozen archived page's
content fail CI. The current (editable) year has no baseline and is exempt.

---

## 5. Rollover — `.github/workflows/rollover.yml`

`workflow_dispatch` with input `next_year` (+ optional city/dates):
1. Copy `_templates/edition/*` → `conf/<next>/`, `_data/*/<next>.yml`, `_includes/prose/<next>-*.md`.
2. Set `current_year: <next>` in `_config.yml`.
3. Append the outgoing year to `_data/editions.yml` (moves it into "Previous events").
4. Branch, commit, open a **PR** for the chair to review and merge.

No file moves, no URL breakage. A README documents the same steps for manual use.

---

## 6. Theme & aesthetics

Formal, academic, clean, a touch more modern than the current site. Custom layouts in
the repo (no theme gem) for full control and zero external dependencies.
- **Logo**: black bass-clef DLfM mark, top-left, links home.
- **Type**: serif display for headings (academic register) + clean sans body;
  self-hosted (no CDN) for privacy/robustness.
- **Palette**: near-black ink + paper white + one restrained accent (drawn from the
  logo's monochrome character).
- **Layout**: slim fixed header + nav (with "Previous events" dropdown + edition
  switcher), readable content column (~72ch), quiet footer.
- **Standards**: responsive, WCAG AA, no JS framework (tiny vanilla JS for the menu),
  fast static output.

---

## 7. Milestones

1. **Scaffold + theme skeleton + schemas**; 2026 rendering at `/` and `/2026/`.
2. **Fidelity gate** built; migrate **2025** end-to-end to prove the gate green.
3. **Batch-migrate 2018–2024** (data-driven pages); download + relink assets.
4. **Migrate 2014–2017** (landing-only workshops).
5. **Rollover Action** + chair-facing README.
6. **Deploy**: `CNAME dlfm.rism.digital`, GitHub Pages, redirects/SEO.

---

## 8. Decisions (closed)

1. **Root URL behaviour** — **co-render** the current year at both `/` and `/<year>/`
   from a single source (the `/<year>/` page is canonical; root stubs locate the
   current edition and render its content + front-matter meta).
2. **Fonts** — **Spectral** (serif, headings/display) + **Inter** (sans, body/UI),
   both SIL OFL, self-hosted under `assets/fonts/` (no CDN at runtime).
3. **Deploy/DNS** — `rism.digital` administered by the RISM Digital Center; the user
   has the contact and will arrange the CNAME for `dlfm.rism.digital` + Pages once all
   parties give the go-ahead. Build deploy-ready; enable later.
4. **External links** — keep submission/registration/proceedings pointers going out to
   CMT / IAML / ACM DL as-is.

## 9. Layout note (co-render mechanics)

Each year lives in a top-level `<year>/` folder so URLs are natural (`/2026/programme/`)
with no permalink config. The `<year>/` page is the single source (front-matter meta +
Markdown body; big tables in `_data/<type>/<year>.yml`). Root stubs (`index.md`,
`programme.md`, …) carry no year; the shared layout resolves
`year = page.year | default: site.current_year`, finds the matching edition page, and
renders its content — so `/` and `/<year>/` render identically from one source.

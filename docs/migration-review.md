# DLfM migration review

A per-year list of issues found after the 2018–2025 batch migration, for review
and correction. Content words are all gate-verified present (`tools/verify_fidelity.py`),
so these are **structural / link / rendering** issues, not missing text.

Legend: `[ ]` todo · `[x]` done · add **Chair notes** inline under any item.

---

## Decisions (agreed)

- **Source still available:** the Oxford Mosaic site (`dlfm.web.ox.ac.uk`) stays up
  until migration is complete — cross-check and re-download assets from it freely.
- **Data-drive everywhere:** convert every edition's **programme** to the 2025
  data-driven representation (styled sessions, jump bar, poster links). Proceed as
  long as the fidelity gate stays green for each year (it will catch any dropped
  rows/authors/titles).

---

## 🔴 Content-affecting

### 1. Dead poster/paper PDF links (Mosaic-mangled `/files/*`)
Older programmes link to old-CMS URLs that 404 (e.g. `…/files/10zhangposterjpg` →
`…/10zhangposter.jpg`). Not rehosted because the mangled names lack extensions.
- Distinct dead links: **2021 (12), 2018 (6), 2019 (5), 2022 (5)**, 2020 (1), 2023 (1), 2025 (2), 2024 (0).
- **2019, 2021, 2022 have no local asset dir at all** — all their poster/paper PDFs are dead.
- Fix: download from the live Mosaic site, de-mangle names, rehost under `assets/<year>/`, repoint.
- [ ] 2018  [ ] 2019  [ ] 2020  [ ] 2021  [ ] 2022  [ ] 2023  [ ] 2025
- **Chair notes:** Posters missing completely from 2026 programme (metadata; PDFs haven't been uploaded on Mosaic yet and should be added in a later step once available there). 

### 2. 2018 sponsors missing entirely
The "DLfM 2018 is kindly supported by:" logos were dropped (not in hero, not in
prose); no `_data/sponsors/2018.yml`. Recover logos from Mosaic + add.
- [ ] fixed
- **Chair notes:**

### 3. 2019 committee — bogus "Programme Chair" entry
`_data/committee/2019.yml` has a duplicate Programme Chair with name
`"<u>Contact e-mail</u>: <drizo@dlsi.ua.es>"` (contact line mis-captured). Real
chair (David Rizo) is correct — delete the bogus entry; relocate the email if wanted.
- [ ] fixed
- **Chair notes:**

### 4. 2018 committee — bogus member
`_data/committee/2018.yml` ends with member `"DLfM 2018 is kindly supported by:"`
(a heading captured as a person). Delete.
- [ ] fixed
- **Chair notes:**

### 5. 2025 proceedings — wrong "Full citation" link
`citation_url` points to the ACM **logo image** (`…/footer-logo1.png`) instead of
the proceedings DOI (`https://doi.org/10.1145/3748336`). Only 2025 affected
(2018–2024 correct). Fix the value + the parser (grabs `<img>` before the link).
- [ ] fixed
- **Chair notes:**

---

## 🟡 Consistency / cosmetic

### 6. Programme rendering inconsistency → data-drive all (per decision)
2025 is data-driven; 2018–2024 are prose renderings of the original tables
(rougher). Convert 2018–2024 programmes to `_data/programme/<year>.yml`, gate-green.
- [ ] 2018  [ ] 2019  [ ] 2020  [ ] 2021  [ ] 2022  [ ] 2023  [ ] 2024
- **Chair notes:**

### 7. Landing "association" lead duplicates the hero
On 2018–2024, the prose opens with the full association line, duplicating the
hero's concise satellite line. Decide: drop the lead, or keep for detail.
- [ ] decided / fixed
- **Chair notes:**

### 8. `<colgroup>` cruft in prose programmes
Left in **2021, 2023, 2024** (invisible, but untidy). Moot once data-driven (#6).
- [ ] n/a after #6
- **Chair notes:**

### 9. 2019 sponsor logos low-res
~200px source images → may look soft at display size. Re-fetch larger from Mosaic
if available.
- [ ] fixed
- **Chair notes:**

---

## Scope notes (not fully verified by this scan)

- **Per-page visual rendering** — flagged from data/structure, not pixels; a manual
  pass will catch layout nuances (mobile table wrapping, logo balance, etc.).
- **External links** (DOIs/ACM) gate-verified as preserved; old-CMS self-links
  repointed except the dead PDFs in #1.
- **Committee role labels / affiliations** parsed cleanly for 2020–2025; only 2018/2019
  had the anomalies above.

---

## Chair's additional findings
* General request: the Mosaic proceedings pages all open with an ACM DL logo and link to "Full Citation in the ACM Digital Library". Please replicate accordingly for all proceedings pages here.
* 2024 main page has a bullet point:
`Registration page: </2024/registration/>`. Please update with full link, i.e. https://dlfm.rism.digital/2024/registration/'
* Same for 2023 under programme: `The DLfM 2023 schedule can now be found here: </2023/programme/>`. Please be on the lookout for this pattern (a literal relative URI in-text) and fix more generally.
* 2023: sshrc.png is so small as to be unreadable. Please provide very-wide-very-short logos like this with two slots' worth of space to make themn legible
* 2022: white background behind gt-music.png should be stripped, but then the gold GT logo might become hard to see against background. Let's try and see? There are also two talks in the first session missing links on the programme page (they are also not present in the proceedings page) -- can you cross-check these against Mosaic?
* 2021: again, white backgrounds in two logos that however both also feature golden elements -- I guess this is why you chose not to extract the backgrounds here, but it looks off. Maybe we can brainstorm a solution? Again also an instance of a verbatim relative URI: `The DLfM preliminary schedule can now be found here: </2021/programme/>`. Programme page: internal links at the top are not working; please fix and give the jump bar return treatment (up-arrow links at each of the anchors). Proceedings page: weird verbatim markdown text at the top, `# **DLfM '21: 8th International Conference on Digital Libraries for Musicology**`
* 2020: same issue with very-wide-very-short sshrc/canada logo. News section on landing page retains a link to mosaic: `https://dlfm.web.ox.ac.uk/dlfm-2020-programme`. Internal "important dates" link broken. Same for other internal links, e.g. "Trompa challenge", "proceedings track", "IMPORTANT DATES" again further down. Programme page: ACM logo with white background. 
* 2019: First two jumpbar items shouldn't be (conference location and association with ISMIR). Landing page has mosaic links for the prior years. 
* 2018: Same spurious first two jump bar items. Mosaic links for proceedings and programme (twice) in landing page text. Same prior-year mosaic links there too. Non-functioning internal "Important dates" "Submissions", "Proceedings-track" links. No sponsor images, but then a free-floating "DLfM 2018 is kindly supported by" at the bottom; please cross-check with mosaic version and fix. Proceedings page: weird verbatim markdown `## SESSION: Technological advances`, no other session information; can you check what happened?
* 2014-2017 still missing (next on roadmap?)

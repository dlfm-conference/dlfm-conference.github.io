# The DLfM conference website

This repository houses the website for the International Conference on Digital
Libraries for Musicology (DLfM). The site is published automatically by GitHub: whatever you save here
appears at the live address a minute or two later. You do **not** need to install
anything, and you do **not** need to know how to program. Everything below is done
through the GitHub website in your browser.

The rest of this page is a **guide for the conference chairs** who look after the
site from year to year — the General, Programme, Proceedings, and Local chairs. It
assumes no technical background. If you have never used GitHub before, start at
[How this works](#2-how-this-works-a-five-minute-mental-model) and read in order.

---

## Contents

1. [Before you start](#1-before-you-start)
2. [How this works (a five-minute mental model)](#2-how-this-works-a-five-minute-mental-model)
3. [The yearly cycle at a glance](#3-the-yearly-cycle-at-a-glance)
4. [Running an automation ("Action")](#4-running-an-automation-action)
5. [Editing a page or a data file](#5-editing-a-page-or-a-data-file)
6. [Proceedings and abstracts](#6-proceedings-and-abstracts)
7. [The automatic "Content fidelity" check](#7-the-automatic-content-fidelity-check)
8. [If something goes wrong, and who to ask](#8-if-something-goes-wrong-and-who-to-ask)
9. [Quick reference — "I want to…"](#9-quick-reference--i-want-to)
10. [For maintainers & developers](#10-for-maintainers--developers)

---

## 1. Before you start

You need two things:

1. **A web browser.** That's the only software involved.
2. **A GitHub account that has been added to the `dlfm-conference` organisation.**
   If you can open this repository and see an **"Actions"** tab and a **pencil
   (edit) icon** on files, you have the access you need. If not, ask the Steering
   Committee to add you.


---

## 2. How this works (a five-minute mental model)

The website is just a collection of **text files**. Two kinds matter to you:

- **Pages** — written in *Markdown* (a simple text format for headings, links, and
  paragraphs). File names end in `.md`.
- **Data files** — written in *YAML* (a simple list/label format). File names end in
  `.yml`. Sponsors, committees, programmes, and edition dates live in data files.

You only ever do **two kinds of task**:

- **Run an automation** (GitHub calls these **"Actions"** or **"workflows"**). These
  do fiddly, repetitive jobs for you — like setting up next year's edition, or
  building the proceedings list from the official ACM record. See [Section 4](#4-running-an-automation-action).
- **Edit a file** — change some text, add a sponsor, paste in the programme. See
  [Section 5](#5-editing-a-page-or-a-data-file).

### A few words you'll see

| Word | What it means for you |
|---|---|
| **Repository** ("repo") | This whole project — all the files that make up the website. |
| **Commit** | One saved change (GitHub records who changed what, and when). |
| **Branch** | A draft copy of the files where a change is prepared, so the live site is untouched until you're ready. |
| **Pull Request** ("PR") | A proposed change, shown as a tidy before/after, waiting for you to **review** and **Merge**. Think "change waiting for the green light." |
| **Merge** | Clicking the button that says "yes, apply this change." **This is the moment it goes live.** |
| **Action / workflow** | An automation you can run from the **Actions** tab. |

### How a change reaches the site

There are two paths, depending on what you're doing:

**A. Editing a file for your current edition — the everyday case.** You edit in the
browser and **save ("commit") straight to the live site**; your change appears a
minute or two later. There is no separate review step, so re-read your edit before
saving. Made a mistake? Edit the file again — that's the fix.

**B. Running an Action (or any change you want reviewed first).** The change is
prepared as a **Pull Request** — a proposed change on its own branch, with the live
site untouched — and you:

1. **review** it — GitHub shows exactly what would change ("Files changed");
2. see the automatic **check** run (the "Content fidelity" check — see [Section 7](#7-the-automatic-content-fidelity-check));
3. click **"Merge pull request"** → it goes live within a minute or two;
4. click **"Delete branch"** to tidy up (optional; safe).

If a proposed change is wrong, don't merge it — click **"Close pull request"** and
nothing happens to the live site.

You almost never need to touch a **past** edition. If you spot a problem
in one, flag it to the Steering Committee rather than editing it ([Section 8](#8-if-something-goes-wrong-and-who-to-ask)).

---

## 3. The yearly cycle at a glance

Each edition of DLfM moves through the same stages. Most of the year you're just
*editing files*; three moments use an *Action*.

| When | What you do | How | Section |
|---|---|---|---|
| Next edition is decided | **Roll over** to the new year | Action: *Roll over to next year* | [4a](#4a-roll-over-to-next-year) |
| Right after rollover | Fill in dates, city, landing text, the Call for Papers | Edit files | [5](#5-editing-a-page-or-a-data-file) |
| As they're confirmed | Add sponsors, the programme committee | Edit files | [5d](#5d-add-a-sponsor-logo), [5e](#5e-add-or-update-the-programme-committee) |
| When ACM affiliation is confirmed | **Confirm ACM ICPS** (turns on the "published in the ACM ICPS" line) | Action: *Confirm ACM ICPS affiliation* | [4b](#4b-confirm-acm-icps-affiliation) |
| When the schedule is set | Add the programme | Edit `_data/programme/<year>.yml` | [5f](#5f-add-the-programme) |
| After the conference, once proceedings are on the ACM DL | **Publish proceedings** (builds the paper list from ACM) | Action: *Publish proceedings* | [4c](#4c-publish-proceedings) |
| A day or two later | Get the verbatim abstracts added | Ask the Steering Committee | [6](#6-proceedings-and-abstracts) |

Replace `<year>` throughout with the actual four-digit year (e.g. `2027`).

---

## 4. Running an automation ("Action")

### The general recipe (works for all three)

1. Click the **"Actions"** tab at the top of the repository.
2. In the left-hand list, click the Action you want (their names are below).
3. On the right, click the **"Run workflow"** button. A little form drops down.
4. Fill in the boxes (each Action's boxes are described below), then click the green
   **"Run workflow"** button in the form.
5. Wait ~30–60 seconds, then refresh. You'll see the run appear with a spinning
   amber dot, then a green tick ✓ when it's done.
6. The Action has now opened a **Pull Request**. Go to the **"Pull requests"** tab —
   your new proposed change is at the top.
7. Open it, click **"Files changed"**, and check it looks right (each Action tells
   you what to expect).
8. If it's good, click **"Merge pull request"** → **"Confirm merge"**. Then
   **"Delete branch"** to tidy up.
9. If it's *not* right, click **"Close pull request"** — nothing goes live.

> **"This workflow requires approval to run."** On some runs GitHub shows a yellow
> banner asking a maintainer to approve before the automatic check runs. This is a
> safety feature. Just click **"Approve and run"** (you have permission). It doesn't
> change anything — it only lets the check proceed.

_[screenshot: the Actions tab with the "Run workflow" button]_

### 4a. Roll over to next year

Sets up a brand-new edition. Run this once, when the next conference's year is known.

- **Action name:** *Roll over to next year*
- **Boxes:**
  - **New conference year** — e.g. `2027` (required).
  - **Ordinal** — e.g. `14th` (optional; leave blank and it counts up automatically).
  - **City** / **Dates** — optional; you can fill these in later by editing files.
- **What the Pull Request should contain:** a new `2027/` folder (landing, Call for
  Papers, programme, proceedings pages), empty data-file stubs for the year, a new
  entry in `_data/editions.yml`, and a change making 2027 the "current" year. The
  previous year automatically moves into the **"Previous events"** menu.
- **After merging:** the new edition is live but mostly empty — that's expected. Fill
  it in using [Section 5](#5-editing-a-page-or-a-data-file). The "Proceedings" and
  "ACM ICPS" bits stay switched off until later (that's what 4b and 4c are for).

### 4b. Confirm ACM ICPS affiliation

Turns on the line that reads *"Proceedings published in the ACM International
Conference Proceedings Series (ICPS)."* Run this once ACM affiliation for the edition
is confirmed.

- **Action name:** *Confirm ACM ICPS affiliation*
- **Boxes:** **Edition year** — leave blank to use the current year, or type a year.
- **What it does:** switches the ICPS line on. Until that year has its own published
  proceedings page (step 4c), the line links to the general ACM DLfM page. After 4c,
  it automatically points at the year's own proceedings.
- If you run it and the Pull Request is **empty**, that just means it was already on —
  no harm done.

### 4c. Publish proceedings

Builds the year's proceedings page — every paper's title, authors (with ORCID iDs),
and a link to its official ACM record. Run this **after the proceedings are live on
the ACM Digital Library**.

- **Action name:** *Publish proceedings*
- **Boxes:**
  - **ACM proceedings DOI** — the identifier for the whole proceedings volume, e.g.
    `10.1145/3660570` (required). You'll find it on the ACM DL page for the DLfM
    proceedings — it's the DOI of the *proceedings volume*, not an individual paper.
  - **Edition year** — leave blank for the current year, or type a year.
- **What the Pull Request should contain:** a new `_data/proceedings/<year>.yml` with
  the full paper list, and the "Proceedings" link switched on in the menu.
- **Please skim the paper list** in "Files changed" against the ACM table of contents
  before merging, to make sure nothing is missing.
- **No abstracts appear yet.** That is deliberate and correct — see [Section 6](#6-proceedings-and-abstracts).

---

## 5. Editing a page or a data file

### The general recipe (the web editor)

1. Find the file (paths are given below). You can click through the folders, or press
   **`t`** on the code page to search file names.
2. Click the file to open it, then click the **pencil ✏️ icon** ("Edit this file")
   near the top right.
3. Make your change in the text box.
4. Scroll down to the **"Commit changes…"** box. For your **current edition**, leave it
   on **"Commit directly to the `main` branch"** and click **"Commit changes"** — your
   edit is live a minute or two later.
5. *(Optional — for a change you'd like reviewed first)* instead pick **"Create a new
   branch… and start a pull request"** → **"Propose changes"** → **"Create pull
   request"**, then review and **Merge** as in [Section 4](#4-running-an-automation-action) (steps 7–9). This is
   the safer route whenever you're unsure, because it allows you to check over your changes *before* they go live.

> **Two formatting rules that matter.** In `.yml` (data) files, **indent with spaces,
> never tabs**, and keep the existing indentation exactly. In both `.md` and `.yml`,
> if you ever need to write something that looks like an HTML/XML tag (for example the
> MEI element `<annot>`), wrap it in backticks — `` `<annot>` `` — or it will silently
> vanish.

> **Leave the machinery alone.** You never need to edit anything in the `_layouts/`,
> `_includes/`, `tools/`, `.github/`, or `_import/` folders. Those run the site. If a
> task seems to require it, that's a job for the site maintainer (see [Section 8](#8-if-something-goes-wrong-and-who-to-ask)).

> **Stick to your own year.** You look after the **current** edition. You should not
> edit earlier years — if something there needs fixing, flag it to the
> Steering Committee ([Section 8](#8-if-something-goes-wrong-and-who-to-ask)) rather than changing it yourself.

Throughout, replace `<year>` with the real year, e.g. `2027`.

### 5a. Edit the landing page text or news

- **File:** `<year>/index.md`
- The part below the `---` block at the top is [Markdown](https://github.blog/developer-skills/github/github-for-beginners-getting-started-with-markdown/): headings (`##`),
  `**bold**` for **bold** text, `[link-text](https://example.org)` to place links, and bullet lists using `-`. The "news" items near the top are just a
  bullet list — add a new line to announce something.

### 5b. Add or edit the Call for Papers

- **File:** `<year>/call-for-papers.md`
- Same idea — edit the Markdown body. When first rolled over it contains a placeholder
  line; replace it with the real call.

### 5c. Set the dates, city, ordinal, or "satellite of…" note

- **File:** `_data/editions.yml`
- Find your year's block and edit the values. It looks like this:

  ```yaml
  - year: 2027
    ordinal: "14th"
    city: "London, United Kingdom"
    dates: "Thursday 17 September 2027"
    satellite: "A satellite event of ISMIR 2027"   # optional; delete the line if not applicable
    pages: [call-for-papers, programme]
  ```

- Keep the quotation marks. Don't touch the `pages:` line here unless you're adding a
  page (see [5g](#5g-add-an-extra-page-venue-registration-accommodation)).

### 5d. Add a sponsor logo

Two steps: upload the image, then list it.

1. **Upload the logo.** Go to the `assets/sponsors/<year>/` folder (create it if the
   year isn't there yet: on the code page use **"Add file" → "Create new file"** and
   type `assets/sponsors/2027/placeholder.txt` to make the folder, then upload into
   it). Use **"Add file" → "Upload files"** to add a `.png` or `.svg` logo.
2. **List it.** Edit `_data/sponsors/<year>.yml` and add an entry:

   ```yaml
   - name: "University of Example"
     logo: /assets/sponsors/2027/example.png
     url: https://example.edu/
   ```

- For a **very wide, short** logo that would otherwise look tiny, add `wide: true` on
  its own line — it will be given two slots' width:

  ```yaml
  - name: "Some Research Council"
    logo: /assets/sponsors/2027/council.png
    url: https://council.example/
    wide: true
  ```

### 5e. Add or update the programme committee

- **File:** `_data/committee/<year>.yml`
- Two lists — `chairs` (with a `role`) and `members`:

  ```yaml
  chairs:
    - role: Programme Chair
      name: "Ada Lovelace"
      affiliation: "University of Example"
    - role: General Chair
      name: "Alan Turing"
      affiliation: "Example Institute"

  members:
    - name: "Grace Hopper"
      affiliation: "Example College"
    - name: "Edsger Dijkstra"
      affiliation: "Example University"
  ```

### 5f. Add the programme

- **File:** `_data/programme/<year>.yml`
- Until you fill this in, the Programme page politely says *"the programme will be
  published closer to the event"* — so it's fine to leave empty for a while.
- The structure is a list of **sessions**; each session has a `title`, an optional
  `chair` and `time`, and a list of **items** (the talks). A **break** is a short
  entry on its own. Optional **posters** go in their own block at the end.

  ```yaml
  note: "Preliminary programme:"            # optional intro line
  sessions:
    - title: |-
        Session 1: Automatic classification
      chair: |-
        David Lewis
      time: "9:00"
      items:
        - time: "9:00"
          type: |-
            Short paper
          title: |-
            Direct labelling of form of Classical-period piano sonata movements
          url: "https://doi.org/10.1145/3660570.3660577"     # optional link
          authors: |-
            Paul Burger and J. P. Jacobs
        - time: "9:30"
          type: |-
            Full paper
          title: |-
            Acoustic classification of guitar tunings with deep learning
          authors: |-
            Edward Hulme, David Marshall, Kirill Sidorov and Andrew Jones
    - break: |-
        Break & Posters
      time: "10:30"
  posters:
    note: "Poster session:"                 # optional
    challenge_label: "Sustainability challenge"   # optional; see below
    items:
      - title: "An online catalogue of French viola da gamba music"
        authors: "A. N. Other"
        pdf: /assets/2027/files/other-poster.pdf   # optional; upload the PDF first
      - challenge: true                            # a challenge-track poster
        title: "Keeping the lights on: sustaining a music encoding tool"
        authors: "D. L. Effem"
  ```

- The `|-` after a label lets the text sit indented on the next line; keep that style
  for titles and names. Poster/paper PDFs are uploaded to `assets/<year>/files/`
  first (same "Upload files" method as logos).

- **Marking "challenge" posters.** Some years run a themed *challenge track*
  alongside the regular call (past examples: the *Unlocking Musicology*,
  *TROMPA*, and *Software-sustainability* challenges). When only **some** posters
  in a session belong to that track, add `challenge: true` to each of those
  poster entries — they'll get a small coloured chip so readers can tell them
  apart. Set `challenge_label:` once, on the `posters:` block, to name the track
  (e.g. `"Software-sustainability challenge"`); if you leave it out, the chip
  just reads "Challenge". You only need this when a session is **mixed** — if
  *every* poster that year is a challenge poster, don't tag them individually;
  just say so in the `note:` (e.g. `"Poster presentations — TROMPA Challenge"`).

### 5g. Add an extra page (Venue, Registration, Accommodation…)

Some years need extra pages. There are **two categories**, because the top menu only
knows about a fixed set of pages.

**Category A — pages the menu already supports: `Venue` and `Registration`.**
These appear in the top navigation automatically once activated. Two steps:

1. **Create the page.** Make a new file `<year>/venue.md` (or `registration.md`) with
   this heading block, then write the content in Markdown below it:

   ```markdown
   ---
   layout: edition-page
   role: venue
   year: 2027
   title: Venue
   ---

   ## Where to find us

   …your content here…
   ```

2. **Activate it.** Edit `_data/editions.yml` and add  to that year's `pages:`
   list — e.g. change `pages: [call-for-papers, programme]` to
   `pages: [call-for-papers, programme, venue]`. The **Venue** link now shows in the menu.

**Category B — any other page (e.g. Accommodation & Transport).**
The page works fine, but it will **not** get a top-menu link (the menu is fixed). Do
steps 1–2 above using your own label (e.g. `local` with `title: Accommodation and
Transportation`), then **link to it from your landing page** (`<year>/index.md`) so
visitors can find it, for example:

```markdown
[Accommodation and Transportation](/2027/local/)
```

> Adding a brand-new item to the **top menu** itself is a template change — ask the
> site maintainer ([Section 8](#8-if-something-goes-wrong-and-who-to-ask)).

- **Images and downloads** on any page go under `assets/<year>/files/`, and are
  linked with a leading slash, e.g. `/assets/2027/files/map.png`.

---

## 6. Proceedings and abstracts

**Why the proceedings page shows no abstracts at first — and why that's correct.**

When you run *Publish proceedings* ([4c](#4c-publish-proceedings)), the page is built
from **Crossref**, the open, authoritative source of paper metadata: every title,
every author (with their ORCID iD), and a link to each paper's official ACM record.
Abstracts are **deliberately left out at this stage**. The only place the *verbatim*
abstract text lives is the ACM Digital Library, which is protected against automated
reading, and the automatable alternative shortens about a quarter of abstracts — so
publishing from it would risk showing abbreviated text as if it were the real thing.

The result is a page that is already **complete and citable**: every paper is listed
and links to its ACM record, where the abstract can be read. Not showing abstracts
inline is a faithful, deliberate choice, not an error.

**How the abstracts get added (the second step).** By the time proceedings publish,
they are also live on the ACM DL, so the verbatim abstracts become available there.
Adding them is a small **technical** task. **It is not a chair task:** ask the **site maintainer** to arrange the
abstract harvest. 

**The "ACM ICPS" line through the year.** When a new year is started through the rollover action, the ACM ICPS line is not shown at first. *Confirm ACM
ICPS* ([4b](#4b-confirm-acm-icps-affiliation)) switches it on (linking to the general
ACM DLfM page). *Publish proceedings* ([4c](#4c-publish-proceedings)) then repoints it
at the year's own proceedings page and adds the "Proceedings" menu link. You don't
manage this line by hand — the two Actions handle it.

---

## 7. The automatic "Content fidelity" check

A check called **"Content fidelity"** guards the **historical record** from when the site was hosted on Oxford's Mosaic platform: the pages for
the migrated editions **2014–2026** are compared, word for word, against a frozen copy
of the original conference site, so an *accidental* change to a past page is caught.
(Editions from 2027 onward were written fresh here and have no "original" to compare
against, so the check doesn't apply to them — expected, not a gap.) It runs both on
proposed changes (Pull Requests) and on anything committed directly.

- **A green tick ✓** — the migrated pages still match the record. Nothing to do.
- **A red ✗** — some wording on a 2014–2026 page changed. Since you should be working
  only on the **current** edition, a red ✗ almost always means an edit *accidentally*
  touched an old page. Look at "Files changed": if it was a proposed change, don't
  merge it; if you committed it directly, undo it ([Section 8](#8-if-something-goes-wrong-and-who-to-ask)) — then flag the
  old-year issue to the Steering Committee.

The check is **advisory** — it warns, it doesn't block — so it never gets in the way
of legitimate work on the current edition (which it doesn't check anyway). Deliberate
corrections to a past edition are a Steering-Committee / maintainer matter, not a
chair task.

---

## 8. If something goes wrong, and who to ask

- **A Pull Request looks wrong** → don't merge it. Click **"Close pull request"**.
  Nothing goes live. You can always start again.
- **You made a bad direct edit (the everyday case)** → the simplest fix is to **edit
  the file again** and correct it (or paste the previous text back). To undo a whole
  change cleanly, open the file, click **"History"**, click the commit you want to
  reverse, and use the **"Revert"** option — then commit that. (Or ask the maintainer.)
- **You merged an Action or Pull Request by mistake** → open the merged Pull Request,
  click **"Revert"**, and merge the revert. That puts the site back.
- **A page looks broken after an edit** → it's almost always a YAML indentation slip
  (a tab instead of spaces, or a mis-aligned line) or a missing quotation mark. Re-open
  the file, compare against the templates above, and fix the indentation.
- **A word disappeared** → if it looked like `<a tag>`, wrap it in backticks
  (`` `<a tag>` ``) and it'll come back.

**Who to ask.** For anything that needs the "machinery" — adding a brand-new menu
item, harvesting the verbatim abstracts from ACM, making the fidelity check go green
after an intentional edit to an old year, or anything under `_layouts/`, `_includes/`,
`tools/`, or `.github/` — contact the **Steering Committee**, who will put you in touch
with the **site maintainer**.

---

## 9. Quick reference — "I want to…"

| I want to… | Do this |
|---|---|
| Set up next year's edition | Action: **Roll over to next year** ([4a](#4a-roll-over-to-next-year)) |
| Change the dates / city / ordinal | Edit `_data/editions.yml` ([5c](#5c-set-the-dates-city-ordinal-or-satellite-of-note)) |
| Edit the landing text or add news | Edit `<year>/index.md` ([5a](#5a-edit-the-landing-page-text-or-news)) |
| Publish the Call for Papers | Edit `<year>/call-for-papers.md` ([5b](#5b-add-or-edit-the-call-for-papers)) |
| Add a sponsor | Upload logo to `assets/sponsors/<year>/`, list it in `_data/sponsors/<year>.yml` ([5d](#5d-add-a-sponsor-logo)) |
| Add the programme committee | Edit `_data/committee/<year>.yml` ([5e](#5e-add-or-update-the-programme-committee)) |
| Add the programme | Edit `_data/programme/<year>.yml` ([5f](#5f-add-the-programme)) |
| Add a Venue or Registration page | Create `<year>/venue.md`, add `venue` to `pages:` ([5g](#5g-add-an-extra-page-venue-registration-accommodation)) |
| Add an Accommodation (or other) page | Create the page + link it from the landing ([5g](#5g-add-an-extra-page-venue-registration-accommodation)) |
| Turn on the "ACM ICPS" line | Action: **Confirm ACM ICPS affiliation** ([4b](#4b-confirm-acm-icps-affiliation)) |
| Publish the proceedings list | Action: **Publish proceedings** (needs the ACM volume DOI) ([4c](#4c-publish-proceedings)) |
| Get abstracts onto the proceedings page | Ask the site maintainer ([6](#6-proceedings-and-abstracts)) |
| Undo a merged change | Open the PR → **Revert** ([8](#8-if-something-goes-wrong-and-who-to-ask)) |

---

## 10. For maintainers & developers

The site is a **Jekyll** site published by **GitHub Pages** (Deploy from a branch:
`main`, folder `/`). Dependencies are pinned to the `github-pages` gem, so a push to
`main` builds and deploys with no extra CI. To preview locally:
`bundle install` then `bundle exec jekyll serve` (Ruby 3.1; the `github-pages` gem
pins Jekyll 3.9).

- **Content lives in** `_data/` (YAML), the per-year `*.md` pages, and `assets/`.
  Rendering logic lives in `_layouts/` and `_includes/`; site-wide settings in
  `_config.yml`.
- **The lifecycle Actions** are in `.github/workflows/` (`rollover.yml`,
  `confirm-acm.yml`, `publish-proceedings.yml`), backed by scripts in `tools/`
  (`rollover.py`, `edition_flags.py`, `proceedings_from_doi.py`). They open Pull
  Requests via `peter-evans/create-pull-request`; this requires, at both the
  organisation and repository level, Settings → Actions → General → "Allow GitHub
  Actions to create and approve pull requests".
- **The fidelity check** (`.github/workflows/fidelity.yml`, `tools/verify_fidelity.py`)
  compares built page text against frozen captures in `_import/text/` for 2014–2026.
  It is intentionally **advisory** (branch `main` is unprotected) so intentional edits
  to historical pages are never blocked.
- **Verbatim ACM abstracts** are added with `tools/proceedings_from_doi.py … --enrich`, which needs an authenticated browser session and so cannot
  run in CI. 

---
layout: page
permalink: /about/
title: About
eyebrow: International Conference on Digital Libraries for Musicology
---

* TOC
{:toc}

## Background

Digital Libraries for Musicology – DLfM – exists most obviously at the intersection of digital library and musicology research, but also encompasses computer science, library and information science, digital humanities, Music Information Retrieval, alongside digital practice in music collections of cultural institutions. It was established as a workshop by Kevin Page and Ben Fields following their work on interdisciplinary approaches to digital musicology during the AHRC-funded Transforming Musicology project. The first event was co-located with the 2014 Digital Libraries conference in London (itself a joint Joint Conference on Digital Libraries (JCDL) and Theory and Practice of Digital Libraries  (TPDL) event!). After the success of the initial edition confirmed community interest and support for such an event, DLfM continued as a workshop associated with JCDL in 2015, before co-locating with the International Society for Music Information Retrieval (ISMIR) from 2016. As contributions matured and the programme became more oriented around presented papers, DLfM transitioned to become a single-day conference in 2018, when it also began publishing Open Access proceedings. In response to community feedback, and to remain true to its interdisciplinary roots, in 2021 the DLfM Steering Committee decided to alternate co-location between ISMIR and the conference of the International Association of Music Libraries, Archives and Documentation Centres (IAML).

## DLfM Aims and Objectives

DLfM presents a venue specifically for those working on, and with, Digital Library systems and content in the domain of music and musicology. This includes Music Digital Library systems, their application and use in musicology, technologies for enhanced access and organisation of musics in Digital Libraries, bibliographic and metadata for music, intersections with music Linked Data, and the challenges of working with the multiple representations of music across large-scale digital collections such as the Internet Archive and HathiTrust.

DLfM focuses on the implications of music for Digital Libraries and Digital Libraries research when pushing the boundaries of contemporary musicology, including the application of techniques as reported in more technologically-oriented fora such as ISMIR and ICMC.

The conference objectives are:

- to act as a forum for reporting, presenting, and evaluating this work and disseminating new approaches to advance the discipline;
- to create a venue for critically and constructively evaluating and verifying the operation of Music Digital Libraries and the applications and findings that flow from them;
- to consider the suitability of existing Music Digital Libraries, particularly in light of the transformative methods and applications emerging from musicology, large collections of both audio and music related data, ‘big data’ method, and MIR;
- to explore how digital libraries and digital musicology can combine to offer richer online access to online music collections;
- to set the agenda for work in the field to address these new challenges and opportunities.

DLfM has, since its inception, included high-quality proceedings as one of its core outputs. For all editions thus far this has been realised through the ACM ICPS series, with publication in the prestigious ACM Digital Library. Feedback from authors indicated this is a strong motivation for submission. In 2018 Open Access publication of the proceedings was secured with the ACM for the first time, included as part of the conference registration fees. Inclusion in the ACM DL brings a requirement for rigorous peer-review, and an expectation of high quality contributions of full (8 page) and short (4 page) paper submissions (formatted according to the ACM double-column template). Submissions should therefore report substantial pieces of research, and the peer review process should be run with the utmost respect and professionalism. A minimum of three reviews are expected per paper, and the reviews are expected to be careful, insightful, and supportive. Thus far DLfM has undertaken single-blind reviewing.

Since submission of full and short papers requires a significant investment of research and writing effort for authors, the DLfM programme has always included alternative and complementary sessions with a lower barrier to entry: it is a core principle of the conference to encourage new attendees from both musicology and technology backgrounds, provide a venue where new interdisciplinary approaches can be discovered, and new collaborations can be nurtured. As such, poster and “challenge” paper sessions are an equally important segment of the programme. The “challenge” paper session, often run as a panel following short presentations, has also proved a valuable opportunity for (project) sponsorship, whereby sponsors can work with the organisers to set a theme or topic for the session. Examples of these can be seen in the Call for Papers (CfP) and programmes from previous years. Posters and Challenge Papers are not included in the ACM proceedings, but instead published on the DLfM website. Sponsors have, in this way, consistently helped keep the registration price of DLfM low.

## DLfM Website

From 2014 to 2026, the DLfM website was hosted by the University of Oxford, at [https://dlfm.web.ox.ac.uk/](https://web.archive.org/web/20260820144840/https://dlfm.web.ox.ac.uk/) (archived). It is now [hosted on GitHub](https://github.com/dlfm-conference/dlfm-conference.github.io) with the support of the [RISM Digital Center](https://rism.digital/) at <https://dlfm.info/>, following a redesign contributed in-kind by the [Let's Encode!](https://letsenco.de) project. The site maintains an archive of past editions — their calls for papers, programmes, and proceedings — and is expected to continue hosting future editions of DLfM. Editing access is given to the Programme Chair and Proceedings Chair.

## Steering Committee

Membership of the DLfM Steering Committee is open to all previous General Chairs (who wish to remain Steering Committee members), with membership re-confirmed annually. The Steering Committee are consulted in selection of the Programme Chair, and remain on hand to offer advice and experience to the Programme Chair, General Chair, and Local Chair. Please contact the Chair of the Steering Committee in the first instance.

Current (2026) members of the DLfM Steering Committee are:

- Claire Arthur, Georgia Institute of Technology
- David Lewis, Goldsmiths University of London
- Kevin Page (Chair), University of Oxford
- Laurent Pugin, RISM Digital Center / University of Bern
- Martha E. Thomae, DDMAL, Schulich School of Music, McGill University, Montreal
- David M. Weigl, mdw – University of Music and Performing Arts Vienna

## Past Organising Committees

Each edition of DLfM is organised by a team drawn from the community and appointed afresh for that year. With thanks to everyone who has served, the chairs of every previous edition are listed below — follow a year for its full programme committee and for affiliations as they stood at the time.

<!-- Rendered from `_data/committee/<year>.yml` (2018 onwards, maintained by the
     rollover Action) and `_data/committee_early.yml` (2014–2017, see the note
     in that file). New editions therefore appear here with no edit to this page.
     Written as raw HTML because kramdown's `{:toc}` would otherwise pick up a
     heading per year; the jump bar lists H2s only.

     "Previous" means the same here as in the nav, the footer and /previous/:
     every edition except site.current_year, which is the forthcoming (or
     running) one and has its committee on its own landing page. Rollover
     flips current_year, so the outgoing edition joins this list by itself.
     The .size guard is belt-and-braces for the window in between: rollover
     writes `chairs: []`, and an empty array is TRUTHY in Liquid, so testing
     comm.chairs alone renders a year heading above an empty list. -->
<div class="past-committees">
{%- assign past = site.data.editions | where_exp: "e", "e.year != site.current_year" -%}
{%- for ed in past -%}
  {%- assign ystr = ed.year | append: "" -%}
  {%- assign comm = site.data.committee[ystr] -%}
  {%- unless comm -%}{%- assign comm = site.data.committee_early[ystr] -%}{%- endunless -%}
  {%- if comm.chairs.size > 0 -%}
  <section class="pc-edition">
    <h3 class="pc-head"><a href="/{{ ed.year }}/">{{ ed.year }}</a><span class="pc-place">{{ ed.city }}</span></h3>
    <ul class="pc-roles">
    {%- assign roles = comm.chairs | map: "role" | uniq -%}
    {%- for role in roles -%}
      {%- assign holders = comm.chairs | where: "role", role | map: "name" | join: ", " -%}
      <li><span class="pc-role">{{ role }}</span><span class="pc-names">{{ holders }}</span></li>
    {%- endfor -%}
    </ul>
  </section>
  {%- endif -%}
{%- endfor -%}
</div>

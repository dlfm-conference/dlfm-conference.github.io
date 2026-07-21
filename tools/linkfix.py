#!/usr/bin/env python3
"""Shared link normalisation for migrated pages.

Repoints old Oxford Mosaic (dlfm.web.ox.ac.uk) URLs to the new site paths, and
turns bare autolinked relative URIs (`</2024/registration/>`) into proper links.
Used by make_landing.py and make_prose_page.py so every page is consistent.
"""
import re

WAYBACK = re.compile(r"https?://web\.archive\.org/web/\d+/")
SITE = "https://dlfm.rism.digital"


def _subpage(slug):
    if slug == "cfp":
        return "call-for-papers"
    if slug.startswith("accommodation"):
        return "local"
    return slug


def repoint(text):
    """Rewrite legacy Mosaic URLs to new-site paths."""
    text = WAYBACK.sub("", text)
    B = r"https?://dlfm\.web\.ox\.ac\.uk"

    # /workshops/dlfm-YYYY[/programme|/proceedings]
    text = re.sub(B + r"/workshops/dlfm-(\d{4})/(programme|proceedings)", r"/\1/\2/", text)
    text = re.sub(B + r"/workshops/dlfm-(\d{4})\b/?", r"/\1/", text)

    # [dlfm-]YYYY-(programme|proceedings|cfp|registration|venue|accommodation…)
    text = re.sub(
        B + r"/(?:dlfm-)?(\d{4})-(programme|proceedings|cfp|registration|venue|accommodation-and-transportation)\b/?",
        lambda m: f"/{m.group(1)}/{_subpage(m.group(2))}/", text)

    # Nth-international-conference…  ->  /(2013+N)/
    text = re.sub(
        B + r"/(\d+)(?:st|nd|rd|th)-international-conference[a-z0-9-]*",
        lambda m: f"/{2013 + int(m.group(1))}/", text)

    # shared virtual-conference instructions page
    text = re.sub(B + r"/gathertown-user-instructions/?", "/2020/gathertown-user-instructions/", text)

    # mangled mailto (dlfmYYYY%40easychair.org)
    text = re.sub(B + r"/(dlfm\d+)%40(easychair\.org)", r"mailto:\1@\2", text)

    # any remaining bare old-site root -> new canonical site (do last)
    text = re.sub(B + r"/?(?=[)\s\"'>]|$)", SITE + "/", text)
    return text


def fix_autolinks(text):
    """`</2024/registration/>` (autolinked relative URI) -> proper full link."""
    return re.sub(r"<(/\d{4}/[a-z-]+/?)>",
                  lambda m: f"[{SITE}{m.group(1)}]({m.group(1)})", text)


def normalise(text):
    return fix_autolinks(repoint(text))

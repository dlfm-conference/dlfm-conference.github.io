#!/usr/bin/env python3
"""Deterministically extract the inner HTML of the Oxford Mosaic main-content
region (<div id="main-content" role="main">) from a captured page.

No LLM, no third-party deps — stdlib html.parser only, so the output is a pure
function of the input HTML. This is the trusted first step of the content
fidelity pipeline: raw HTML -> (this) main-content fragment -> pandoc -> text.

Usage: python3 tools/extract_main.py <input.html>   # writes fragment to stdout
"""
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
TARGET_ID = "main-content"


def _attrs(attrs):
    out = []
    for name, val in attrs:
        if val is None:
            out.append(f" {name}")
        else:
            out.append(f' {name}="{val.replace(chr(34), "&quot;")}"')
    return "".join(out)


class MainExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.capturing = False
        self.depth = 0          # div-nesting depth inside the target
        self.out = []

    def handle_starttag(self, tag, attrs):
        if not self.capturing:
            if tag == "div" and dict(attrs).get("id") == TARGET_ID:
                self.capturing = True
                self.depth = 1  # entered the wrapper; don't emit it
            return
        if tag == "div":
            self.depth += 1
        self.out.append(f"<{tag}{_attrs(attrs)}>")

    def handle_startendtag(self, tag, attrs):
        if self.capturing:
            self.out.append(f"<{tag}{_attrs(attrs)} />")

    def handle_endtag(self, tag):
        if not self.capturing:
            return
        if tag == "div":
            self.depth -= 1
            if self.depth == 0:
                self.capturing = False  # exited the wrapper; don't emit it
                return
        if tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self.capturing:
            self.out.append(data)

    def handle_comment(self, data):
        if self.capturing:
            self.out.append(f"<!--{data}-->")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: extract_main.py <input.html>")
    with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
        p = MainExtractor()
        p.feed(fh.read())
    sys.stdout.write("".join(p.out))


if __name__ == "__main__":
    main()

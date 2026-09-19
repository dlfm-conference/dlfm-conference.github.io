-- Drop table attributes before writing.
--
-- pandoc >= 3 renders a table's HTML attributes into its plain/markdown output
-- as a trailing `{height="1726" style="..." width="1507"}` block on the caption
-- line. Those are Mosaic's markup, not the page's words, and the fidelity gate
-- (tools/verify_fidelity.py) compares words — so left in, they read as content
-- the built site has "dropped". The pandoc that made the original 2014-2026
-- captures did not emit them; this keeps regenerated captures comparable.
function Table (t)
  t.attr = pandoc.Attr()
  return t
end

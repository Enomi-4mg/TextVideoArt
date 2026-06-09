# Unicode Display Width Research

TVA format version `0.1.0` validates frame width by Python character count.
It does not calculate terminal or browser display cell width.

This keeps the current format simple, but it means some Unicode text can pass
validation while rendering wider or narrower than expected.

## Width Models

Code point count is simple and matches the current implementation most closely.
It does not model combining marks, emoji sequences, or terminal cell behavior.

Grapheme cluster count better matches what a reader sees as one written symbol.
It still does not answer how many monospace cells a symbol occupies.

Display cell width is closest to terminal layout. It needs Unicode width tables,
terminal-specific behavior, and policy for ambiguous-width characters.

## Known Issues

Full-width Japanese characters commonly occupy two terminal cells while counting
as one Python character.

Combining marks can add visual marks to a previous character while counting as
separate code points.

Emoji may render as one glyph, multiple glyphs, one cell, two cells, or fallback
boxes depending on terminal, browser, operating system, and font.

Unicode block elements in the `blocks` charset are useful for denser images, but
they should not be treated as general full-width support.

## Future Options

A future format revision could add `width_mode` to manifest metadata.

Possible values:

```text
character_count
grapheme_cluster
display_cell
```

The CLI could also add diagnostics that warn when a charset contains characters
with likely non-1-cell display width.

Charset profiles may be a lighter-weight path: a preset can declare whether it
is intended for plain ASCII, block elements, or experimental wide characters.

No validation behavior changes are recommended for TVA `0.1.0`.

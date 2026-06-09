# Color Layer Design Research

Future color support should not embed ANSI escape sequences inside
`frames/*.txt`.

Frame text should remain plain text. Color should be represented as optional
sidecar data.

## Recommended Direction

Use optional per-frame JSON files under:

```text
colors/
```

Missing color files mean no color overrides for that frame.

Initial color records should use 2D runs:

```json
{
  "runs": [
    {"line": 0, "column": 0, "length": 12, "fg": "#ffffff", "bg": "#000000"}
  ]
}
```

2D runs are easier to inspect and align with text frame line and column
coordinates. 1D runs are compact but require flattening rules that are easier to
misread and harder to debug.

## Color Values

Prefer hex-only color values:

```text
#rgb
#rrggbb
#rrggbbaa
```

Named colors, ANSI color numbers, and CSS functions should stay out of the
initial format.

## Renderer Implications

The Web Player can map runs to styled spans or a future canvas renderer.

HTML export can emit static markup with inline styles or CSS classes.

Terminal playback can translate hex colors to ANSI truecolor only when explicitly
requested.

The VJ sample should eventually share the Web Player renderer path instead of
building a separate color interpretation.

No `colors/*.json` implementation, validation changes, or TVA version change is
recommended in this phase.

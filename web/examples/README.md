# tvart Browser Examples

These examples are static browser apps. Serve the repository root or the `web/`
directory with any local static server, then open the example paths below.

```bash
python3 -m http.server 8000
```

From the repository root, open `http://localhost:8000/web/`.

## Examples

- `web/player/`: static Web Player for loading a local `.tva` archive.
- `web/examples/api-demo/`: direct `TvaPlayer` API controls, events, markers,
  and manifest display.
- `web/examples/webcam-preview/`: experimental browser-side camera-to-text
  preview. It does not create `.tva` files.
- `web/examples/vj-sample/`: experimental full-window output surface for browser
  capture, OBS, and VJ workflows.

## Dependencies

The examples intentionally avoid a build step. TVA archive loading currently
imports JSZip from `https://cdn.jsdelivr.net/`, so the Web Player, API demo, and
VJ sample need network access unless JSZip is vendored in a future hardening
pass.

## Sample Assets

Large videos and generated `.tva` archives should not be committed directly to
the repository. Prefer GitHub Releases for large sample assets. If a tiny,
validated `.tva` sample is added later, keep the `.gitignore` exception narrow,
such as `!examples/**/*.tva`.

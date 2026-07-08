# tvart Browser Examples

These examples are static browser apps. Serve the repository root or the `web/`
directory with any local static server, then open the example paths below.

```bash
python3 -m http.server 8000
```

From the repository root, open `http://localhost:8000/web/`.

## Examples

- `web/player/`: unified Web Player for loading a local `.tva` archive,
  debugging `TvaPlayer` API behavior, and tuning VJ capture output through
  Player / Debug / VJ tabs.
- `web/examples/webcam-preview/`: experimental browser-side camera-to-text
  preview. It does not create `.tva` files.

## Dependencies

The examples intentionally avoid a build step. TVA archive loading uses the
vendored JSZip module in `web/vendor/`, so the Web Player does not need network
access at runtime.

## Sample Assets

Large videos and generated `.tva` archives should not be committed directly to
the repository. Prefer GitHub Releases for large sample assets. Tiny, validated
browser demos may live under `web/samples/`; keep `.gitignore` exceptions narrow
and avoid committing personal works or bulky exports.

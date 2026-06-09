# Charset Presets

`tvart` provides named charset presets for conversion, preview, and manifest
metadata fixes.

```text
standard = " .:-=+*#%@"
simple   = " .#"
blocks   = " ░▒▓█"
dense    = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
```

Use `--charset-preset` with `convert` or `preview`.

Use `--set-charset-preset` with `fix`.

`--charset` and `--charset-preset` are mutually exclusive. `--set-charset`
and `--set-charset-preset` are also mutually exclusive.

The `blocks` preset contains Unicode block elements. TVA format version `0.1.0`
still validates frame width by character count, not display cell width.

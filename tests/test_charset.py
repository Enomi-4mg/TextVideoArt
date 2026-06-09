from __future__ import annotations

import unittest

import path_setup  # noqa: F401
from tvart.charset import CHARSET_PRESETS, resolve_charset


class CharsetTests(unittest.TestCase):
    def test_resolve_charset_defaults_to_standard(self) -> None:
        self.assertEqual(resolve_charset(None, None), CHARSET_PRESETS["standard"])

    def test_resolve_charset_uses_explicit_charset(self) -> None:
        self.assertEqual(resolve_charset(" .#", None), " .#")

    def test_resolve_charset_uses_preset(self) -> None:
        self.assertEqual(resolve_charset(None, "simple"), " .#")

    def test_unknown_preset_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_charset(None, "missing")


if __name__ == "__main__":
    unittest.main()

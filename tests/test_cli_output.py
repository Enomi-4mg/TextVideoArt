from __future__ import annotations

import unittest
from contextlib import redirect_stderr
from io import StringIO

import path_setup  # noqa: F401
from tvart.convert import _clear_status, _status


class CliOutputTests(unittest.TestCase):
    def test_status_is_transient_on_stderr(self) -> None:
        stream = StringIO()
        with redirect_stderr(stream):
            _status("Working...", quiet=False)
            _clear_status(quiet=False)

        self.assertEqual(stream.getvalue(), "\r\033[KWorking...\r\033[K")

    def test_quiet_status_writes_nothing(self) -> None:
        stream = StringIO()
        with redirect_stderr(stream):
            _status("Working...", quiet=True)
            _clear_status(quiet=True)

        self.assertEqual(stream.getvalue(), "")


if __name__ == "__main__":
    unittest.main()

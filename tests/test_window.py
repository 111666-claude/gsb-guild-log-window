import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guildlog.window import Entry, Window  # noqa: E402


class WindowTest(unittest.TestCase):
    def test_recent_is_lazy(self):
        window = Window(1000, 10)
        window.add(Entry("e1", "p1", "kick", "p2", 0))
        stream = window.recent(0)
        self.assertEqual(len(list(stream)), 1)

    def test_entry_keeps_fields(self):
        entry = Entry("e1", "p1", "kick", "p2", 5)
        self.assertEqual((entry.actor, entry.action, entry.target), ("p1", "kick", "p2"))

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Window(1000, 10).scanned, 0)


if __name__ == "__main__":
    unittest.main()

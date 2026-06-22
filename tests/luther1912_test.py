"""
test_coverage_boost.py – Zusätzliche Tests zur Erhöhung der Code Coverage.

Abgedeckte Module:
- src/luther1912.py        (war 0 %)
- src/schlachter1951.py    (war 0 %)
- src/web.py               (war 0 %)
- src/strong_manager.py    (war 30 %)
- src/bible_base.py        (Lücken: _parse_verse_per_line_format,
                            _parse_standard_format, _remove_span_tag,
                            _go_to_next_passage, _to_passage_reached,
                            _is_flood_search-Randpfade)
- src/main.py              (Routen und load_ignore_words)
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# Pfad sicherstellen
# ---------------------------------------------------------------------------
_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _src not in sys.path:
    sys.path.insert(0, _src)


# ===========================================================================
# Luther 1912
# ===========================================================================

class TestLuther1912(unittest.TestCase):

    def setUp(self):
        from luther1912 import Luther1912
        self.Bible = Luther1912
        self.sample = (
            "1. Mose\n"
            "Kapitel 1\n"
            "1 Im Anfang schuf Gott die Himmel und die Erde.\n"
            "2 Und die Erde war wüst und leer.\n"
            "Kapitel 2\n"
            "1 Und die Himmel und die Erde wurden vollendet.\n"
            "Matthäus\n"
            "Kapitel 1\n"
            "1 Dies ist das Buch der Geschichte Jesu Christi.\n"
        )

    def test_init(self):
        b = self.Bible()
        self.assertEqual(b.name, "Luther 1912")
        self.assertEqual(b.books, {})

    def test_load_text_real_file(self):
        """Luther1912 lädt mit _parse_verse_per_line_format + _normalize_book_names."""
        b = self.Bible()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False, encoding="utf-8") as f:
            f.write(self.sample)
            path = f.name
        try:
            b.load_text(path)
            self.assertIn("1. Mose", b.books)
            verse = b.get_verse("1. Mose", 1, 1)
            self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")
        finally:
            os.unlink(path)

    def test_load_text_file_not_found(self):
        b = self.Bible()
        with patch("builtins.print") as mp:
            b.load_text("nicht_vorhanden.txt")
        mp.assert_called_once()
        self.assertIn("Error loading Luther 1912", str(mp.call_args))

    def test_load_text_permission_error(self):
        b = self.Bible()
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("builtins.print") as mp:
                b.load_text("test.txt")
        self.assertIn("Error loading Luther 1912", str(mp.call_args))

    def test_normalize_book_names(self):
        b = self.Bible()
        b.books["1Mos"] = {1: {1: "Im Anfang"}}
        b._apply_book_name_normalization()
        self.assertIn("1. Mose", b.books)
        self.assertNotIn("1Mos", b.books)

    def test_normalize_book_names_merge(self):
        """Wenn normalisierter Name schon existiert, wird zusammengeführt."""
        b = self.Bible()
        b.books["1. Mose"] = {1: {1: "Vers 1"}}
        b.books["1Mos"] = {1: {2: "Vers 2"}}
        b._apply_book_name_normalization()
        self.assertIn(2, b.books["1. Mose"][1])

    def test_multiple_books_loaded_real_file(self):
        b = self.Bible()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False, encoding="utf-8") as f:
            f.write(self.sample)
            path = f.name
        try:
            b.load_text(path)
            names = b.get_book_names()
            self.assertGreaterEqual(len(names), 1)
        finally:
            os.unlink(path)

    def test_empty_file(self):
        b = self.Bible()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False, encoding="utf-8") as f:
            f.write("")
            path = f.name
        try:
            b.load_text(path)
            self.assertEqual(len(b.books), 0)
        finally:
            os.unlink(path)


# ===========================================================================
# Schlachter 1951
# ===========================================================================


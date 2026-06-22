import unittest
from unittest.mock import mock_open, patch, MagicMock
import os
import tempfile

class TestSchlachter1951(unittest.TestCase):

    def setUp(self):
        from schlachter1951 import Schlachter1951
        self.Bible = Schlachter1951
        self.sample = (
            "1. Mose\n"
            "Kapitel 1\n"
            "1 Im Anfang schuf Gott die Himmel und die Erde.\n"
            "2 Und die Erde war wüst und leer.\n"
            "2. Mose\n"
            "Kapitel 1\n"
            "1 Dies sind die Namen der Söhne Israels.\n"
        )

    def test_init(self):
        b = self.Bible()
        self.assertEqual(b.name, "Schlachter 1951")
        self.assertEqual(b.books, {})

    def test_load_text_real_file(self):
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
        self.assertIn("Error loading Schlachter 1951", str(mp.call_args))

    def test_load_text_permission_error(self):
        b = self.Bible()
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("builtins.print") as mp:
                b.load_text("test.txt")
        self.assertIn("Error loading Schlachter 1951", str(mp.call_args))

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

    def test_multiple_chapters_real(self):
        b = self.Bible()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False, encoding="utf-8") as f:
            f.write(self.sample)
            path = f.name
        try:
            b.load_text(path)
            self.assertEqual(b.get_chapter_count("1. Mose"), 1)
            self.assertEqual(b.get_verse_count("1. Mose", 1), 2)
        finally:
            os.unlink(path)

    def test_normalize_schlachter_book_name(self):
        b = self.Bible()
        # Methode wurde in bible_base.py zentralisiert
        self.assertEqual(b._normalize_german_book_name("1Mos"), "1. Mose")
        self.assertEqual(b._normalize_german_book_name("Mt"), "Matthäus")
        # Unbekannte Namen bleiben unverändert
        self.assertEqual(b._normalize_german_book_name("UnbekanntXYZ"), "UnbekanntXYZ")


# ===========================================================================
# World English Bible (web.py)
# ===========================================================================




if __name__ == "__main__":
    unittest.main()

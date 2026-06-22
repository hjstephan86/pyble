import unittest
import os
import tempfile
from unittest.mock import patch


class TestWorldEnglishBible(unittest.TestCase):

    def setUp(self):
        from web import WorldEnglishBible
        self.Bible = WorldEnglishBible
        self.sample = (
            "Genesis\n"
            "Chapter 1\n"
            "1 In the beginning God created the heavens and the earth.\n"
            "2 The earth was formless and empty.\n"
            "Matthew\n"
            "Chapter 1\n"
            "1 The book of the genealogy of Jesus Christ.\n"
        )

    def test_init(self):
        b = self.Bible()
        self.assertEqual(b.name, "WEB")
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
            self.assertEqual(verse, "In the beginning God created the heavens and the earth.")
        finally:
            os.unlink(path)

    def test_rename_books_to_german(self):
        b = self.Bible()
        b.books = {"Genesis": {1: {1: "In the beginning."}},
                   "Revelation": {22: {21: "Amen."}}}
        b._rename_books_to_german()
        self.assertIn("1. Mose", b.books)
        self.assertIn("Offenbarung", b.books)
        self.assertNotIn("Genesis", b.books)
        self.assertNotIn("Revelation", b.books)

    def test_rename_books_unknown_name_kept(self):
        """Unbekannte englische Buchnamen bleiben erhalten."""
        b = self.Bible()
        b.books = {"UnknownBook": {1: {1: "Some text."}}}
        b._rename_books_to_german()
        self.assertIn("UnknownBook", b.books)

    def test_load_text_file_not_found(self):
        b = self.Bible()
        with patch("builtins.print") as mp:
            b.load_text("nicht_vorhanden.txt")
        mp.assert_called_once()
        self.assertIn("Error loading World English Bible", str(mp.call_args))

    def test_load_text_permission_error(self):
        b = self.Bible()
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("builtins.print") as mp:
                b.load_text("test.txt")
        self.assertIn("Error loading World English Bible", str(mp.call_args))

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

    def test_multiple_books_renamed(self):
        b = self.Bible()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False, encoding="utf-8") as f:
            f.write(self.sample)
            path = f.name
        try:
            b.load_text(path)
            names = b.get_book_names()
            self.assertIn("1. Mose", names)
            self.assertIn("Matthäus", names)
        finally:
            os.unlink(path)


    def test_normalize_english_book_name_abbreviations(self):
        """Drei-Buchstaben-Abkürzungen werden auf den vollen englischen Namen abgebildet."""
        b = self.Bible()
        # AT-Abkürzungen
        self.assertEqual(b._normalize_english_book_name("Gen"), "Genesis")
        self.assertEqual(b._normalize_english_book_name("Exo"), "Exodus")
        self.assertEqual(b._normalize_english_book_name("Psa"), "Psalms")
        self.assertEqual(b._normalize_english_book_name("Son"), "Song of Solomon")
        self.assertEqual(b._normalize_english_book_name("Mal"), "Malachi")
        # NT-Abkürzungen
        self.assertEqual(b._normalize_english_book_name("Mat"), "Matthew")
        self.assertEqual(b._normalize_english_book_name("Rev"), "Revelation")
        self.assertEqual(b._normalize_english_book_name("1Co"), "1 Corinthians")
        self.assertEqual(b._normalize_english_book_name("2Ti"), "2 Timothy")

    def test_normalize_english_book_name_full_name_mappings(self):
        """Erweiterte Kurznamen (mit Leerzeichen) werden korrekt aufgelöst."""
        b = self.Bible()
        self.assertEqual(b._normalize_english_book_name("1 Sam"), "1 Samuel")
        self.assertEqual(b._normalize_english_book_name("2 Kin"), "2 Kings")
        self.assertEqual(b._normalize_english_book_name("1 Cor"), "1 Corinthians")
        self.assertEqual(b._normalize_english_book_name("1 Pet"), "1 Peter")
        self.assertEqual(b._normalize_english_book_name("3 Joh"), "3 John")

    def test_normalize_english_book_name_unknown(self):
        """Unbekannte Namen werden unverändert zurückgegeben."""
        b = self.Bible()
        self.assertEqual(b._normalize_english_book_name("Unknown"), "Unknown")
        self.assertEqual(b._normalize_english_book_name("Genesis"), "Genesis")


if __name__ == "__main__":
    unittest.main()

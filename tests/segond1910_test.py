import unittest
import os
import tempfile
from unittest.mock import patch


class TestSegond1910(unittest.TestCase):

    def setUp(self):
        from segond1910 import Segond1910
        self.Bible = Segond1910
        self.sample = (
            "Genèse\n"
            "Chapitre 1\n"
            "1 Au commencement, Dieu créa les cieux et la terre.\n"
            "2 La terre était informe et vide.\n"
            "Matthieu\n"
            "Chapitre 1\n"
            "1 Généalogie de Jésus-Christ, fils de David.\n"
        )

    def test_init(self):
        b = self.Bible()
        self.assertEqual(b.name, "Segond 1910")
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
            self.assertEqual(verse, "Au commencement, Dieu créa les cieux et la terre.")
        finally:
            os.unlink(path)

    def test_rename_books_to_german(self):
        b = self.Bible()
        b.books = {"Genèse": {1: {1: "Au commencement."}},
                   "Apocalypse": {22: {21: "Amen."}}}
        b._rename_books_to_german()
        self.assertIn("1. Mose", b.books)
        self.assertIn("Offenbarung", b.books)
        self.assertNotIn("Genèse", b.books)
        self.assertNotIn("Apocalypse", b.books)

    def test_rename_books_unknown_name_kept(self):
        """Unbekannte französische Buchnamen bleiben erhalten."""
        b = self.Bible()
        b.books = {"UnknownBook": {1: {1: "Some text."}}}
        b._rename_books_to_german()
        self.assertIn("UnknownBook", b.books)

    def test_load_text_file_not_found(self):
        b = self.Bible()
        with patch("builtins.print") as mp:
            b.load_text("nicht_vorhanden.txt")
        mp.assert_called_once()
        self.assertIn("Error loading Segond 1910", str(mp.call_args))

    def test_load_text_permission_error(self):
        b = self.Bible()
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("builtins.print") as mp:
                b.load_text("test.txt")
        self.assertIn("Error loading Segond 1910", str(mp.call_args))

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


if __name__ == "__main__":
    unittest.main()

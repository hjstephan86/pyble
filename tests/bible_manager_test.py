import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import os
from src.bible_manager import BibleManager
from src.elberfelder1905 import Elberfelder1905


class TestBibleManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = BibleManager()
        self.sample_content = """1. Mose
Kapitel 1
1 Im Anfang schuf Gott die Himmel und die Erde.
2 Und die Erde war wüst und leer und Finsternis war über der Tiefe und der Geist Gottes schwebte über den Wassern.
3 Und Gott sprach: Es werde Licht! und es ward Licht.
"""
    
    def test_init(self):
        """Test BibleManager initialization"""
        self.assertEqual(self.manager.bibles, {})
        self.assertIsInstance(self.manager.bibles, dict)
    
    def test_load_bibles_directory_not_exists(self):
        """Test loading bibles when directory doesn't exist"""
        with patch('builtins.print') as mock_print:
            self.manager.load_bibles("non_existent_directory")
            mock_print.assert_called_once_with("Warning: Texts directory non_existent_directory not found")
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_bibles_no_files(self, mock_glob, mock_exists):
        """Test loading bibles when no txt files exist"""
        mock_exists.return_value = True
        mock_glob.return_value = []
        
        self.manager.load_bibles("test_dir")
        self.assertEqual(len(self.manager.bibles), 0)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_bibles_elberfelder1905(self, mock_file, mock_glob, mock_exists):
        """Test loading Elberfelder1905 bible"""
        mock_exists.return_value = True
        
        # Mock file path
        mock_file_path = MagicMock()
        mock_file_path.stem = "elberfelder1905_test"
        mock_glob.return_value = [mock_file_path]
        
        # Mock file content
        mock_file.return_value.read.return_value = self.sample_content
        
        with patch('src.bible_manager.Elberfelder1905') as MockElberfelder:
            mock_bible = MagicMock()
            mock_bible.name = "Elberfelder 1905"
            mock_bible.books = {"1. Mose": {1: {1: "Im Anfang schuf Gott die Himmel und die Erde."}}}
            MockElberfelder.return_value = mock_bible
            
            with patch('builtins.print') as mock_print:
                self.manager.load_bibles("test_dir")
                
                # Verify bible was loaded
                MockElberfelder.assert_called_once()
                mock_bible.load_text.assert_called_once()
                mock_print.assert_called_once_with("Loaded Elberfelder 1905 with 1 books")
                
                # Verify bible was added to manager (Key wird intern .upper() gespeichert)
                self.assertIn("ELBERFELDER 1905", self.manager.bibles)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_bibles_unknown_format(self, mock_glob, mock_exists):
        """Test loading bible with unknown format"""
        mock_exists.return_value = True
        
        # Mock file path with unknown format
        mock_file_path = MagicMock()
        mock_file_path.stem = "unknown_bible_format"
        mock_glob.return_value = [mock_file_path]
        
        with patch('builtins.print') as mock_print:
            self.manager.load_bibles("test_dir")
            
            # Should print warning about unknown format
            mock_print.assert_called_once_with("Warning: No specific parser found for unknown_bible_format, skipping")
            
            # No bibles should be loaded
            self.assertEqual(len(self.manager.bibles), 0)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_bibles_empty_content(self, mock_glob, mock_exists):
        """Test loading bible with empty content"""
        mock_exists.return_value = True
        
        mock_file_path = MagicMock()
        mock_file_path.stem = "elberfelder1905_empty"
        mock_glob.return_value = [mock_file_path]
        
        with patch('src.bible_manager.Elberfelder1905') as MockElberfelder:
            mock_bible = MagicMock()
            mock_bible.name = "Elberfelder 1905"
            mock_bible.books = {}  # Empty books
            MockElberfelder.return_value = mock_bible
            
            with patch('builtins.print') as mock_print:
                self.manager.load_bibles("test_dir")
                
                # Should print warning about no content
                mock_print.assert_called_once_with("Warning: No content loaded from elberfelder1905_empty")
                
                # No bibles should be in manager
                self.assertEqual(len(self.manager.bibles), 0)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_bibles_multiple_formats(self, mock_glob, mock_exists):
        """Test loading multiple bible formats"""
        mock_exists.return_value = True
        
        # Mock multiple file paths
        mock_elberfelder_path = MagicMock()
        mock_elberfelder_path.stem = "elberfelder1905_test"
        mock_world_path = MagicMock()
        mock_world_path.stem = "world_english_bible"
        mock_schlachter_path = MagicMock()
        mock_schlachter_path.stem = "schlachter1951_test"
        
        mock_glob.return_value = [mock_elberfelder_path, mock_world_path, mock_schlachter_path]
        
        with patch('src.bible_manager.Elberfelder1905') as MockElberfelder, \
             patch('src.bible_manager.WorldEnglishBible') as MockWorld, \
             patch('src.bible_manager.Schlachter1951') as MockSchlachter:
            
            # Mock bible instances
            mock_elberfelder = MagicMock()
            mock_elberfelder.name = "Elberfelder 1905"
            mock_elberfelder.books = {"1. Mose": {}}
            MockElberfelder.return_value = mock_elberfelder
            
            mock_world = MagicMock()
            mock_world.name = "WEB"
            mock_world.books = {"Genesis": {}}
            MockWorld.return_value = mock_world
            
            mock_schlachter = MagicMock()
            mock_schlachter.name = "Schlachter 1951"
            mock_schlachter.books = {"1. Mose": {}}
            MockSchlachter.return_value = mock_schlachter
            
            with patch('builtins.print'):
                self.manager.load_bibles("test_dir")
                
                # Verify all bibles were loaded (Keys werden intern .upper() gespeichert)
                self.assertEqual(len(self.manager.bibles), 3)
                self.assertIn("ELBERFELDER 1905", self.manager.bibles)
                self.assertIn("WEB", self.manager.bibles)
                self.assertIn("SCHLACHTER 1951", self.manager.bibles)
    
    def test_get_bible_existing(self):
        """Test getting existing bible translation"""
        # Add a mock bible (Key wird intern .upper() gespeichert)
        mock_bible = MagicMock()
        self.manager.bibles["TESTBIBLE"] = mock_bible

        result = self.manager.get_bible("TestBible")
        self.assertEqual(result, mock_bible)
    
    def test_get_bible_non_existing(self):
        """Test getting non-existing bible translation"""
        result = self.manager.get_bible("NonExistentBible")
        self.assertIsNone(result)
    
    def test_get_translation_names_empty(self):
        """Test getting translation names when no bibles loaded"""
        names = self.manager.get_translation_names()
        self.assertEqual(names, [])
    
    def test_get_translation_names_with_bibles(self):
        """Test getting translation names with loaded bibles"""
        # Add mock bibles – Key .upper(), Mock bekommt .name für get_translation_names()
        mock1 = MagicMock(); mock1.name = "Bible1"
        mock2 = MagicMock(); mock2.name = "Bible2"
        mock3 = MagicMock(); mock3.name = "Bible3"
        self.manager.bibles["BIBLE1"] = mock1
        self.manager.bibles["BIBLE2"] = mock2
        self.manager.bibles["BIBLE3"] = mock3

        names = self.manager.get_translation_names()
        self.assertEqual(len(names), 3)
        self.assertIn("Bible1", names)
        self.assertIn("Bible2", names)
        self.assertIn("Bible3", names)
    
    def test_load_bibles_case_insensitive_matching(self):
        """Test that bible format matching is case insensitive"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            
            # Test uppercase pattern
            mock_file_path = MagicMock()
            mock_file_path.stem = "ELBERFELDER1905_test"
            mock_glob.return_value = [mock_file_path]
            
            with patch('src.bible_manager.Elberfelder1905') as MockElberfelder:
                mock_bible = MagicMock()
                mock_bible.name = "Elberfelder 1905"
                mock_bible.books = {"1. Mose": {}}
                MockElberfelder.return_value = mock_bible
                
                with patch('builtins.print'):
                    self.manager.load_bibles("test_dir")
                    
                    # Should still match due to case insensitive comparison
                    self.assertEqual(len(self.manager.bibles), 1)
    
    def test_load_bibles_partial_pattern_matching(self):
        """Test that bible format matching works with partial patterns"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            
            # Test files with pattern in middle of filename
            mock_file_path = MagicMock()
            mock_file_path.stem = "german_elberfelder1905_complete"
            mock_glob.return_value = [mock_file_path]
            
            with patch('src.bible_manager.Elberfelder1905') as MockElberfelder:
                mock_bible = MagicMock()
                mock_bible.name = "Elberfelder 1905"
                mock_bible.books = {"1. Mose": {}}
                MockElberfelder.return_value = mock_bible
                
                with patch('builtins.print'):
                    self.manager.load_bibles("test_dir")
                    
                    # Should match due to 'elberfelder1905' being in filename
                    self.assertEqual(len(self.manager.bibles), 1)
    
    def test_bible_manager_integration(self):
        """Test complete integration workflow"""
        # Create and load a bible
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            mock_file_path = MagicMock()
            mock_file_path.stem = "elberfelder1905"
            mock_glob.return_value = [mock_file_path]
            
            with patch('src.bible_manager.Elberfelder1905') as MockElberfelder:
                # Create realistic mock bible
                mock_bible = MagicMock()
                mock_bible.name = "Elberfelder 1905"
                mock_bible.books = {
                    "1. Mose": {
                        1: {
                            1: "Im Anfang schuf Gott die Himmel und die Erde.",
                            2: "Und die Erde war wüst und leer."
                        }
                    }
                }
                MockElberfelder.return_value = mock_bible
                
                with patch('builtins.print'):
                    # Load bibles
                    self.manager.load_bibles("test_dir")
                    
                    # Test retrieval operations
                    names = self.manager.get_translation_names()
                    self.assertEqual(names, ["Elberfelder 1905"])
                    
                    bible = self.manager.get_bible("Elberfelder 1905")
                    self.assertIsNotNone(bible)
                    self.assertEqual(bible.name, "Elberfelder 1905")
                    
                    # Test non-existent bible
                    non_existent = self.manager.get_bible("NonExistent")
                    self.assertIsNone(non_existent)


if __name__ == '__main__':
    unittest.main()


"""
test_api_coverage.py – Gezielte Tests für verbleibende Coverage-Lücken.

Abgedeckte Bereiche:
- main.py: alle API-Routen (strong, search, count, chapter-count,
           verse-count, book, chapter, verse, chapter-list)
- bible_manager.py: search_bible (Translation + alle Übersetzungen)
- strong_manager.py: load mit XML, reflink-Parsing, rank-Zweige
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _src not in sys.path:
    sys.path.insert(0, _src)

# ---------------------------------------------------------------------------
# Hilfsfunktion: echter BibleManager mit Mini-Bibel
# ---------------------------------------------------------------------------

def _make_bible_manager():
    """BibleManager mit einer kleinen In-Memory-Bibel."""
    from bible_manager import BibleManager
    from bible_base import Bible

    class MiniBible(Bible):
        def load_text(self, fp):
            self._parse_text(
                "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.\n"
                "0#1. Mose#1#2#Und die Erde war wüst und leer.\n"
                "0#1. Mose#2#1#Und die Himmel und die Erde wurden vollendet.\n"
                "0#Johannes#3#16#Also hat Gott die Welt geliebt."
            )

    mgr = BibleManager()
    b = MiniBible("TestBible")
    b.load_text("")
    b.book_positions = {n: i for i, n in enumerate(b.books.keys())}
    mgr.bibles["TESTBIBLE"] = b
    return mgr, b


# ===========================================================================
# BibleManager.search_bible
# ===========================================================================

class TestBibleManagerSearchBible(unittest.TestCase):

    def setUp(self):
        self.mgr, self.bible = _make_bible_manager()

    def test_search_in_specific_translation(self):
        result = self.mgr.search_bible("Gott", translation="TestBible")
        self.assertGreater(result["total"], 0)
        self.assertIn("results", result)
        for r in result["results"]:
            self.assertEqual(r["translation"], "TestBible")
            self.assertIn("book", r)
            self.assertIn("chapter", r)
            self.assertIn("verse", r)

    def test_search_all_translations(self):
        result = self.mgr.search_bible("Gott")
        self.assertGreater(result["total"], 0)
        self.assertIn("results", result)

    def test_search_with_book_filter(self):
        result = self.mgr.search_bible("Gott", translation="TestBible", book="1. Mose")
        for r in result["results"]:
            self.assertEqual(r["book"], "1. Mose")

    def test_search_not_found(self):
        result = self.mgr.search_bible("XYZnichtvorhanden", translation="TestBible")
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["results"], [])

    def test_search_invalid_translation(self):
        result = self.mgr.search_bible("Gott", translation="NichtVorhanden")
        self.assertEqual(result["total"], 0)

    def test_search_all_translations_multiple_bibles(self):
        from bible_base import Bible
        class Mini2(Bible):
            def load_text(self, fp):
                self._parse_text("0#Genesis#1#1#In the beginning God created.")
        b2 = Mini2("Bible2")
        b2.load_text("")
        b2.book_positions = {n: i for i, n in enumerate(b2.books.keys())}
        self.mgr.bibles["BIBLE2"] = b2
        result = self.mgr.search_bible("Gott")
        # Nur TestBible hat "Gott"
        self.assertGreater(result["total"], 0)

    def test_search_result_structure(self):
        result = self.mgr.search_bible("Gott", translation="TestBible")
        self.assertIn("total", result)
        self.assertIn("results", result)
        if result["results"]:
            r = result["results"][0]
            self.assertIn("hit_count", r)
            self.assertIn("text", r)


# ===========================================================================
# StrongManager – verbleibende Pfade
# ===========================================================================


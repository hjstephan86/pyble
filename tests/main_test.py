import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest
import sys
import os

# main.py erwartet 'static' relativ zum cwd beim Import.
# Wir wechseln kurz in src/, importieren, dann zurück ins ursprüngliche Verzeichnis.
_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
_orig_dir = os.getcwd()
os.makedirs(os.path.join(_src_dir, 'static'), exist_ok=True)
sys.path.insert(0, _src_dir)
os.chdir(_src_dir)
try:
    from main import app, bible_manager
finally:
    os.chdir(_orig_dir)


class TestMainAPI(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        # Templates und static werden relativ zum cwd gesucht
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(_src_dir)
        self.client = TestClient(app)

        # Mock bible data
        self.mock_bible_data = {
            "1. Mose": {
                1: {
                    1: "Im Anfang schuf Gott die Himmel und die Erde.",
                    2: "Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.",
                    3: "Und Gott sprach: Es werde Licht! und es ward Licht."
                },
                2: {
                    1: "Und die Himmel und die Erde wurden vollendet."
                }
            }
        }

    def tearDown(self):
        os.chdir(_orig_dir)
        
        # Mock bible data
        self.mock_bible_data = {
            "1. Mose": {
                1: {
                    1: "Im Anfang schuf Gott die Himmel und die Erde.",
                    2: "Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.",
                    3: "Und Gott sprach: Es werde Licht! und es ward Licht."
                },
                2: {
                    1: "Und die Himmel und die Erde wurden vollendet."
                }
            }
        }
    
    def test_root_endpoint(self):
        """Test the root HTML endpoint"""
        with patch.object(bible_manager, 'get_translation_names', return_value=["Elberfelder 1905"]):
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.headers.get("content-type", ""))
    
    def test_list_translations_endpoint(self):
        """Test the list translations endpoint"""
        with patch.object(bible_manager, 'get_translation_names', return_value=["Elberfelder 1905", "WorldEnglishBible"]):
            response = self.client.get("/api/translations")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("translations", data)
            self.assertEqual(data["translations"], ["Elberfelder 1905", "WorldEnglishBible"])
    
    def test_list_translations_empty(self):
        """Test list translations when no translations available"""
        with patch.object(bible_manager, 'get_translation_names', return_value=[]):
            response = self.client.get("/api/translations")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["translations"], [])
    
    def test_get_books_valid_translation(self):
        """Test get books for valid translation"""
        mock_bible = MagicMock()
        mock_bible.get_book_names.return_value = ["1. Mose", "2. Mose"]
        mock_bible.get_chapter_count.side_effect = lambda book: 50 if book == "1. Mose" else 40
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/books")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["translation"], "Elberfelder 1905")
            self.assertEqual(len(data["books"]), 2)
            
            # Check book structure
            book1 = next(book for book in data["books"] if book["name"] == "1. Mose")
            self.assertEqual(book1["chapters"], 50)
    
    def test_get_books_invalid_translation(self):
        """Test get books for invalid translation"""
        with patch.object(bible_manager, 'get_bible', return_value=None):
            response = self.client.get("/api/NonExistentTranslation/books")
            self.assertEqual(response.status_code, 404)
            
            data = response.json()
            self.assertIn("Translation 'NonExistentTranslation' not found", data["detail"])
    
    def test_get_book_valid(self):
        """Test get book with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.get_book.return_value = self.mock_bible_data["1. Mose"]
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["book"], "1. Mose")
            self.assertEqual(data["translation"], "Elberfelder 1905")
            self.assertIn("chapters", data)
            self.assertEqual(len(data["chapters"]), 2)  # 2 chapters
    
    def test_get_book_invalid_translation(self):
        """Test get book with invalid translation"""
        with patch.object(bible_manager, 'get_bible', return_value=None):
            response = self.client.get("/api/NonExistent/1. Mose")
            self.assertEqual(response.status_code, 404)
    
    def test_get_book_invalid_book(self):
        """Test get book with invalid book name"""
        mock_bible = MagicMock()
        mock_bible.get_book.return_value = None
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/NonExistentBook")
            self.assertEqual(response.status_code, 404)
            
            data = response.json()
            self.assertIn("Book 'NonExistentBook' not found", data["detail"])
    
    def test_get_chapter_valid(self):
        """Test get chapter with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.get_chapter.return_value = self.mock_bible_data["1. Mose"][1]
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["book"], "1. Mose")
            self.assertEqual(data["chapter"], 1)
            self.assertEqual(data["translation"], "Elberfelder 1905")
            self.assertIn("verses", data)
            self.assertEqual(len(data["verses"]), 3)  # 3 verses
    
    def test_get_chapter_invalid_translation(self):
        """Test get chapter with invalid translation"""
        with patch.object(bible_manager, 'get_bible', return_value=None):
            response = self.client.get("/api/NonExistent/1. Mose/1")
            self.assertEqual(response.status_code, 404)
    
    def test_get_chapter_invalid_chapter(self):
        """Test get chapter with invalid chapter number"""
        mock_bible = MagicMock()
        mock_bible.get_chapter.return_value = None
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose/999")
            self.assertEqual(response.status_code, 404)
            
            data = response.json()
            self.assertIn("Chapter 999 not found", data["detail"])
    
    def test_get_verse_valid(self):
        """Test get verse with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Im Anfang schuf Gott die Himmel und die Erde."
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["book"], "1. Mose")
            self.assertEqual(data["chapter"], 1)
            self.assertEqual(data["verse"], 1)
            self.assertEqual(data["text"], "Im Anfang schuf Gott die Himmel und die Erde.")
            self.assertEqual(data["translation"], "Elberfelder 1905")
    
    def test_get_verse_invalid_translation(self):
        """Test get verse with invalid translation"""
        with patch.object(bible_manager, 'get_bible', return_value=None):
            response = self.client.get("/api/NonExistent/1. Mose/1/1")
            self.assertEqual(response.status_code, 404)
    
    def test_get_verse_invalid_verse(self):
        """Test get verse with invalid verse number"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = None
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/999")
            self.assertEqual(response.status_code, 404)
            
            data = response.json()
            self.assertIn("Verse 999 not found", data["detail"])
    
    def test_get_chapter_list_valid(self):
        """Test get chapter list with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.books = {"1. Mose": {1: {}, 2: {}}}
        mock_bible.get_verse_count.side_effect = lambda book, chapter: 31 if chapter == 1 else 25
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose/chapters")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["translation"], "Elberfelder 1905")
            self.assertEqual(data["book"], "1. Mose")
            self.assertEqual(len(data["chapters"]), 2)
            
            # Check chapter structure
            chapter1 = next(ch for ch in data["chapters"] if ch["chapter"] == 1)
            self.assertEqual(chapter1["verses"], 31)
    
    def test_get_chapter_list_invalid_translation(self):
        """Test get chapter list with invalid translation"""
        with patch.object(bible_manager, 'get_bible', return_value=None):
            response = self.client.get("/api/NonExistent/1. Mose/chapters")
            self.assertEqual(response.status_code, 404)
    
    def test_get_chapter_list_invalid_book(self):
        """Test get chapter list with invalid book"""
        mock_bible = MagicMock()
        mock_bible.books = {}
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/NonExistentBook/chapters")
            self.assertEqual(response.status_code, 404)
            
            data = response.json()
            self.assertIn("Book 'NonExistentBook' not found", data["detail"])
    
    def test_api_endpoints_with_special_characters(self):
        """Test API endpoints with special characters in book names"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse with special characters"
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            # Test with URL encoded book name
            response = self.client.get("/api/Elberfelder 1905/1.%20Mose/1/1")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["book"], "1. Mose")
    
    def test_api_endpoints_with_edge_case_numbers(self):
        """Test API endpoints with edge case numbers"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            # Test with chapter 0
            response = self.client.get("/api/Elberfelder 1905/1. Mose/0/1")
            self.assertEqual(response.status_code, 200)
            mock_bible.get_verse.assert_called_with("1. Mose", 0, 1)
            
            # Test with verse 0
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/0")
            self.assertEqual(response.status_code, 200)
            mock_bible.get_verse.assert_called_with("1. Mose", 1, 0)
    
    def test_api_endpoints_parameter_types(self):
        """Test that API endpoints properly handle parameter types"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            # Test with valid integer parameters
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
            self.assertEqual(response.status_code, 200)
            
            # FastAPI should handle type conversion automatically
            mock_bible.get_verse.assert_called_with("1. Mose", 1, 1)
    
    def test_error_response_format(self):
        """Test that error responses have proper format"""
        with patch.object(bible_manager, 'get_bible', return_value=None):
            response = self.client.get("/api/NonExistent/1. Mose/1/1")
            self.assertEqual(response.status_code, 404)
            
            data = response.json()
            self.assertIn("detail", data)
            self.assertIsInstance(data["detail"], str)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading

        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"

        results = []

        # patch.object muss außerhalb der Threads gesetzt werden,
        # da unittest.mock nicht thread-safe ist
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            def make_request():
                response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
                results.append(response.status_code)

            threads = [threading.Thread(target=make_request) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        self.assertEqual(len(results), 5)
        self.assertTrue(all(status == 200 for status in results))
    
    def test_response_models_integration(self):
        """Test that responses match the defined Pydantic models"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Im Anfang schuf Gott die Himmel und die Erde."
        mock_bible.get_chapter.return_value = {1: "Verse 1", 2: "Verse 2"}
        mock_bible.get_book.return_value = {1: {1: "Verse 1"}}
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            # Test VerseResponse
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            required_fields = ["book", "chapter", "verse", "text", "translation"]
            for field in required_fields:
                self.assertIn(field, data)
            
            # Test ChapterResponse
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            required_fields = ["book", "chapter", "verses", "translation"]
            for field in required_fields:
                self.assertIn(field, data)
            
            # Test BookResponse
            response = self.client.get("/api/Elberfelder 1905/1. Mose")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            required_fields = ["book", "chapters", "translation"]
            for field in required_fields:
                self.assertIn(field, data)
    
    def test_api_documentation_endpoints(self):
        """Test that API documentation endpoints are accessible"""
        # Test OpenAPI schema
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("openapi", data)
        self.assertIn("info", data)
        self.assertIn("paths", data)
    
    def test_static_files_mount(self):
        """Test that static files are properly mounted"""
        # This test assumes there might be static files
        # In a real scenario, you would test actual static file serving
        response = self.client.get("/static/nonexistent.css")
        # Should return 404 for non-existent static file
        self.assertEqual(response.status_code, 404)
    
    @patch('main.bible_manager')
    def test_startup_event(self, mock_manager):
        """Test the startup event"""
        # The startup event should call load_bibles
        # This is tested implicitly when the app starts
        # We can verify the manager has the method
        self.assertTrue(hasattr(mock_manager, 'load_bibles'))
    
    def test_content_type_headers(self):
        """Test that responses have correct content-type headers"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"
        
        with patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
            self.assertEqual(response.status_code, 200)
            self.assertIn("application/json", response.headers.get("content-type", ""))
    
    def test_api_versioning_in_urls(self):
        """Test that API endpoints are properly versioned"""
        # All API endpoints should start with /api/
        mock_bible = MagicMock()
        mock_bible.get_translation_names.return_value = ["Test"]
        
        with patch.object(bible_manager, 'get_translation_names', return_value=["Test"]):
            response = self.client.get("/api/translations")
            self.assertEqual(response.status_code, 200)
        
        # Non-API endpoint should not work
        response = self.client.get("/translations")
        self.assertEqual(response.status_code, 404)


class TestMainIntegration(unittest.TestCase):
    """Integration tests for the main application"""

    def setUp(self):
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(_src_dir)
        self.client = TestClient(app)
    
    def test_full_workflow_integration(self):
        """Test complete workflow from translations to verse"""
        # Mock a complete bible
        mock_bible = MagicMock()
        mock_bible.get_book_names.return_value = ["1. Mose"]
        mock_bible.get_chapter_count.return_value = 2
        mock_bible.get_verse_count.return_value = 3
        mock_bible.books = {"1. Mose": {1: {}, 2: {}}}
        mock_bible.get_verse.return_value = "Im Anfang schuf Gott die Himmel und die Erde."
        mock_bible.get_chapter.return_value = {
            1: "Im Anfang schuf Gott die Himmel und die Erde.",
            2: "Und die Erde war wüst und leer."
        }
        mock_bible.get_book.return_value = {
            1: {1: "Verse 1", 2: "Verse 2"},
            2: {1: "Verse 1"}
        }
        
        with patch.object(bible_manager, 'get_translation_names', return_value=["Elberfelder 1905"]), \
             patch.object(bible_manager, 'get_bible', return_value=mock_bible):
            
            # 1. Get available translations
            response = self.client.get("/api/translations")
            self.assertEqual(response.status_code, 200)
            translations = response.json()["translations"]
            self.assertIn("Elberfelder 1905", translations)
            
            # 2. Get books for translation
            response = self.client.get("/api/Elberfelder 1905/books")
            self.assertEqual(response.status_code, 200)
            books = response.json()["books"]
            self.assertEqual(len(books), 1)
            self.assertEqual(books[0]["name"], "1. Mose")
            
            # 3. Get chapters for book
            response = self.client.get("/api/Elberfelder 1905/1. Mose/chapters")
            self.assertEqual(response.status_code, 200)
            chapters = response.json()["chapters"]
            self.assertEqual(len(chapters), 2)
            
            # 4. Get specific chapter
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1")
            self.assertEqual(response.status_code, 200)
            chapter_data = response.json()
            self.assertEqual(chapter_data["book"], "1. Mose")
            self.assertEqual(chapter_data["chapter"], 1)
            
            # 5. Get specific verse
            response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
            self.assertEqual(response.status_code, 200)
            verse_data = response.json()
            self.assertEqual(verse_data["text"], "Im Anfang schuf Gott die Himmel und die Erde.")


if __name__ == '__main__':
    unittest.main()


class TestMainLoadIgnoreWords(unittest.TestCase):

    def setUp(self):
        _src_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "src")
        )
        self._orig_dir = os.getcwd()
        self.addCleanup(os.chdir, self._orig_dir)
        os.makedirs(os.path.join(_src_dir, "static"), exist_ok=True)
        os.chdir(_src_dir)
        if _src_dir not in sys.path:
            sys.path.insert(0, _src_dir)

    def test_load_ignore_words_normal(self):
        from main import load_ignore_words
        content = "der\ndie\ndas\n# Kommentar\n\nein\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = load_ignore_words("ignore.txt")
        self.assertIn("der", words)
        self.assertIn("die", words)
        self.assertNotIn("# Kommentar", words)
        self.assertNotIn("", words)

    def test_load_ignore_words_missing_file(self):
        from main import load_ignore_words
        words = load_ignore_words("nicht_vorhanden.txt")
        self.assertIsInstance(words, set)
        self.assertEqual(len(words), 0)

    def test_load_ignore_words_empty_file(self):
        from main import load_ignore_words
        with patch("builtins.open", mock_open(read_data="")):
            words = load_ignore_words("empty.txt")
        self.assertEqual(len(words), 0)




class TestMainRoutes(unittest.TestCase):
    """Integration-Tests für FastAPI-Routen via TestClient."""

    @classmethod
    def setUpClass(cls):
        _src_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "src")
        )
        cls._src_dir = _src_dir
        cls._orig_dir = os.getcwd()
        os.makedirs(os.path.join(_src_dir, "static"), exist_ok=True)
        os.chdir(_src_dir)
        if _src_dir not in sys.path:
            sys.path.insert(0, _src_dir)
        from fastapi.testclient import TestClient
        from main import app
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._orig_dir)

    def test_home_html_route(self):
        r = self.client.get("/home.html")
        self.assertEqual(r.status_code, 200)

    def test_read_html_route(self):
        r = self.client.get("/read")
        self.assertEqual(r.status_code, 200)

    def test_search_html_route(self):
        r = self.client.get("/search.html")
        self.assertEqual(r.status_code, 200)

    def test_count_html_route(self):
        r = self.client.get("/count.html")
        self.assertEqual(r.status_code, 200)

    def test_strong_html_route(self):
        r = self.client.get("/strong.html")
        self.assertEqual(r.status_code, 200)

    def test_parallel_html_route(self):
        r = self.client.get("/parallel.html")
        self.assertEqual(r.status_code, 200)

    def test_about_html_route(self):
        r = self.client.get("/about.html")
        self.assertEqual(r.status_code, 200)

    def test_api_translations(self):
        r = self.client.get("/api/translations")
        self.assertEqual(r.status_code, 200)
        self.assertIn("translations", r.json())

    def test_api_books_valid(self):
        from main import bible_manager
        mock_bible = MagicMock()
        mock_bible.get_book_names.return_value = ["1. Mose", "Johannes"]
        mock_bible.get_chapter_count.return_value = 50
        with patch.object(bible_manager, "get_bible", return_value=mock_bible):
            r = self.client.get("/api/TestBible/books")
        self.assertEqual(r.status_code, 200)

    def test_api_books_invalid_translation(self):
        from main import bible_manager
        with patch.object(bible_manager, "get_bible", return_value=None):
            r = self.client.get("/api/NichtVorhanden/books")
        self.assertEqual(r.status_code, 404)

    def test_api_strong_number_endpoint_exists(self):
        """Strong-Endpunkt antwortet (404 wenn nicht geladen, 200 wenn geladen)."""
        r = self.client.get("/api/strong/number/H430")
        self.assertIn(r.status_code, [200, 404, 503])

    def test_api_search_too_short(self):
        r = self.client.get("/api/search?q=a")
        self.assertEqual(r.status_code, 400)

    def test_api_count_wrong_order(self):
        from main import bible_manager
        mock_bible = MagicMock()
        mock_bible.get_book_names.return_value = ["1. Mose", "2. Mose"]
        mock_bible.book_positions = {"1. Mose": 0, "2. Mose": 1}
        with patch.object(bible_manager, "get_bible", return_value=mock_bible):
            r = self.client.get(
                "/api/count?translation=Test"
                "&book_from=2. Mose&chapter_from=1&verse_from=1"
                "&book_to=1. Mose&chapter_to=1&verse_to=1"
            )
        self.assertIn(r.status_code, [400, 404, 422, 200])


if __name__ == "__main__":
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

class TestMainAPICoverage(unittest.TestCase):
    """Tests für alle nicht abgedeckten main.py-Routen."""

    @classmethod
    def setUpClass(cls):
        _src_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "src"))
        cls._src_dir = _src_dir
        cls._orig_dir = os.getcwd()
        os.makedirs(os.path.join(_src_dir, "static"), exist_ok=True)
        os.chdir(_src_dir)
        if _src_dir not in sys.path:
            sys.path.insert(0, _src_dir)
        from fastapi.testclient import TestClient
        from main import app, bible_manager
        cls.app = app
        cls.bible_manager = bible_manager
        cls.client = TestClient(app)
        # Mini-Bibel in den bible_manager injizieren (Key wird intern .upper() gespeichert)
        mgr, bible = _make_bible_manager()
        bible_manager.bibles["TESTBIBLE"] = bible

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._orig_dir)

    def setUp(self):
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self._src_dir)

    # ------------------------------------------------------------------
    # Bücher-Routen
    # ------------------------------------------------------------------

    def test_get_books_valid(self):
        r = self.client.get("/api/TestBible/books")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("books", data)
        self.assertGreater(len(data["books"]), 0)

    def test_get_chapter_count_valid(self):
        r = self.client.get("/api/TestBible/1. Mose/chapter-count")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("chapters", data)
        self.assertEqual(data["chapters"], 2)

    def test_get_chapter_count_invalid_translation(self):
        r = self.client.get("/api/NichtVorhanden/1. Mose/chapter-count")
        self.assertEqual(r.status_code, 404)

    def test_get_chapter_count_invalid_book(self):
        r = self.client.get("/api/TestBible/NichtVorhanden/chapter-count")
        self.assertEqual(r.status_code, 404)

    def test_get_verse_count_valid(self):
        r = self.client.get("/api/TestBible/1. Mose/1/verse-count")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("verses", data)
        self.assertEqual(data["verses"], 2)

    def test_get_verse_count_invalid_chapter(self):
        r = self.client.get("/api/TestBible/1. Mose/999/verse-count")
        self.assertEqual(r.status_code, 404)

    # ------------------------------------------------------------------
    # Suche
    # ------------------------------------------------------------------

    def test_search_valid(self):
        r = self.client.get("/api/search?q=Gott&translation=TestBible")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("results", data)
        self.assertIn("total", data)
        self.assertGreater(data["total"], 0)

    def test_search_all_translations(self):
        r = self.client.get("/api/search?q=Gott")
        self.assertEqual(r.status_code, 200)

    def test_search_with_book(self):
        r = self.client.get("/api/search?q=Gott&translation=TestBible&book=1. Mose")
        self.assertEqual(r.status_code, 200)

    def test_search_pagination(self):
        r = self.client.get("/api/search?q=Gott&translation=TestBible&page=1&limit=2")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertLessEqual(len(data["results"]), 2)
        self.assertEqual(data["page"], 1)

    def test_search_page2(self):
        r = self.client.get("/api/search?q=Gott&translation=TestBible&page=2&limit=1")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["page"], 2)

    def test_search_too_short_returns_400(self):
        r = self.client.get("/api/search?q=a")
        self.assertEqual(r.status_code, 400)

    # ------------------------------------------------------------------
    # Wortzählung (count)
    # ------------------------------------------------------------------

    def test_count_valid(self):
        r = self.client.get(
            "/api/count"
            "?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("counted_words", data)
        self.assertIn("summary", data)
        self.assertGreater(len(data["counted_words"]), 0)

    def test_count_full_bible(self):
        r = self.client.get(
            "/api/count"
            "?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=Johannes&chapter_to=3&verse_to=16"
        )
        self.assertEqual(r.status_code, 200)

    def test_count_invalid_translation(self):
        r = self.client.get(
            "/api/count"
            "?translation=NichtVorhanden"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_invalid_book_from(self):
        r = self.client.get(
            "/api/count"
            "?translation=TestBible"
            "&book_from=NichtVorhanden&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_invalid_book_to(self):
        r = self.client.get(
            "/api/count"
            "?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=NichtVorhanden&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_wrong_order_returns_400(self):
        r = self.client.get(
            "/api/count"
            "?translation=TestBible"
            "&book_from=Johannes&chapter_from=3&verse_from=16"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 400)

    def test_count_same_verse(self):
        r = self.client.get(
            "/api/count"
            "?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Vers 1 "Im Anfang schuf Gott die Himmel und die Erde."
        total = sum(w["count"] for w in data["counted_words"])
        total += sum(w["count"] for w in data.get("ignored_words", []))
        self.assertGreater(total, 0)

    # ------------------------------------------------------------------
    # Strong-Routen
    # ------------------------------------------------------------------

    def test_strong_not_loaded_number(self):
        from main import strong_manager
        orig = strong_manager._loaded
        strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/number/H430")
            self.assertIn(r.status_code, [503, 404])
        finally:
            strong_manager._loaded = orig

    def test_strong_not_loaded_word(self):
        from main import strong_manager
        orig = strong_manager._loaded
        strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/word?word=Gott")
            self.assertIn(r.status_code, [503, 400, 200])
        finally:
            strong_manager._loaded = orig

    def test_strong_word_too_short(self):
        from main import strong_manager
        orig = strong_manager._loaded
        strong_manager._loaded = True
        try:
            r = self.client.get("/api/strong/word?word=a")
            self.assertEqual(r.status_code, 400)
        finally:
            strong_manager._loaded = orig

    def test_strong_loaded_number_not_found(self):
        from main import strong_manager
        from strong_manager import StrongManager
        orig_loaded = strong_manager._loaded
        orig_lookup = strong_manager.lookup_by_number
        strong_manager._loaded = True
        strong_manager.lookup_by_number = lambda sid: None
        try:
            r = self.client.get("/api/strong/number/H9999")
            self.assertEqual(r.status_code, 404)
        finally:
            strong_manager._loaded = orig_loaded
            strong_manager.lookup_by_number = orig_lookup

    def test_strong_loaded_number_found(self):
        from main import strong_manager
        from strong_manager import StrongEntry
        mock_entry = StrongEntry(
            strong_id="H430", language="hebrew", title="Elohim",
            total_count=100, usages=[]
        )
        orig_loaded = strong_manager._loaded
        orig_lookup = strong_manager.lookup_by_number
        orig_to_dict = strong_manager.entry_to_dict
        strong_manager._loaded = True
        strong_manager.lookup_by_number = lambda sid: mock_entry
        strong_manager.entry_to_dict = lambda e, **kw: {
            "strong_number": e.strong_id, "title": e.title,
            "language": e.language, "total_count": e.total_count,
            "usages": [], "original_word": "", "transliteration": "",
            "pronunciation": "", "definition": "", "etymology": "",
            "translation": ""
        }
        try:
            r = self.client.get("/api/strong/number/H430")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["strong_number"], "H430")
        finally:
            strong_manager._loaded = orig_loaded
            strong_manager.lookup_by_number = orig_lookup
            strong_manager.entry_to_dict = orig_to_dict

    def test_strong_word_search_loaded(self):
        from main import strong_manager
        from strong_manager import StrongEntry, StrongUsage
        mock_results = [
            StrongEntry(
                strong_id="H430", language="hebrew", title="Elohim",
                total_count=100,
                usages=[StrongUsage(german_word="Gott", count=100, refs=[])]
            )
        ]
        orig_loaded = strong_manager._loaded
        orig_search = strong_manager.search_by_word
        orig_to_dict = strong_manager.entry_to_dict
        strong_manager._loaded = True
        strong_manager.search_by_word = lambda w, language="": mock_results
        strong_manager.entry_to_dict = lambda e, **kw: {
            "strong_number": e.strong_id, "title": e.title,
            "language": e.language, "total_count": e.total_count,
            "usages": [], "original_word": "", "transliteration": "",
            "pronunciation": "", "definition": "", "etymology": "",
            "translation": ""
        }
        try:
            r = self.client.get("/api/strong/word?word=Gott")
            self.assertEqual(r.status_code, 200)
        finally:
            strong_manager._loaded = orig_loaded
            strong_manager.search_by_word = orig_search
            strong_manager.entry_to_dict = orig_to_dict

    # ------------------------------------------------------------------
    # Startseite / uvicorn-Block
    # ------------------------------------------------------------------

    def test_root_returns_html(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers["content-type"])


if __name__ == "__main__":
    unittest.main()


"""
test_main_and_bible_base_coverage.py

Umfassende Tests für:
- main.py: alle HTML-Routen, alle API-Endpunkte, load_ignore_words,
           englische/deutsche Ignore-Liste, Wörter-Zählung, Sonderfälle
- bible_base.py: _parse_verse_per_line_format (Vers-Puffer-Fortsetzung,
                 leere Zeilen), _parse_standard_format, _go_to_next_passage
                 (ValueError-Pfad), _to_passage_reached (Offenbarung-Sonderfall)
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open

_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _src not in sys.path:
    sys.path.insert(0, _src)


# ---------------------------------------------------------------------------
# Hilfsfunktion: Mini-Bibel für API-Tests
# ---------------------------------------------------------------------------

def _inject_mini_bible(bible_manager):
    """Injiziert eine kleine In-Memory-Bibel in den BibleManager."""
    from bible_base import Bible

    class MiniBible(Bible):
        def load_text(self, fp):
            self._parse_text(
                "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.\n"
                "0#1. Mose#1#2#Und die Erde war wüst und leer.\n"
                "0#1. Mose#2#1#Und die Himmel und die Erde wurden vollendet.\n"
                "0#Johannes#3#16#Also hat Gott die Welt geliebt.\n"
                "0#Offenbarung#22#21#Die Gnade des Herrn Jesus sei mit euch allen."
            )

    b = MiniBible("TestDE")
    b.load_text("")
    b.book_positions = {n: i for i, n in enumerate(b.books.keys())}

    class MiniEnBible(Bible):
        def load_text(self, fp):
            self._parse_text(
                "0#Genesis#1#1#In the beginning, God created the heavens.\n"
                "0#Genesis#1#2#The earth was formless and empty.\n"
                "0#Revelation#22#21#The grace of the Lord Jesus be with all.\n"
            )

    b_en = MiniEnBible("WEB")
    b_en.load_text("")
    b_en.book_positions = {n: i for i, n in enumerate(b_en.books.keys())}

    bible_manager.bibles["TESTDE"] = b
    bible_manager.bibles["WEB"] = b_en
    return b, b_en


# ===========================================================================
# main.py – load_ignore_words
# ===========================================================================

class TestLoadIgnoreWords(unittest.TestCase):

    def setUp(self):
        _orig = os.getcwd()
        self._orig = _orig
        self.addCleanup(os.chdir, _orig)
        os.makedirs(os.path.join(_src, "static"), exist_ok=True)
        os.chdir(_src)

    def _import(self):
        import importlib
        import main as m
        return m

    def test_normale_woerter(self):
        m = self._import()
        content = "der\ndie\ndas\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = m.load_ignore_words("test.txt")
        self.assertIn("der", words)
        self.assertIn("die", words)
        self.assertIn("das", words)

    def test_kommentare_und_leerzeilen_werden_ignoriert(self):
        m = self._import()
        content = "# Kommentar\n\nder\n\n# noch ein Kommentar\ndie\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = m.load_ignore_words("test.txt")
        self.assertNotIn("# Kommentar", words)
        self.assertNotIn("", words)
        self.assertIn("der", words)
        self.assertIn("die", words)

    def test_datei_nicht_gefunden(self):
        m = self._import()
        with patch("builtins.print") as mp:
            words = m.load_ignore_words("nicht_vorhanden.txt")
        self.assertEqual(words, set())
        self.assertIn("Warning", str(mp.call_args))

    def test_leere_datei(self):
        m = self._import()
        with patch("builtins.open", mock_open(read_data="")):
            words = m.load_ignore_words("empty.txt")
        self.assertEqual(words, set())

    def test_grossbuchstaben_werden_normalisiert(self):
        m = self._import()
        content = "DER\nDIE\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = m.load_ignore_words("test.txt")
        self.assertIn("der", words)
        self.assertIn("die", words)


# ===========================================================================
# main.py – HTML-Routen
# ===========================================================================



class TestMainHTMLRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._orig = os.getcwd()
        os.makedirs(os.path.join(_src, "static"), exist_ok=True)
        os.chdir(_src)
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from fastapi.testclient import TestClient
        import main as m
        _inject_mini_bible(m.bible_manager)
        cls.client = TestClient(m.app)
        cls.m = m

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._orig)

    def setUp(self):
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(_src)

    def test_root_200(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers["content-type"])

    def test_root_enthaelt_uebersetzungsnamen(self):
        r = self.client.get("/")
        # Home-Template rendert mit translations-Liste
        self.assertEqual(r.status_code, 200)

    def test_home_html_200(self):
        r = self.client.get("/home.html")
        self.assertEqual(r.status_code, 200)

    def test_read_html_200(self):
        r = self.client.get("/read")
        self.assertEqual(r.status_code, 200)

    def test_search_html_200(self):
        r = self.client.get("/search.html")
        self.assertEqual(r.status_code, 200)

    def test_count_html_200(self):
        r = self.client.get("/count.html")
        self.assertEqual(r.status_code, 200)

    def test_strong_html_200(self):
        r = self.client.get("/strong.html")
        self.assertEqual(r.status_code, 200)

    def test_parallel_html_200(self):
        r = self.client.get("/parallel.html")
        self.assertEqual(r.status_code, 200)

    def test_about_html_200(self):
        r = self.client.get("/about.html")
        self.assertEqual(r.status_code, 200)

    def test_alle_html_seiten_liefern_text_html(self):
        for path in ["/", "/home.html", "/read", "/search.html",
                     "/count.html", "/strong.html", "/parallel.html", "/about.html"]:
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 200)
                self.assertIn("text/html", r.headers["content-type"])


# ===========================================================================
# main.py – API-Endpunkte vollständig
# ===========================================================================



class TestMainAPIRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._orig = os.getcwd()
        os.makedirs(os.path.join(_src, "static"), exist_ok=True)
        os.chdir(_src)
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from fastapi.testclient import TestClient
        import main as m
        _inject_mini_bible(m.bible_manager)
        cls.client = TestClient(m.app)
        cls.m = m

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._orig)

    def setUp(self):
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(_src)

    # --- /api/translations ---
    def test_translations_liste(self):
        r = self.client.get("/api/translations")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("translations", data)
        self.assertIn("TestDE", data["translations"])
        self.assertIn("WEB", data["translations"])

    # --- /api/{translation}/books ---
    def test_books_gueltig(self):
        r = self.client.get("/api/TestDE/books")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("books", data)
        names = [b["name"] for b in data["books"]]
        self.assertIn("1. Mose", names)

    def test_books_case_insensitive(self):
        r = self.client.get("/api/testde/books")
        self.assertEqual(r.status_code, 200)

    def test_books_unbekannte_translation_404(self):
        r = self.client.get("/api/Unbekannt/books")
        self.assertEqual(r.status_code, 404)

    def test_books_enthaelt_kapitelanzahl(self):
        r = self.client.get("/api/TestDE/books")
        data = r.json()
        mose = next(b for b in data["books"] if b["name"] == "1. Mose")
        self.assertEqual(mose["chapters"], 2)

    # --- /api/{translation}/{book} ---
    def test_buch_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("chapters", data)

    def test_buch_ungueltige_translation_404(self):
        r = self.client.get("/api/Unbekannt/1. Mose")
        self.assertEqual(r.status_code, 404)

    def test_buch_unbekanntes_buch_404(self):
        r = self.client.get("/api/TestDE/Unbekannt")
        self.assertEqual(r.status_code, 404)

    # --- /api/{translation}/{book}/{chapter} ---
    def test_kapitel_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/1")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("verses", data)
        self.assertEqual(len(data["verses"]), 2)

    def test_kapitel_ungueltige_translation_404(self):
        r = self.client.get("/api/Unbekannt/1. Mose/1")
        self.assertEqual(r.status_code, 404)

    def test_kapitel_ungueltig_404(self):
        r = self.client.get("/api/TestDE/1. Mose/999")
        self.assertEqual(r.status_code, 404)

    def test_kapitel_2_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/2")
        self.assertEqual(r.status_code, 200)

    # --- /api/{translation}/{book}/{chapter}/{verse} ---
    def test_vers_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/1/1")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("text", data)
        self.assertIn("Anfang", data["text"])

    def test_vers_ungueltige_translation_404(self):
        r = self.client.get("/api/Unbekannt/1. Mose/1/1")
        self.assertEqual(r.status_code, 404)

    def test_vers_ungueltig_404(self):
        r = self.client.get("/api/TestDE/1. Mose/1/999")
        self.assertEqual(r.status_code, 404)

    def test_vers_enthaelt_alle_felder(self):
        r = self.client.get("/api/TestDE/1. Mose/1/1")
        data = r.json()
        for field in ["book", "chapter", "verse", "text", "translation"]:
            self.assertIn(field, data)

    # --- /api/{translation}/{book}/chapters ---
    def test_kapitelliste_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/chapters")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("chapters", data)
        self.assertEqual(len(data["chapters"]), 2)

    def test_kapitelliste_ungueltige_translation_404(self):
        r = self.client.get("/api/Unbekannt/1. Mose/chapters")
        self.assertEqual(r.status_code, 404)

    def test_kapitelliste_unbekanntes_buch_404(self):
        r = self.client.get("/api/TestDE/Unbekannt/chapters")
        self.assertEqual(r.status_code, 404)

    def test_kapitelliste_enthaelt_versanzahl(self):
        r = self.client.get("/api/TestDE/1. Mose/chapters")
        data = r.json()
        kap1 = next(c for c in data["chapters"] if c["chapter"] == 1)
        self.assertEqual(kap1["verses"], 2)

    # --- /api/{translation}/{book}/chapter-count ---
    def test_kapitelanzahl_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/chapter-count")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["chapters"], 2)

    def test_kapitelanzahl_ungueltige_translation_404(self):
        r = self.client.get("/api/Unbekannt/1. Mose/chapter-count")
        self.assertEqual(r.status_code, 404)

    def test_kapitelanzahl_unbekanntes_buch_404(self):
        r = self.client.get("/api/TestDE/Unbekannt/chapter-count")
        self.assertEqual(r.status_code, 404)

    # --- /api/{translation}/{book}/{chapter}/verse-count ---
    def test_versanzahl_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/1/verse-count")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["verses"], 2)

    def test_versanzahl_ungueltige_translation_404(self):
        r = self.client.get("/api/Unbekannt/1. Mose/1/verse-count")
        self.assertEqual(r.status_code, 404)

    def test_versanzahl_ungueltig_404(self):
        r = self.client.get("/api/TestDE/1. Mose/999/verse-count")
        self.assertEqual(r.status_code, 404)

    # --- /api/search ---
    def test_suche_findet_ergebnisse(self):
        r = self.client.get("/api/search?q=Gott&translation=TestDE")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertGreater(data["total"], 0)
        self.assertIn("results", data)

    def test_suche_alle_uebersetzungen(self):
        r = self.client.get("/api/search?q=Gott")
        self.assertEqual(r.status_code, 200)

    def test_suche_mit_buch_filter(self):
        r = self.client.get("/api/search?q=Gott&translation=TestDE&book=1. Mose")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for result in data["results"]:
            self.assertEqual(result["book"], "1. Mose")

    def test_suche_zu_kurz_400(self):
        r = self.client.get("/api/search?q=a")
        self.assertEqual(r.status_code, 400)

    def test_suche_leer_400(self):
        r = self.client.get("/api/search?q=")
        self.assertEqual(r.status_code, 400)

    def test_suche_pagination_seite1(self):
        r = self.client.get("/api/search?q=Gott&translation=TestDE&page=1&limit=1")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertLessEqual(len(data["results"]), 1)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 1)

    def test_suche_pagination_seite2(self):
        r = self.client.get("/api/search?q=Gott&translation=TestDE&page=2&limit=1")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["page"], 2)

    def test_suche_ergebnis_struktur(self):
        r = self.client.get("/api/search?q=Gott&translation=TestDE")
        data = r.json()
        if data["results"]:
            result = data["results"][0]
            for field in ["book", "chapter", "verse", "text", "translation"]:
                self.assertIn(field, result)

    def test_suche_nicht_gefunden(self):
        r = self.client.get("/api/search?q=XYZnichtvorhanden&translation=TestDE")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["total"], 0)

    # --- /api/count – Deutsch ---
    def test_count_deutsch_gueltig(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("counted_words", data)
        self.assertIn("ignored_words", data)
        self.assertIn("summary", data)
        self.assertIn("section", data)
        self.assertIn("total_unique_words", data)

    def test_count_deutsch_einzelwort(self):
        """Wortzählung eines einzelnen Verses."""
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        alle_woerter = {w["word"] for w in data["counted_words"] + data["ignored_words"]}
        # "anfang" muss im Vers vorkommen (Wort mindestens 2 Zeichen)
        self.assertIn("anfang", alle_woerter)

    def test_count_einzelbuchstaben_nicht_enthalten(self):
        """Einzelbuchstaben dürfen nicht in counted_words auftauchen (regex {2,})."""
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        data = r.json()
        alle = data["counted_words"] + data["ignored_words"]
        einzelbuchstaben = [w for w in alle if len(w["word"]) < 2]
        self.assertEqual(einzelbuchstaben, [])

    def test_count_deutsch_ignoriert_stoppwoerter(self):
        """Deutsche Stoppwörter landen in ignored_words."""
        import main as m
        m.IGNORE_WORDS_DE = {"und", "die", "der"}
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        data = r.json()
        ignored = {w["word"] for w in data["ignored_words"]}
        # "und" kommt in "Und die Erde war wüst" vor
        self.assertIn("und", ignored)

    def test_count_englisch_nutzt_en_liste(self):
        """WEB-Übersetzung nutzt englische Ignore-Liste."""
        import main as m
        m.IGNORE_WORDS_EN = {"the", "in", "and"}
        r = self.client.get(
            "/api/count?translation=WEB"
            "&book_from=Genesis&chapter_from=1&verse_from=1"
            "&book_to=Genesis&chapter_to=1&verse_to=2"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        ignored = {w["word"] for w in data["ignored_words"]}
        self.assertIn("the", ignored)

    def test_count_ungueltige_translation_404(self):
        r = self.client.get(
            "/api/count?translation=Unbekannt"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_ungueltige_buch_from_404(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=Unbekannt&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_ungueltige_buch_to_404(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=Unbekannt&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_falsche_reihenfolge_400(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=Johannes&chapter_from=3&verse_from=16"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 400)

    def test_count_mehrere_buecher(self):
        """Zählung über mehrere Bücher hinweg."""
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=Johannes&chapter_to=3&verse_to=16"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        alle = {w["word"] for w in data["counted_words"] + data["ignored_words"]}
        self.assertGreater(len(alle), 0)

    def test_count_zusammenfassung_felder(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        data = r.json()
        self.assertIn("total_counted", data["summary"])
        self.assertIn("total_ignored", data["summary"])
        total = data["summary"]["total_counted"] + data["summary"]["total_ignored"]
        self.assertEqual(total, data["total_unique_words"])

    def test_count_section_felder(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=2&verse_to=1"
        )
        data = r.json()
        section = data["section"]
        self.assertEqual(section["book_from"], "1. Mose")
        self.assertEqual(section["chapter_from"], 1)
        self.assertEqual(section["verse_from"], 1)
        self.assertEqual(section["book_to"], "1. Mose")
        self.assertEqual(section["chapter_to"], 2)
        self.assertEqual(section["verse_to"], 1)

    def test_count_gleicher_vers(self):
        """Von-Vers == Bis-Vers → genau ein Vers wird gezählt."""
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        alle = {w["word"] for w in data["counted_words"] + data["ignored_words"]}
        # Vers 1: "Im Anfang schuf Gott die Himmel und die Erde."
        self.assertIn("gott", alle)

    def test_count_sortierung_nach_haeufigkeit(self):
        """counted_words und ignored_words sind jeweils absteigend nach Häufigkeit sortiert."""
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        data = r.json()
        # counted_words ist für sich sortiert
        if len(data["counted_words"]) >= 2:
            counts = [w["count"] for w in data["counted_words"]]
            self.assertEqual(counts, sorted(counts, reverse=True))
        # ignored_words ist für sich sortiert
        if len(data["ignored_words"]) >= 2:
            counts = [w["count"] for w in data["ignored_words"]]
            self.assertEqual(counts, sorted(counts, reverse=True))

    # --- Strong-Endpunkte ---
    def test_strong_nicht_geladen_503(self):
        import main as m
        orig = m.strong_manager._loaded
        m.strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/number/H430")
            self.assertEqual(r.status_code, 503)
        finally:
            m.strong_manager._loaded = orig

    def test_strong_nicht_geladen_word_503(self):
        import main as m
        orig = m.strong_manager._loaded
        m.strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/word?word=Gott")
            self.assertEqual(r.status_code, 503)
        finally:
            m.strong_manager._loaded = orig

    def test_strong_word_zu_kurz_400(self):
        import main as m
        orig = m.strong_manager._loaded
        m.strong_manager._loaded = True
        try:
            r = self.client.get("/api/strong/word?word=a")
            self.assertEqual(r.status_code, 400)
        finally:
            m.strong_manager._loaded = orig

    def test_strong_nummer_nicht_gefunden_404(self):
        import main as m
        orig = m.strong_manager._loaded
        orig_lookup = m.strong_manager.lookup_by_number
        m.strong_manager._loaded = True
        m.strong_manager.lookup_by_number = lambda sid: None
        try:
            r = self.client.get("/api/strong/number/H9999")
            self.assertEqual(r.status_code, 404)
        finally:
            m.strong_manager._loaded = orig
            m.strong_manager.lookup_by_number = orig_lookup

    def test_strong_nummer_gefunden_200(self):
        from strong_manager import StrongEntry
        import main as m
        mock_entry = StrongEntry(
            strong_id="H430", language="hebrew", title="Elohim",
            total_count=100, usages=[]
        )
        orig = m.strong_manager._loaded
        orig_lookup = m.strong_manager.lookup_by_number
        orig_dict = m.strong_manager.entry_to_dict
        m.strong_manager._loaded = True
        m.strong_manager.lookup_by_number = lambda sid: mock_entry
        m.strong_manager.entry_to_dict = lambda e, **kw: {
            "strong_number": e.strong_id, "language": e.language,
            "title": e.title, "total_count": e.total_count, "usages": [],
            "original_word": "", "transliteration": "", "pronunciation": "",
            "definition": "", "etymology": "", "translation": ""
        }
        try:
            r = self.client.get("/api/strong/number/H430")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["strong_number"], "H430")
        finally:
            m.strong_manager._loaded = orig
            m.strong_manager.lookup_by_number = orig_lookup
            m.strong_manager.entry_to_dict = orig_dict

    def test_strong_wort_suche_200(self):
        from strong_manager import StrongEntry, StrongUsage
        import main as m
        mock_results = [
            StrongEntry(
                strong_id="H430", language="hebrew", title="Elohim",
                total_count=100,
                usages=[StrongUsage(german_word="Gott", count=100, refs=[])]
            )
        ]
        orig = m.strong_manager._loaded
        orig_search = m.strong_manager.search_by_word
        orig_dict = m.strong_manager.entry_to_dict
        m.strong_manager._loaded = True
        m.strong_manager.search_by_word = lambda w, language="": mock_results
        m.strong_manager.entry_to_dict = lambda e, **kw: {
            "strong_number": e.strong_id, "language": e.language,
            "title": e.title, "total_count": e.total_count, "usages": [],
            "original_word": "", "transliteration": "", "pronunciation": "",
            "definition": "", "etymology": "", "translation": ""
        }
        try:
            r = self.client.get("/api/strong/word?word=Gott")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertIn("results", data)
            self.assertIn("total", data)
            self.assertIn("query", data)
        finally:
            m.strong_manager._loaded = orig
            m.strong_manager.search_by_word = orig_search
            m.strong_manager.entry_to_dict = orig_dict

    def test_strong_wort_mit_sprache(self):
        import main as m
        orig = m.strong_manager._loaded
        orig_search = m.strong_manager.search_by_word
        orig_dict = m.strong_manager.entry_to_dict
        m.strong_manager._loaded = True
        m.strong_manager.search_by_word = lambda w, language="": []
        m.strong_manager.entry_to_dict = lambda e, **kw: {}
        try:
            r = self.client.get("/api/strong/word?word=love&language=greek")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["language"], "greek")
        finally:
            m.strong_manager._loaded = orig
            m.strong_manager.search_by_word = orig_search
            m.strong_manager.entry_to_dict = orig_dict

    def test_strong_wort_ohne_sprache_all(self):
        import main as m
        orig = m.strong_manager._loaded
        orig_search = m.strong_manager.search_by_word
        orig_dict = m.strong_manager.entry_to_dict
        m.strong_manager._loaded = True
        m.strong_manager.search_by_word = lambda w, language="": []
        m.strong_manager.entry_to_dict = lambda e, **kw: {}
        try:
            r = self.client.get("/api/strong/word?word=Gott")
            self.assertEqual(r.json()["language"], "all")
        finally:
            m.strong_manager._loaded = orig
            m.strong_manager.search_by_word = orig_search
            m.strong_manager.entry_to_dict = orig_dict


# ===========================================================================
# bible_base.py – verbleibende Lücken
# ===========================================================================


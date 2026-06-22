import unittest
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
import pytest
import sys
import os

# ---------------------------------------------------------------------------
# sys.path: src/ einmalig eintragen, kein os.chdir mehr nötig.
# Die App-Instanz wird mit TestClient(app) erstellt; Templates und static
# werden von FastAPI relativ zum CWD gesucht – deshalb wechseln wir in
# setUpClass einmalig in src/ und bleiben dort für die gesamte Testsession.
# ---------------------------------------------------------------------------
_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

os.makedirs(os.path.join(_src_dir, 'static'), exist_ok=True)
os.chdir(_src_dir)

from main import app, get_bible_manager, get_strong_manager, get_ignore_words_de, get_ignore_words_en, get_ignore_words_fr


# ---------------------------------------------------------------------------
# Hilfsfunktion: Dependency Override zurücksetzen
# ---------------------------------------------------------------------------
def _clear_overrides():
    app.dependency_overrides.clear()


class TestMainAPI(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.addCleanup(_clear_overrides)

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

    def _override_bible_manager(self, mock_bm):
        app.dependency_overrides[get_bible_manager] = lambda: mock_bm

    def _override_strong_manager(self, mock_sm):
        app.dependency_overrides[get_strong_manager] = lambda: mock_sm

    def test_root_endpoint(self):
        """Test the root HTML endpoint"""
        mock_bm = MagicMock()
        mock_bm.get_translation_names.return_value = ["Elberfelder 1905"]
        self._override_bible_manager(mock_bm)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))

    def test_list_translations_endpoint(self):
        """Test the list translations endpoint"""
        mock_bm = MagicMock()
        mock_bm.get_translation_names.return_value = ["Elberfelder 1905", "WorldEnglishBible"]
        self._override_bible_manager(mock_bm)
        response = self.client.get("/api/translations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("translations", data)
        self.assertEqual(data["translations"], ["Elberfelder 1905", "WorldEnglishBible"])

    def test_list_translations_empty(self):
        """Test list translations when no translations available"""
        mock_bm = MagicMock()
        mock_bm.get_translation_names.return_value = []
        self._override_bible_manager(mock_bm)
        response = self.client.get("/api/translations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["translations"], [])

    def test_get_books_valid_translation(self):
        """Test get books for valid translation"""
        mock_bible = MagicMock()
        mock_bible.get_book_names.return_value = ["1. Mose", "2. Mose"]
        mock_bible.get_chapter_count.side_effect = lambda book: 50 if book == "1. Mose" else 40
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/books")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["translation"], "Elberfelder 1905")
        self.assertEqual(len(data["books"]), 2)
        book1 = next(book for book in data["books"] if book["name"] == "1. Mose")
        self.assertEqual(book1["chapters"], 50)

    def test_get_books_invalid_translation(self):
        """Test get books for invalid translation"""
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/NonExistentTranslation/books")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Translation 'NonExistentTranslation' not found", data["detail"])

    def test_get_book_valid(self):
        """Test get book with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.get_book.return_value = self.mock_bible_data["1. Mose"]
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["book"], "1. Mose")
        self.assertEqual(data["translation"], "Elberfelder 1905")
        self.assertIn("chapters", data)
        self.assertEqual(len(data["chapters"]), 2)

    def test_get_book_invalid_translation(self):
        """Test get book with invalid translation"""
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/NonExistent/1. Mose")
        self.assertEqual(response.status_code, 404)

    def test_get_book_invalid_book(self):
        """Test get book with invalid book name"""
        mock_bible = MagicMock()
        mock_bible.get_book.return_value = None
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/NonExistentBook")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Book 'NonExistentBook' not found", data["detail"])

    def test_get_chapter_valid(self):
        """Test get chapter with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.get_chapter.return_value = self.mock_bible_data["1. Mose"][1]
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["book"], "1. Mose")
        self.assertEqual(data["chapter"], 1)
        self.assertEqual(data["translation"], "Elberfelder 1905")
        self.assertIn("verses", data)
        self.assertEqual(len(data["verses"]), 3)

    def test_get_chapter_invalid_translation(self):
        """Test get chapter with invalid translation"""
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/NonExistent/1. Mose/1")
        self.assertEqual(response.status_code, 404)

    def test_get_chapter_invalid_chapter(self):
        """Test get chapter with invalid chapter number"""
        mock_bible = MagicMock()
        mock_bible.get_chapter.return_value = None
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Chapter 999 not found", data["detail"])

    def test_get_verse_valid(self):
        """Test get verse with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Im Anfang schuf Gott die Himmel und die Erde."
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

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
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/NonExistent/1. Mose/1/1")
        self.assertEqual(response.status_code, 404)

    def test_get_verse_invalid_verse(self):
        """Test get verse with invalid verse number"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = None
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1/999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Verse 999 not found", data["detail"])

    def test_get_chapter_list_valid(self):
        """Test get chapter list with valid parameters"""
        mock_bible = MagicMock()
        mock_bible.books = {"1. Mose": {1: {}, 2: {}}}
        mock_bible.get_verse_count.side_effect = lambda book, chapter: 31 if chapter == 1 else 25
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/chapters")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["translation"], "Elberfelder 1905")
        self.assertEqual(data["book"], "1. Mose")
        self.assertEqual(len(data["chapters"]), 2)
        chapter1 = next(ch for ch in data["chapters"] if ch["chapter"] == 1)
        self.assertEqual(chapter1["verses"], 31)

    def test_get_chapter_list_invalid_translation(self):
        """Test get chapter list with invalid translation"""
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/NonExistent/1. Mose/chapters")
        self.assertEqual(response.status_code, 404)

    def test_get_chapter_list_invalid_book(self):
        """Test get chapter list with invalid book"""
        mock_bible = MagicMock()
        mock_bible.books = {}
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/NonExistentBook/chapters")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Book 'NonExistentBook' not found", data["detail"])

    def test_api_endpoints_with_special_characters(self):
        """Test API endpoints with special characters in book names"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse with special characters"
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1.%20Mose/1/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["book"], "1. Mose")

    def test_api_endpoints_with_edge_case_numbers(self):
        """Test API endpoints with edge case numbers"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/0/1")
        self.assertEqual(response.status_code, 200)
        mock_bible.get_verse.assert_called_with("1. Mose", 0, 1)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1/0")
        self.assertEqual(response.status_code, 200)
        mock_bible.get_verse.assert_called_with("1. Mose", 1, 0)

    def test_api_endpoints_parameter_types(self):
        """Test that API endpoints properly handle parameter types"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
        self.assertEqual(response.status_code, 200)
        mock_bible.get_verse.assert_called_with("1. Mose", 1, 1)

    def test_error_response_format(self):
        """Test that error responses have proper format"""
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        self._override_bible_manager(mock_bm)

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
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        results = []

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
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for field in ["book", "chapter", "verse", "text", "translation"]:
            self.assertIn(field, data)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for field in ["book", "chapter", "verses", "translation"]:
            self.assertIn(field, data)

        response = self.client.get("/api/Elberfelder 1905/1. Mose")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for field in ["book", "chapters", "translation"]:
            self.assertIn(field, data)

    def test_api_documentation_endpoints(self):
        """Test that API documentation endpoints are accessible"""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("openapi", data)
        self.assertIn("info", data)
        self.assertIn("paths", data)

    def test_static_files_mount(self):
        """Test that static files are properly mounted"""
        response = self.client.get("/static/nonexistent.css")
        self.assertEqual(response.status_code, 404)

    def test_content_type_headers(self):
        """Test that responses have correct content-type headers"""
        mock_bible = MagicMock()
        mock_bible.get_verse.return_value = "Test verse"
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers.get("content-type", ""))

    def test_api_versioning_in_urls(self):
        """Test that API endpoints are properly versioned"""
        mock_bm = MagicMock()
        mock_bm.get_translation_names.return_value = ["Test"]
        self._override_bible_manager(mock_bm)

        response = self.client.get("/api/translations")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/translations")
        self.assertEqual(response.status_code, 404)


class TestMainIntegration(unittest.TestCase):
    """Integration tests for the main application"""

    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(_clear_overrides)

    def test_full_workflow_integration(self):
        """Test complete workflow from translations to verse"""
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

        mock_bm = MagicMock()
        mock_bm.get_translation_names.return_value = ["Elberfelder 1905"]
        mock_bm.get_bible.return_value = mock_bible
        app.dependency_overrides[get_bible_manager] = lambda: mock_bm

        response = self.client.get("/api/translations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Elberfelder 1905", response.json()["translations"])

        response = self.client.get("/api/Elberfelder 1905/books")
        self.assertEqual(response.status_code, 200)
        books = response.json()["books"]
        self.assertEqual(books[0]["name"], "1. Mose")

        response = self.client.get("/api/Elberfelder 1905/1. Mose/chapters")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["chapters"]), 2)

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["book"], "1. Mose")

        response = self.client.get("/api/Elberfelder 1905/1. Mose/1/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["text"],
            "Im Anfang schuf Gott die Himmel und die Erde."
        )


class TestMainLoadIgnoreWords(unittest.TestCase):

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
    """Integrationstests für FastAPI-Routen via TestClient."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.addCleanup(_clear_overrides)

    def test_home_html_route(self):
        r = self.client.get("/home.html")
        self.assertEqual(r.status_code, 200)

    def test_read_html_route(self):
        r = self.client.get("/read")
        self.assertEqual(r.status_code, 200)

    def test_read_html_dot_html_route(self):
        r = self.client.get("/read.html")
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
        mock_bible = MagicMock()
        mock_bible.get_book_names.return_value = ["1. Mose", "Johannes"]
        mock_bible.get_chapter_count.return_value = 50
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        app.dependency_overrides[get_bible_manager] = lambda: mock_bm

        r = self.client.get("/api/TestBible/books")
        self.assertEqual(r.status_code, 200)

    def test_api_books_invalid_translation(self):
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = None
        app.dependency_overrides[get_bible_manager] = lambda: mock_bm

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
        mock_bible = MagicMock()
        mock_bible.books = {"1. Mose": {1: {1: "Vers"}}, "2. Mose": {1: {1: "Vers"}}}
        mock_bm = MagicMock()
        mock_bm.get_bible.return_value = mock_bible
        app.dependency_overrides[get_bible_manager] = lambda: mock_bm

        r = self.client.get(
            "/api/count?translation=Test"
            "&book_from=2. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertIn(r.status_code, [400, 404, 422, 200])


# ---------------------------------------------------------------------------
# TestMainAPICoverage – gezielte Tests für verbleibende Coverage-Lücken
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


class TestMainAPICoverage(unittest.TestCase):
    """Tests für alle nicht abgedeckten main.py-Routen."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Mini-Bibel direkt in den App-eigenen BibleManager injizieren
        from main import _bible_manager
        mgr, bible = _make_bible_manager()
        _bible_manager.bibles["TESTBIBLE"] = bible

    def setUp(self):
        self.addCleanup(_clear_overrides)

    def test_get_books_valid(self):
        r = self.client.get("/api/TestBible/books")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("books", data)
        self.assertGreater(len(data["books"]), 0)

    def test_get_chapter_count_valid(self):
        r = self.client.get("/api/TestBible/1. Mose/chapter-count")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["chapters"], 2)

    def test_get_chapter_count_invalid_translation(self):
        r = self.client.get("/api/NichtVorhanden/1. Mose/chapter-count")
        self.assertEqual(r.status_code, 404)

    def test_get_chapter_count_invalid_book(self):
        r = self.client.get("/api/TestBible/NichtVorhanden/chapter-count")
        self.assertEqual(r.status_code, 404)

    def test_get_verse_count_valid(self):
        r = self.client.get("/api/TestBible/1. Mose/1/verse-count")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["verses"], 2)

    def test_get_verse_count_invalid_chapter(self):
        r = self.client.get("/api/TestBible/1. Mose/999/verse-count")
        self.assertEqual(r.status_code, 404)

    def test_search_valid(self):
        r = self.client.get("/api/search?q=Gott&translation=TestBible")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("results", data)
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
        self.assertEqual(r.json()["page"], 2)

    def test_search_too_short_returns_400(self):
        r = self.client.get("/api/search?q=a")
        self.assertEqual(r.status_code, 400)

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
            "/api/count?translation=NichtVorhanden"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_invalid_book_from(self):
        r = self.client.get(
            "/api/count?translation=TestBible"
            "&book_from=NichtVorhanden&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_invalid_book_to(self):
        r = self.client.get(
            "/api/count?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=NichtVorhanden&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_count_wrong_order_returns_400(self):
        r = self.client.get(
            "/api/count?translation=TestBible"
            "&book_from=Johannes&chapter_from=3&verse_from=16"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 400)

    def test_count_same_verse(self):
        r = self.client.get(
            "/api/count?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        total = sum(w["count"] for w in data["counted_words"])
        total += sum(w["count"] for w in data.get("ignored_words", []))
        self.assertGreater(total, 0)

    def test_strong_not_loaded_number(self):
        from main import _strong_manager
        orig = _strong_manager._loaded
        _strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/number/H430")
            self.assertIn(r.status_code, [503, 404])
        finally:
            _strong_manager._loaded = orig

    def test_strong_not_loaded_word(self):
        from main import _strong_manager
        orig = _strong_manager._loaded
        _strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/word?word=Gott")
            self.assertIn(r.status_code, [503, 400, 200])
        finally:
            _strong_manager._loaded = orig

    def test_strong_word_too_short(self):
        from main import _strong_manager
        orig = _strong_manager._loaded
        _strong_manager._loaded = True
        try:
            r = self.client.get("/api/strong/word?word=a")
            self.assertEqual(r.status_code, 400)
        finally:
            _strong_manager._loaded = orig

    def test_strong_loaded_number_not_found(self):
        from main import _strong_manager
        orig_loaded = _strong_manager._loaded
        orig_lookup = _strong_manager.lookup_by_number
        _strong_manager._loaded = True
        _strong_manager.lookup_by_number = lambda sid: None
        try:
            r = self.client.get("/api/strong/number/H9999")
            self.assertEqual(r.status_code, 404)
        finally:
            _strong_manager._loaded = orig_loaded
            _strong_manager.lookup_by_number = orig_lookup

    def test_strong_loaded_number_found(self):
        from main import _strong_manager
        from strong_manager import StrongEntry
        mock_entry = StrongEntry(
            strong_id="H430", language="hebrew", title="Elohim",
            total_count=100, usages=[]
        )
        orig_loaded = _strong_manager._loaded
        orig_lookup = _strong_manager.lookup_by_number
        orig_to_dict = _strong_manager.entry_to_dict
        _strong_manager._loaded = True
        _strong_manager.lookup_by_number = lambda sid: mock_entry
        _strong_manager.entry_to_dict = lambda e, **kw: {
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
            _strong_manager._loaded = orig_loaded
            _strong_manager.lookup_by_number = orig_lookup
            _strong_manager.entry_to_dict = orig_to_dict

    def test_strong_word_search_loaded(self):
        from main import _strong_manager
        from strong_manager import StrongEntry, StrongUsage
        mock_results = [
            StrongEntry(
                strong_id="H430", language="hebrew", title="Elohim",
                total_count=100,
                usages=[StrongUsage(german_word="Gott", count=100, refs=[])]
            )
        ]
        orig_loaded = _strong_manager._loaded
        orig_search = _strong_manager.search_by_word
        orig_to_dict = _strong_manager.entry_to_dict
        _strong_manager._loaded = True
        _strong_manager.search_by_word = lambda w, language="": mock_results
        _strong_manager.entry_to_dict = lambda e, **kw: {
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
            _strong_manager._loaded = orig_loaded
            _strong_manager.search_by_word = orig_search
            _strong_manager.entry_to_dict = orig_to_dict

    def test_root_returns_html(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers["content-type"])

    def test_count_ignore_words_de_via_dependency(self):
        """Stoppwörter werden über Dependency inject korrekt angewendet."""
        app.dependency_overrides[get_ignore_words_de] = lambda: {"und", "die", "der"}
        r = self.client.get(
            "/api/count?translation=TestBible"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        ignored = {w["word"] for w in data["ignored_words"]}
        self.assertIn("und", ignored)

    def test_count_ignore_words_en_via_dependency(self):
        """Englische Stoppwörter gelten für ENGLISH_TRANSLATIONS."""
        from bible_base import Bible
        from bible_manager import BibleManager
        from main import _bible_manager

        class MiniEnBible(Bible):
            def load_text(self, fp):
                self._parse_text(
                    "0#Genesis#1#1#In the beginning God created.\n"
                    "0#Genesis#1#2#The earth was formless and empty.\n"
                )

        b_en = MiniEnBible("WEB")
        b_en.load_text("")
        b_en.book_positions = {n: i for i, n in enumerate(b_en.books.keys())}
        _bible_manager.bibles["WEB"] = b_en

        app.dependency_overrides[get_ignore_words_en] = lambda: {"the", "in", "and"}
        r = self.client.get(
            "/api/count?translation=WEB"
            "&book_from=Genesis&chapter_from=1&verse_from=1"
            "&book_to=Genesis&chapter_to=1&verse_to=2"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        ignored = {w["word"] for w in data["ignored_words"]}
        self.assertIn("the", ignored)

    def test_count_ignore_words_fr_via_dependency(self):
        """Französische Stoppwörter gelten für FRENCH_TRANSLATIONS."""
        from bible_base import Bible
        from main import _bible_manager, FRENCH_TRANSLATIONS

        class MiniFrBible(Bible):
            def load_text(self, fp):
                self._parse_text(
                    "0#Genèse#1#1#Au commencement Dieu créa les cieux et la terre.\n"
                    "0#Genèse#1#2#La terre était informe et vide.\n"
                )

        b_fr = MiniFrBible("Segond 1910")
        b_fr.load_text("")
        b_fr.book_positions = {n: i for i, n in enumerate(b_fr.books.keys())}
        _bible_manager.bibles["SEGOND 1910"] = b_fr

        app.dependency_overrides[get_ignore_words_fr] = lambda: {"et", "la", "au", "les"}
        r = self.client.get(
            "/api/count?translation=Segond 1910"
            "&book_from=Genèse&chapter_from=1&verse_from=1"
            "&book_to=Genèse&chapter_to=1&verse_to=2"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        ignored = {w["word"] for w in data["ignored_words"]}
        self.assertIn("et", ignored)
        self.assertIn("la", ignored)


# ---------------------------------------------------------------------------
# TestMainHTMLRoutes / TestMainAPIRoutes / TestLoadIgnoreWords
# (zusammengefasste Tests aus dem alten test_main_and_bible_base_coverage-Block)
# ---------------------------------------------------------------------------

def _inject_mini_bible(bm):
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

    class MiniEnBible(Bible):
        def load_text(self, fp):
            self._parse_text(
                "0#Genesis#1#1#In the beginning, God created the heavens.\n"
                "0#Genesis#1#2#The earth was formless and empty.\n"
                "0#Revelation#22#21#The grace of the Lord Jesus be with all.\n"
            )

    b = MiniBible("TestDE")
    b.load_text("")
    b.book_positions = {n: i for i, n in enumerate(b.books.keys())}

    b_en = MiniEnBible("WEB")
    b_en.load_text("")
    b_en.book_positions = {n: i for i, n in enumerate(b_en.books.keys())}

    bm.bibles["TESTDE"] = b
    bm.bibles["WEB"] = b_en
    return b, b_en


class TestLoadIgnoreWordsExtended(unittest.TestCase):

    def test_normale_woerter(self):
        from main import load_ignore_words
        content = "der\ndie\ndas\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = load_ignore_words("test.txt")
        self.assertIn("der", words)
        self.assertIn("die", words)
        self.assertIn("das", words)

    def test_kommentare_und_leerzeilen_werden_ignoriert(self):
        from main import load_ignore_words
        content = "# Kommentar\n\nder\n\n# noch ein Kommentar\ndie\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = load_ignore_words("test.txt")
        self.assertNotIn("# Kommentar", words)
        self.assertNotIn("", words)
        self.assertIn("der", words)

    def test_datei_nicht_gefunden(self):
        from main import load_ignore_words
        words = load_ignore_words("nicht_vorhanden.txt")
        self.assertEqual(words, set())

    def test_grossbuchstaben_werden_normalisiert(self):
        from main import load_ignore_words
        content = "DER\nDIE\n"
        with patch("builtins.open", mock_open(read_data=content)):
            words = load_ignore_words("test.txt")
        self.assertIn("der", words)
        self.assertIn("die", words)


class TestMainHTMLRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from main import _bible_manager
        _inject_mini_bible(_bible_manager)
        cls.client = TestClient(app)

    def setUp(self):
        self.addCleanup(_clear_overrides)

    def test_alle_html_seiten_200(self):
        for path in ["/", "/home.html", "/read", "/read.html", "/search.html",
                     "/count.html", "/strong.html", "/parallel.html", "/about.html"]:
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 200)
                self.assertIn("text/html", r.headers["content-type"])


class TestMainAPIRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from main import _bible_manager
        _inject_mini_bible(_bible_manager)
        cls.client = TestClient(app)

    def setUp(self):
        self.addCleanup(_clear_overrides)

    def test_translations_liste(self):
        r = self.client.get("/api/translations")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("TestDE", data["translations"])

    def test_books_gueltig(self):
        r = self.client.get("/api/TestDE/books")
        self.assertEqual(r.status_code, 200)
        names = [b["name"] for b in r.json()["books"]]
        self.assertIn("1. Mose", names)

    def test_books_case_insensitive(self):
        r = self.client.get("/api/testde/books")
        self.assertEqual(r.status_code, 200)

    def test_books_unbekannte_translation_404(self):
        r = self.client.get("/api/Unbekannt/books")
        self.assertEqual(r.status_code, 404)

    def test_kapitel_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["verses"]), 2)

    def test_vers_gueltig(self):
        r = self.client.get("/api/TestDE/1. Mose/1/1")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Anfang", r.json()["text"])

    def test_suche_findet_ergebnisse(self):
        r = self.client.get("/api/search?q=Gott&translation=TestDE")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(r.json()["total"], 0)

    def test_suche_zu_kurz_400(self):
        r = self.client.get("/api/search?q=a")
        self.assertEqual(r.status_code, 400)

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

    def test_count_zusammenfassung_korrekt(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=2"
        )
        data = r.json()
        total = data["summary"]["total_counted"] + data["summary"]["total_ignored"]
        self.assertEqual(total, data["total_unique_words"])

    def test_count_falsche_reihenfolge_400(self):
        r = self.client.get(
            "/api/count?translation=TestDE"
            "&book_from=Johannes&chapter_from=3&verse_from=16"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 400)

    def test_count_ungueltige_translation_404(self):
        r = self.client.get(
            "/api/count?translation=Unbekannt"
            "&book_from=1. Mose&chapter_from=1&verse_from=1"
            "&book_to=1. Mose&chapter_to=1&verse_to=1"
        )
        self.assertEqual(r.status_code, 404)

    def test_strong_nicht_geladen_503(self):
        from main import _strong_manager
        orig = _strong_manager._loaded
        _strong_manager._loaded = False
        try:
            r = self.client.get("/api/strong/number/H430")
            self.assertEqual(r.status_code, 503)
        finally:
            _strong_manager._loaded = orig


if __name__ == "__main__":
    unittest.main()

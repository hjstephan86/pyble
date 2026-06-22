import unittest
from pydantic import ValidationError
from src.models import VerseResponse, ChapterResponse, BookResponse, BibleListResponse


class TestModels(unittest.TestCase):
    
    def test_verse_response_valid(self):
        """Test VerseResponse with valid data"""
        verse_data = {
            "book": "1. Mose",
            "chapter": 1,
            "verse": 1,
            "text": "Im Anfang schuf Gott die Himmel und die Erde.",
            "translation": "Elberfelder 1905"
        }
        
        verse = VerseResponse(**verse_data)
        
        self.assertEqual(verse.book, "1. Mose")
        self.assertEqual(verse.chapter, 1)
        self.assertEqual(verse.verse, 1)
        self.assertEqual(verse.text, "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(verse.translation, "Elberfelder 1905")
    
    def test_verse_response_type_validation(self):
        """Test VerseResponse type validation"""
        # Test with invalid chapter type
        with self.assertRaises(ValidationError):
            VerseResponse(
                book="1. Mose",
                chapter="not_a_number",  # Should be int
                verse=1,
                text="Test text",
                translation="Test"
            )
    
    def test_verse_response_missing_field(self):
        """Test VerseResponse with missing required field"""
        with self.assertRaises(ValidationError):
            VerseResponse(
                book="1. Mose",
                chapter=1,
                verse=1,
                # Missing text field
                translation="Test"
            )
    
    def test_verse_response_serialization(self):
        """Test VerseResponse serialization"""
        verse = VerseResponse(
            book="1. Mose",
            chapter=1,
            verse=1,
            text="Im Anfang schuf Gott die Himmel und die Erde.",
            translation="Elberfelder 1905"
        )
        
        data = verse.model_dump()
        expected = {
            "book": "1. Mose",
            "chapter": 1,
            "verse": 1,
            "text": "Im Anfang schuf Gott die Himmel und die Erde.",
            "translation": "Elberfelder 1905"
        }
        
        self.assertEqual(data, expected)
    
    def test_chapter_response_valid(self):
        """Test ChapterResponse with valid data"""
        verses_data = {
            1: "Im Anfang schuf Gott die Himmel und die Erde.",
            2: "Und die Erde war wüst und leer, und Finsternis war über der Tiefe.",
            3: "Und Gott sprach: Es werde Licht! und es ward Licht."
        }
        
        chapter_data = {
            "book": "1. Mose",
            "chapter": 1,
            "verses": verses_data,
            "translation": "Elberfelder 1905"
        }
        
        chapter = ChapterResponse(**chapter_data)
        
        self.assertEqual(chapter.book, "1. Mose")
        self.assertEqual(chapter.chapter, 1)
        self.assertEqual(chapter.verses, verses_data)
        self.assertEqual(chapter.translation, "Elberfelder 1905")
    
    def test_chapter_response_empty_verses(self):
        """Test ChapterResponse with empty verses"""
        chapter = ChapterResponse(
            book="1. Mose",
            chapter=1,
            verses={},
            translation="Elberfelder 1905"
        )
        
        self.assertEqual(chapter.verses, {})
    
    def test_chapter_response_type_validation(self):
        """Test ChapterResponse type validation"""
        # Test with invalid verses type
        with self.assertRaises(ValidationError):
            ChapterResponse(
                book="1. Mose",
                chapter=1,
                verses="not_a_dict",  # Should be dict
                translation="Test"
            )
    
    def test_chapter_response_serialization(self):
        """Test ChapterResponse serialization"""
        verses_data = {
            1: "Im Anfang schuf Gott die Himmel und die Erde.",
            2: "Und die Erde war wüst und leer."
        }
        
        chapter = ChapterResponse(
            book="1. Mose",
            chapter=1,
            verses=verses_data,
            translation="Elberfelder 1905"
        )
        
        data = chapter.model_dump()
        expected = {
            "book": "1. Mose",
            "chapter": 1,
            "verses": verses_data,
            "translation": "Elberfelder 1905"
        }
        
        self.assertEqual(data, expected)
    
    def test_book_response_valid(self):
        """Test BookResponse with valid data"""
        chapters_data = {
            1: {
                1: "Im Anfang schuf Gott die Himmel und die Erde.",
                2: "Und die Erde war wüst und leer."
            },
            2: {
                1: "Und die Himmel und die Erde wurden vollendet."
            }
        }
        
        book_data = {
            "book": "1. Mose",
            "chapters": chapters_data,
            "translation": "Elberfelder 1905"
        }
        
        book = BookResponse(**book_data)
        
        self.assertEqual(book.book, "1. Mose")
        self.assertEqual(book.chapters, chapters_data)
        self.assertEqual(book.translation, "Elberfelder 1905")
    
    def test_book_response_empty_chapters(self):
        """Test BookResponse with empty chapters"""
        book = BookResponse(
            book="1. Mose",
            chapters={},
            translation="Elberfelder 1905"
        )
        
        self.assertEqual(book.chapters, {})
    
    def test_book_response_complex_structure(self):
        """Test BookResponse with complex nested structure"""
        complex_chapters = {
            1: {
                1: "Verse 1:1",
                2: "Verse 1:2",
                3: "Verse 1:3"
            },
            2: {
                1: "Verse 2:1",
                2: "Verse 2:2"
            },
            3: {
                1: "Verse 3:1"
            }
        }
        
        book = BookResponse(
            book="Test Book",
            chapters=complex_chapters,
            translation="Test Translation"
        )
        
        self.assertEqual(len(book.chapters), 3)
        self.assertEqual(len(book.chapters[1]), 3)
        self.assertEqual(len(book.chapters[2]), 2)
        self.assertEqual(len(book.chapters[3]), 1)
    
    def test_book_response_serialization(self):
        """Test BookResponse serialization"""
        chapters_data = {
            1: {
                1: "Im Anfang schuf Gott die Himmel und die Erde."
            }
        }
        
        book = BookResponse(
            book="1. Mose",
            chapters=chapters_data,
            translation="Elberfelder 1905"
        )
        
        data = book.model_dump()
        expected = {
            "book": "1. Mose",
            "chapters": chapters_data,
            "translation": "Elberfelder 1905"
        }
        
        self.assertEqual(data, expected)
    
    def test_bible_list_response_valid(self):
        """Test BibleListResponse with valid data"""
        translations = ["Elberfelder 1905", "WorldEnglishBible", "Schlachter 1951"]
        
        bible_list = BibleListResponse(translations=translations)
        
        self.assertEqual(bible_list.translations, translations)
    
    def test_bible_list_response_empty(self):
        """Test BibleListResponse with empty list"""
        bible_list = BibleListResponse(translations=[])
        
        self.assertEqual(bible_list.translations, [])
    
    def test_bible_list_response_single_item(self):
        """Test BibleListResponse with single item"""
        bible_list = BibleListResponse(translations=["Elberfelder 1905"])
        
        self.assertEqual(bible_list.translations, ["Elberfelder 1905"])
        self.assertEqual(len(bible_list.translations), 1)
    
    def test_bible_list_response_type_validation(self):
        """Test BibleListResponse type validation"""
        # Test with invalid type
        with self.assertRaises(ValidationError):
            BibleListResponse(translations="not_a_list")
    
    def test_bible_list_response_serialization(self):
        """Test BibleListResponse serialization"""
        translations = ["Elberfelder 1905", "WorldEnglishBible"]
        
        bible_list = BibleListResponse(translations=translations)
        
        data = bible_list.model_dump()
        expected = {"translations": translations}
        
        self.assertEqual(data, expected)
    
    def test_all_models_json_serialization(self):
        """Test JSON serialization for all models"""
        import json
        
        # Test VerseResponse
        verse = VerseResponse(
            book="1. Mose",
            chapter=1,
            verse=1,
            text="Im Anfang schuf Gott die Himmel und die Erde.",
            translation="Elberfelder 1905"
        )
        verse_json = verse.model_dump_json()
        self.assertIsInstance(verse_json, str)
        verse_dict = json.loads(verse_json)
        self.assertEqual(verse_dict["book"], "1. Mose")
        
        # Test ChapterResponse
        chapter = ChapterResponse(
            book="1. Mose",
            chapter=1,
            verses={1: "Test verse"},
            translation="Elberfelder 1905"
        )
        chapter_json = chapter.model_dump_json()
        self.assertIsInstance(chapter_json, str)
        
        # Test BookResponse
        book = BookResponse(
            book="1. Mose",
            chapters={1: {1: "Test verse"}},
            translation="Elberfelder 1905"
        )
        book_json = book.model_dump_json()
        self.assertIsInstance(book_json, str)
        
        # Test BibleListResponse
        bible_list = BibleListResponse(translations=["Test"])
        list_json = bible_list.model_dump_json()
        self.assertIsInstance(list_json, str)
    
    def test_model_validation_edge_cases(self):
        """Test model validation with edge cases"""
        # Test with very long strings
        long_text = "A" * 10000
        verse = VerseResponse(
            book=long_text,
            chapter=1,
            verse=1,
            text=long_text,
            translation=long_text
        )
        self.assertEqual(len(verse.text), 10000)
        
        # Test with zero values
        verse_zero = VerseResponse(
            book="Book",
            chapter=0,
            verse=0,
            text="",
            translation="Translation"
        )
        self.assertEqual(verse_zero.chapter, 0)
        self.assertEqual(verse_zero.verse, 0)
        self.assertEqual(verse_zero.text, "")
        
        # Test with negative values (should work as they're just integers)
        verse_negative = VerseResponse(
            book="Book",
            chapter=-1,
            verse=-1,
            text="Text",
            translation="Translation"
        )
        self.assertEqual(verse_negative.chapter, -1)
        self.assertEqual(verse_negative.verse, -1)


if __name__ == '__main__':
    unittest.main()
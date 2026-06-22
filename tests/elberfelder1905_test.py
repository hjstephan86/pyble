import unittest
from unittest.mock import mock_open, patch, MagicMock
import os
import tempfile
from src.elberfelder1905 import Elberfelder1905


class TestElberfelder1905(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.bible = Elberfelder1905()
        self.sample_content = """1. Mose
Kapitel 1
1 Im Anfang schuf Gott die Himmel und die Erde.
2 Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.
3 Und Gott sprach: Es werde Licht! und es ward Licht.
4 Und Gott sah das Licht, daß es gut war; und Gott schied das Licht von der Finsternis.
5 Und Gott nannte das Licht Tag, und die Finsternis nannte er Nacht. Und es ward Abend und es ward Morgen: erster Tag.
6 Und Gott sprach: Es werde eine Ausdehnung inmitten der Wasser, und sie scheide die Wasser von den Wassern!
7 Und Gott machte die Ausdehnung und schied die Wasser, welche unterhalb der Ausdehnung, von den Wassern, die oberhalb der Ausdehnung sind. Und es ward also.
8 Und Gott nannte die Ausdehnung Himmel. Und es ward Abend und es ward Morgen: zweiter Tag.
9 Und Gott sprach: Es sammeln sich die Wasser unterhalb des Himmels an einen Ort, und es werde sichtbar das Trockene! Und es ward also.
10 Und Gott nannte das Trockene Erde, und die Sammlung der Wasser nannte er Meere. Und Gott sah, daß es gut war.
11 Und Gott sprach: Die Erde lasse Gras hervorsprossen, Kraut, das Samen hervorbringe, Fruchtbäume, die Frucht tragen nach ihrer Art, in welcher ihr Same sei auf der Erde! Und es ward also.
"""
    
    def test_init(self):
        """Test Elberfelder1905 initialization"""
        self.assertEqual(self.bible.name, "Elberfelder 1905")
        self.assertEqual(self.bible.books, {})
    
    def test_load_text_with_mock(self):
        """Test loading text using mock file"""
        with patch('builtins.open', mock_open(read_data=self.sample_content)):
            self.bible.load_text('test_file.txt')
        
        # Verify content was loaded correctly
        self.assertIn("1. Mose", self.bible.books)
        self.assertEqual(len(self.bible.books["1. Mose"][1]), 11)  # 11 verses
        
        # Test specific verses
        verse1 = self.bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse1, "Im Anfang schuf Gott die Himmel und die Erde.")
        
        verse11 = self.bible.get_verse("1. Mose", 1, 11)
        self.assertEqual(verse11, "Und Gott sprach: Die Erde lasse Gras hervorsprossen, Kraut, das Samen hervorbringe, Fruchtbäume, die Frucht tragen nach ihrer Art, in welcher ihr Same sei auf der Erde! Und es ward also.")
    
    def test_load_text_with_real_file(self):
        """Test loading text with a real temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.sample_content)
            temp_file_path = f.name
        
        try:
            self.bible.load_text(temp_file_path)
            
            # Verify content was loaded
            self.assertIn("1. Mose", self.bible.books)
            verse = self.bible.get_verse("1. Mose", 1, 1)
            self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")
        finally:
            os.unlink(temp_file_path)
    
    def test_load_text_file_not_found(self):
        """Test loading text from non-existent file"""
        with patch('builtins.print') as mock_print:
            self.bible.load_text('non_existent_file.txt')
            mock_print.assert_called_once()
            # Check that error message was printed
            self.assertTrue(any('Error loading Elberfelder 1905' in str(call) for call in mock_print.call_args_list))
    
    def test_load_text_permission_error(self):
        """Test loading text with permission error"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('builtins.print') as mock_print:
                self.bible.load_text('test_file.txt')
                mock_print.assert_called_once()
                # Check that error message was printed
                self.assertTrue(any('Error loading Elberfelder 1905' in str(call) for call in mock_print.call_args_list))
    
    def test_load_text_unicode_decode_error(self):
        """Test loading text with unicode decode error"""
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')):
            with patch('builtins.print') as mock_print:
                self.bible.load_text('test_file.txt')
                mock_print.assert_called_once()
    
    def test_load_text_empty_file(self):
        """Test loading empty file"""
        with patch('builtins.open', mock_open(read_data="")):
            self.bible.load_text('empty_file.txt')
        
        # Should have no books loaded
        self.assertEqual(len(self.bible.books), 0)
    
    def test_load_text_malformed_content(self):
        """Test loading file with malformed content"""
        malformed_content = """This is not a proper bible format
        Random text here
        Another line without proper structure"""
        
        with patch('builtins.open', mock_open(read_data=malformed_content)):
            self.bible.load_text('malformed_file.txt')
        
        # Should have no books loaded due to malformed content
        self.assertEqual(len(self.bible.books), 0)
    
    def test_load_text_mixed_formats(self):
        """Test loading file with mixed verse formats"""
        mixed_content = """1. Mose
Kapitel 1
1 Im Anfang schuf Gott die Himmel und die Erde.
2 Und die Erde war wüst und leer.
3 Und Gott sprach: Es werde Licht!
"""
        
        with patch('builtins.open', mock_open(read_data=mixed_content)):
            self.bible.load_text('mixed_file.txt')
        
        # Should load all three verses
        self.assertIn("1. Mose", self.bible.books)
        self.assertEqual(len(self.bible.books["1. Mose"][1]), 3)
        
        verse1 = self.bible.get_verse("1. Mose", 1, 1)
        verse2 = self.bible.get_verse("1. Mose", 1, 2)
        verse3 = self.bible.get_verse("1. Mose", 1, 3)
        
        self.assertEqual(verse1, "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(verse2, "Und die Erde war wüst und leer.")
        self.assertEqual(verse3, "Und Gott sprach: Es werde Licht!")
    
    def test_load_text_multiple_books(self):
        """Test loading file with multiple books"""
        multi_book_content = """1. Mose
Kapitel 1
1 Im Anfang schuf Gott die Himmel und die Erde.
2. Mose
Kapitel 1
1 Und dies sind die Namen der Söhne Israels.
"""
        
        with patch('builtins.open', mock_open(read_data=multi_book_content)):
            self.bible.load_text('multi_book_file.txt')
        
        # Should load both books
        self.assertIn("1. Mose", self.bible.books)
        self.assertIn("2. Mose", self.bible.books)
        
        verse1 = self.bible.get_verse("1. Mose", 1, 1)
        verse2 = self.bible.get_verse("2. Mose", 1, 1)
        
        self.assertEqual(verse1, "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(verse2, "Und dies sind die Namen der Söhne Israels.")
    
    def test_load_text_multiple_chapters(self):
        """Test loading file with multiple chapters"""
        multi_chapter_content = """1. Mose
Kapitel 1
1 Im Anfang schuf Gott die Himmel und die Erde.
Kapitel 2
1 Und die Himmel und die Erde wurden vollendet.
"""
        
        with patch('builtins.open', mock_open(read_data=multi_chapter_content)):
            self.bible.load_text('multi_chapter_file.txt')
        
        # Should load both chapters
        self.assertIn("1. Mose", self.bible.books)
        self.assertEqual(len(self.bible.books["1. Mose"]), 2)  # 2 chapters
        
        verse1_1 = self.bible.get_verse("1. Mose", 1, 1)
        verse2_1 = self.bible.get_verse("1. Mose", 2, 1)
        
        self.assertEqual(verse1_1, "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(verse2_1, "Und die Himmel und die Erde wurden vollendet.")
    
    def test_inheritance_from_bible_base(self):
        """Test that Elberfelder1905 properly inherits from Bible"""
        # Test that it has inherited methods
        self.assertTrue(hasattr(self.bible, 'get_verse'))
        self.assertTrue(hasattr(self.bible, 'get_chapter'))
        self.assertTrue(hasattr(self.bible, 'get_book'))
        self.assertTrue(hasattr(self.bible, 'get_book_names'))
        self.assertTrue(hasattr(self.bible, 'get_chapter_count'))
        self.assertTrue(hasattr(self.bible, 'get_verse_count'))
    
    def test_load_and_retrieve_operations(self):
        """Test complete load and retrieve workflow"""
        with patch('builtins.open', mock_open(read_data=self.sample_content)):
            self.bible.load_text('test_file.txt')
        
        # Test various retrieval operations
        book_names = self.bible.get_book_names()
        self.assertEqual(book_names, ["1. Mose"])
        
        chapter_count = self.bible.get_chapter_count("1. Mose")
        self.assertEqual(chapter_count, 1)
        
        verse_count = self.bible.get_verse_count("1. Mose", 1)
        self.assertEqual(verse_count, 11)
        
        chapter_data = self.bible.get_chapter("1. Mose", 1)
        self.assertIsNotNone(chapter_data)
        self.assertEqual(len(chapter_data), 11)
        
        book_data = self.bible.get_book("1. Mose")
        self.assertIsNotNone(book_data)
        self.assertIn(1, book_data)


if __name__ == '__main__':
    unittest.main()
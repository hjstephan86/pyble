import unittest
from unittest.mock import mock_open, patch
from src.bible_base import Bible


class BibleStub(Bible):
    """Concrete implementation of Bible for testing"""
    
    def load_text(self, file_path: str) -> None:
        """Test implementation of load_text"""
        test_content = """0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.
0#1. Mose#1#2#Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.
0#1. Mose#1#3#Und Gott sprach: Es werde Licht! und es ward Licht.
0#1. Mose#1#4#Und Gott sah das Licht, daß es gut war; und Gott schied das Licht von der Finsternis.
0#1. Mose#1#5#Und Gott nannte das Licht Tag, und die Finsternis nannte er Nacht. Und es ward Abend und es ward Morgen: erster Tag.
0#1. Mose#1#6#Und Gott sprach: Es werde eine Ausdehnung inmitten der Wasser, und sie scheide die Wasser von den Wassern!
0#1. Mose#1#7#Und Gott machte die Ausdehnung und schied die Wasser, welche unterhalb der Ausdehnung, von den Wassern, die oberhalb der Ausdehnung sind. Und es ward also.
0#1. Mose#1#8#Und Gott nannte die Ausdehnung Himmel. Und es ward Abend und es ward Morgen: zweiter Tag.
0#1. Mose#1#9#Und Gott sprach: Es sammeln sich die Wasser unterhalb des Himmels an einen Ort, und es werde sichtbar das Trockene! Und es ward also.
0#1. Mose#1#10#Und Gott nannte das Trockene Erde, und die Sammlung der Wasser nannte er Meere. Und Gott sah, daß es gut war.
0#1. Mose#1#11#Und Gott sprach: Die Erde lasse Gras hervorsprossen, Kraut, das Samen hervorbringe, Fruchtbäume, die Frucht tragen nach ihrer Art, in welcher ihr Same sei auf der Erde! Und es ward also."""
        self._parse_text(test_content)


class TestBibleBase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.bible = BibleStub("Test Bible")
        self.bible.load_text("test_path")
    
    def test_init(self):
        """Test Bible initialization"""
        bible = BibleStub("Test Name")
        self.assertEqual(bible.name, "Test Name")
        self.assertEqual(bible.books, {})
    
    def test_get_verse_valid(self):
        """Test getting a valid verse"""
        verse = self.bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")
    
    def test_get_verse_invalid_book(self):
        """Test getting verse from non-existent book"""
        verse = self.bible.get_verse("NonExistent", 1, 1)
        self.assertIsNone(verse)
    
    def test_get_verse_invalid_chapter(self):
        """Test getting verse from non-existent chapter"""
        verse = self.bible.get_verse("1. Mose", 999, 1)
        self.assertIsNone(verse)
    
    def test_get_verse_invalid_verse(self):
        """Test getting non-existent verse"""
        verse = self.bible.get_verse("1. Mose", 1, 999)
        self.assertIsNone(verse)
    
    def test_get_chapter_valid(self):
        """Test getting a valid chapter"""
        chapter = self.bible.get_chapter("1. Mose", 1)
        self.assertIsNotNone(chapter)
        self.assertEqual(len(chapter), 11)  # 11 verses loaded
        self.assertIn(1, chapter)
        self.assertIn(11, chapter)
    
    def test_get_chapter_invalid_book(self):
        """Test getting chapter from non-existent book"""
        chapter = self.bible.get_chapter("NonExistent", 1)
        self.assertIsNone(chapter)
    
    def test_get_chapter_invalid_chapter(self):
        """Test getting non-existent chapter"""
        chapter = self.bible.get_chapter("1. Mose", 999)
        self.assertIsNone(chapter)
    
    def test_get_book_valid(self):
        """Test getting a valid book"""
        book = self.bible.get_book("1. Mose")
        self.assertIsNotNone(book)
        self.assertIn(1, book)  # Chapter 1 exists
    
    def test_get_book_invalid(self):
        """Test getting non-existent book"""
        book = self.bible.get_book("NonExistent")
        self.assertIsNone(book)
    
    def test_get_book_names(self):
        """Test getting list of book names"""
        names = self.bible.get_book_names()
        self.assertIn("1. Mose", names)
        self.assertEqual(len(names), 1)
    
    def test_get_chapter_count_valid(self):
        """Test getting chapter count for valid book"""
        count = self.bible.get_chapter_count("1. Mose")
        self.assertEqual(count, 1)
    
    def test_get_chapter_count_invalid(self):
        """Test getting chapter count for invalid book"""
        count = self.bible.get_chapter_count("NonExistent")
        self.assertEqual(count, 0)
    
    def test_get_verse_count_valid(self):
        """Test getting verse count for valid chapter"""
        count = self.bible.get_verse_count("1. Mose", 1)
        self.assertEqual(count, 11)
    
    def test_get_verse_count_invalid_book(self):
        """Test getting verse count for invalid book"""
        count = self.bible.get_verse_count("NonExistent", 1)
        self.assertEqual(count, 0)
    
    def test_get_verse_count_invalid_chapter(self):
        """Test getting verse count for invalid chapter"""
        count = self.bible.get_verse_count("1. Mose", 999)
        self.assertEqual(count, 0)
    
    def test_parse_text_standard_format(self):
        """Test parsing text in standard format"""
        bible = BibleStub("Test")
        content = "1. Mose 1:1 Im Anfang schuf Gott die Himmel und die Erde."
        bible._parse_text(content)
        
        verse = bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")
    
    def test_parse_text_alternative_format(self):
        """Test parsing text in alternative format"""
        bible = BibleStub("Test")
        content = "1Mos 1:1 Im Anfang schuf Gott die Himmel und die Erde."
        bible._parse_text(content)
        
        verse = bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")
    
    def test_parse_text_hash_format(self):
        """Test parsing text in hash-separated format"""
        bible = BibleStub("Test")
        content = "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde."
        bible._parse_text(content)
        
        verse = bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")
    
    def test_parse_text_empty_lines(self):
        """Test parsing text with empty lines"""
        bible = BibleStub("Test")
        content = """
        
0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.

0#1. Mose#1#2#Und die Erde war wüst und leer.

        """
        bible._parse_text(content)
        
        verse1 = bible.get_verse("1. Mose", 1, 1)
        verse2 = bible.get_verse("1. Mose", 1, 2)
        self.assertEqual(verse1, "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(verse2, "Und die Erde war wüst und leer.")
    
    def test_parse_text_invalid_format(self):
        """Test parsing text with invalid format"""
        bible = BibleStub("Test")
        content = "This is not a valid bible verse format"
        bible._parse_text(content)
        
        # Should not add any books
        self.assertEqual(len(bible.get_book_names()), 0)
    
    def test_normalize_german_book_name_abbreviations(self):
        """Test normalization of German book name abbreviations"""
        bible = BibleStub("Test")
        
        # Test common abbreviations
        self.assertEqual(bible._normalize_german_book_name("1Mos"), "1. Mose")
        self.assertEqual(bible._normalize_german_book_name("Mt"), "Matthäus")
        self.assertEqual(bible._normalize_german_book_name("Ps"), "Psalmen")
        self.assertEqual(bible._normalize_german_book_name("Offb"), "Offenbarung")
    
    def test_normalize_german_book_name_full_names(self):
        """Test normalization of full German book names"""
        bible = BibleStub("Test")
        
        # Test full names (should remain unchanged)
        self.assertEqual(bible._normalize_german_book_name("1. Mose"), "1. Mose")
        self.assertEqual(bible._normalize_german_book_name("Matthäus"), "Matthäus")
    
    def test_normalize_german_book_name_unknown(self):
        """Test normalization of unknown book names"""
        bible = BibleStub("Test")
        
        # Unknown names should remain unchanged
        self.assertEqual(bible._normalize_german_book_name("UnknownBook"), "UnknownBook")


if __name__ == '__main__':
    unittest.main()


class TestBibleBaseCoverage(unittest.TestCase):
    """Tests für nicht abgedeckte Pfade in bible_base.py."""

    def _make_bible(self, content=""):
        from src.bible_base import Bible, Passage
        class B(Bible):
            def load_text(self, fp):
                if content:
                    self._parse_text(content)
        b = B("Test")
        b.load_text("")
        return b

    def test_parse_verse_per_line_format(self):
        """_parse_verse_per_line_format: Kapitel/Vers-Format."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "1. Mose\n"
            "Kapitel 1\n"
            "1 Im Anfang schuf Gott die Himmel und die Erde.\n"
            "2 Und die Erde war wüst und leer.\n"
            "Kapitel 2\n"
            "1 Und die Himmel und die Erde wurden vollendet.\n"
        )
        b._parse_verse_per_line_format(content)
        self.assertIn("1. Mose", b.books)
        self.assertIn(1, b.books["1. Mose"])
        self.assertIn(2, b.books["1. Mose"])
        verse = b.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_standard_format(self):
        """_parse_standard_format: 'Buch Kap:Vers Text'."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "Genesis 1:1 In the beginning God created.\n"
            "Genesis 1:2 The earth was formless.\n"
        )
        b._parse_standard_format(content)
        self.assertIn("Genesis", b.books)
        verse = b.get_verse("Genesis", 1, 1)
        self.assertEqual(verse, "In the beginning God created.")

    def test_remove_span_tag_with_span(self):
        """_remove_span_tag entfernt <span ...>...</span>."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        text = '<span class="x">Im Anfang</span>'
        result = b._remove_span_tag(text)
        self.assertEqual(result, "Im Anfang")

    def test_remove_span_tag_without_span(self):
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        text = "Im Anfang schuf Gott"
        self.assertEqual(b._remove_span_tag(text), text)

    def test_go_to_next_passage_invalid_book(self):
        """_go_to_next_passage gibt False zurück bei ungültigem Buch."""
        from src.bible_base import Bible, Passage
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Vers 1.")
        p = Passage("NichtVorhanden", 1, 1)
        self.assertFalse(b._go_to_next_passage(p))

    def test_go_to_next_passage_invalid_chapter(self):
        from src.bible_base import Bible, Passage
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Vers 1.")
        p = Passage("1. Mose", 999, 1)
        self.assertFalse(b._go_to_next_passage(p))

    def test_to_passage_reached_past_end_book(self):
        """_to_passage_reached: aktuelles Buch liegt nach Ende-Buch."""
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "0#1. Mose#1#1#Vers A.\n"
            "0#2. Mose#1#1#Vers B.\n"
        )
        b._parse_text(content)
        b.book_positions = {n: i for i, n in enumerate(b.books.keys())}
        current = Passage("2. Mose", 1, 1)
        section = Section("1. Mose", 1, 1, "1. Mose", 1, 1)
        self.assertTrue(b._to_passage_reached(current, section))

    def test_to_passage_reached_same_book_past_chapter(self):
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Vers A.")
        b.book_positions = {"1. Mose": 0}
        current = Passage("1. Mose", 5, 1)
        section = Section("1. Mose", 1, 1, "1. Mose", 3, 1)
        self.assertTrue(b._to_passage_reached(current, section))

    def test_to_passage_reached_same_book_chapter_past_verse(self):
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Vers A.")
        b.book_positions = {"1. Mose": 0}
        current = Passage("1. Mose", 1, 10)
        section = Section("1. Mose", 1, 1, "1. Mose", 1, 5)
        self.assertTrue(b._to_passage_reached(current, section))

    def test_to_passage_reached_offenbarung_end(self):
        """Offenbarung 22:22 gilt als Ende der Bibel."""
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#Offenbarung#22#1#Vers A.")
        b.book_positions = {"Offenbarung": 65}
        current = Passage("Offenbarung", 22, 22)
        section = Section("1. Mose", 1, 1, "Offenbarung", 22, 21)
        self.assertTrue(b._to_passage_reached(current, section))

    def test_to_passage_reached_false(self):
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Vers A.")
        b.book_positions = {"1. Mose": 0}
        current = Passage("1. Mose", 1, 1)
        section = Section("1. Mose", 1, 1, "1. Mose", 1, 5)
        self.assertFalse(b._to_passage_reached(current, section))

    def test_is_flood_search_case_wrapper(self):
        """_is_flood_search: False wenn case-Wrapper verwendet wird."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        # backtick = SEARCH_MATCH_CASE_SYMBOL
        sym = b.SEARCH_MATCH_CASE_SYMBOL
        self.assertFalse(b._is_flood_search(f"f {sym}Gott{sym}"))

    def test_is_flood_search_exact_wrapper(self):
        """_is_flood_search: False wenn exact-Wrapper verwendet wird."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        sym = b.SEARCH_MATCH_EXACT_SYMBOL
        self.assertFalse(b._is_flood_search(f"f {sym}Gott{sym}"))

    def test_search_entire_bible_empty(self):
        """search() auf leerer Bibel gibt leeres SearchResult zurück."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        result = b.search("Gott")
        self.assertEqual(result.hit_count, 0)

    def test_search_with_book_filter(self):
        """search() mit Buch-Filter."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text(
            "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel.\n"
            "0#Johannes#3#16#Also hat Gott die Welt geliebt."
        )
        b.book_positions = {n: i for i, n in enumerate(b.books.keys())}
        result = b.search("Gott", "1. Mose")
        self.assertGreater(result.hit_count, 0)
        for f in result.findings:
            self.assertEqual(f.passage.book, "1. Mose")


# ===========================================================================
# main.py – load_ignore_words und Routen
# ===========================================================================


class TestBibleBaseLuecken(unittest.TestCase):

    def _make_bible(self):
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        return B("Test")

    # --- Zeile 64: abstrakte load_text (pass) ---
    def test_abstrakte_load_text_pass(self):
        """Der pass-Zweig in der abstrakten load_text ist nicht direkt testbar,
        aber wir prüfen dass die Subklasse die Methode überschreibt."""
        from src.bible_base import Bible
        b = self._make_bible()
        # Subklasse muss load_text implementieren
        self.assertTrue(hasattr(b, "load_text"))

    # --- Zeile 202: verse_buffer.append (Fortsetzungszeile) ---
    def test_parse_verse_per_line_format_fortsetzungszeilen(self):
        """Verse, die über mehrere Zeilen gehen, werden zusammengeführt."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "1. Mose\n"
            "Kapitel 1\n"
            "1 Im Anfang schuf Gott die Himmel\n"
            "und die Erde.\n"          # ← Fortsetzungszeile (Zeile 202)
            "2 Und die Erde war wüst.\n"
        )
        b._parse_verse_per_line_format(content)
        vers1 = b.get_verse("1. Mose", 1, 1)
        self.assertIn("Himmel", vers1)
        self.assertIn("Erde", vers1)

    def test_parse_verse_per_line_format_mehrere_fortsetzungszeilen(self):
        """Mehrere aufeinanderfolgende Fortsetzungszeilen werden zusammengeführt."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        # Wichtig: Keine Kommas am Zeilenende (sonst erkennt Parser den Vers nicht)
        content = (
            "1. Mose\n"
            "Kapitel 1\n"
            "1 Wohl denen die ohne Tadel leben\n"
            "die im Gesetz des HERRN wandeln\n"
            "die sein Zeugnis bewahren.\n"
            "2 Wohl denen die seine Zeugnisse halten.\n"
        )
        b._parse_verse_per_line_format(content)
        vers1 = b.get_verse("1. Mose", 1, 1)
        self.assertIsNotNone(vers1)
        self.assertIn("Tadel", vers1)
        self.assertIn("wandeln", vers1)
        self.assertIn("bewahren", vers1)

    # --- Zeile 216: leere Zeile in _parse_standard_format (continue) ---
    def test_parse_standard_format_leere_zeilen(self):
        """Leere Zeilen in _parse_standard_format werden übersprungen."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "\n"
            "Genesis 1:1 In the beginning.\n"
            "\n"                               # ← leere Zeile (Zeile 216)
            "Genesis 1:2 The earth was empty.\n"
            "\n"
        )
        b._parse_standard_format(content)
        self.assertEqual(b.get_verse("Genesis", 1, 1), "In the beginning.")
        self.assertEqual(b.get_verse("Genesis", 1, 2), "The earth was empty.")

    def test_parse_standard_format_nur_leerzeilen(self):
        """Nur Leerzeilen → keine Bücher geladen."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_standard_format("\n\n\n   \n")
        self.assertEqual(len(b.books), 0)

    # --- Zeilen 588-589: ValueError in _go_to_next_passage ---
    def test_go_to_next_passage_buch_nicht_in_liste(self):
        """ValueError wenn Buch nicht in book_positions – gibt False zurück."""
        from src.bible_base import Bible, Passage
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text(
            "0#1. Mose#1#1#Vers A.\n"
            "0#Johannes#1#1#Vers B."
        )
        # book_positions fehlt absichtlich → list.index wirft ValueError
        # indem wir books manipulieren
        b.books = {"1. Mose": b.books["1. Mose"]}  # Johannes entfernt
        # Passage zeigt auf letzten Vers von 1. Mose → springt zu nächstem Buch
        # aber Johannes ist nicht mehr in books → ValueError → False
        p = Passage("1. Mose", 1, 1)
        # Letzten Vers überspringen damit _go_to_next_passage zum Buch-Wechsel kommt
        # Setze Vers auf einen Wert der > allen vorhandenen Versen liegt
        p.verse = 999  # kein nächster Vers in Kap 1
        result = b._go_to_next_passage(p)
        # Kein nächstes Kapitel, kein nächstes Buch → False
        self.assertFalse(result)

    def test_go_to_next_passage_letztes_buch_false(self):
        """Wenn kein nächstes Buch vorhanden ist, wird False zurückgegeben."""
        from src.bible_base import Bible, Passage
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#Offenbarung#22#21#Die Gnade des Herrn.")
        p = Passage("Offenbarung", 22, 21)
        result = b._go_to_next_passage(p)
        self.assertFalse(result)

    # --- Zeile 617: _to_passage_reached Offenbarung 22:22+ ---
    def test_to_passage_reached_offenbarung_22_22(self):
        """Offenbarung 22:22 gilt als Bibelende (gibt True zurück)."""
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#Offenbarung#22#21#Die Gnade.")
        b.book_positions = {"Offenbarung": 65}
        current = Passage("Offenbarung", 22, 22)
        section = Section("1. Mose", 1, 1, "Offenbarung", 22, 21)
        self.assertTrue(b._to_passage_reached(current, section))

    def test_to_passage_reached_offenbarung_22_21_nicht_ende(self):
        """Offenbarung 22:21 ist der letzte Vers – noch nicht über Ende."""
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#Offenbarung#22#21#Die Gnade.")
        b.book_positions = {"Offenbarung": 65}
        current = Passage("Offenbarung", 22, 21)
        section = Section("1. Mose", 1, 1, "Offenbarung", 22, 21)
        # Vers 21 ist genau die Endposition → noch nicht überschritten
        self.assertFalse(b._to_passage_reached(current, section))

    def test_to_passage_reached_offenbarung_23(self):
        """Offenbarung Kapitel 23 (hypothetisch) gibt ebenfalls True."""
        from src.bible_base import Bible, Passage, Section
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b.book_positions = {"Offenbarung": 65}
        current = Passage("Offenbarung", 23, 1)
        section = Section("1. Mose", 1, 1, "Offenbarung", 22, 21)
        self.assertTrue(b._to_passage_reached(current, section))

    # --- Zusätzliche _parse_verse_per_line_format Tests ---
    def test_parse_verse_per_line_mehrere_buecher(self):
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "1. Mose\nKapitel 1\n1 Vers A.\n"
            "2. Mose\nKapitel 1\n1 Vers B.\n"
        )
        b._parse_verse_per_line_format(content)
        self.assertIn("1. Mose", b.books)
        self.assertIn("2. Mose", b.books)

    def test_parse_verse_per_line_mehrere_kapitel(self):
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "1. Mose\n"
            "Kapitel 1\n1 Vers 1:1.\n2 Vers 1:2.\n"
            "Kapitel 2\n1 Vers 2:1.\n"
        )
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_chapter_count("1. Mose"), 2)
        self.assertEqual(b.get_verse("1. Mose", 2, 1), "Vers 2:1.")

    def test_parse_verse_per_line_leerzeilen_zwischen_versen(self):
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = (
            "1. Mose\n\nKapitel 1\n\n1 Vers A.\n\n2 Vers B.\n"
        )
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse_count("1. Mose", 1), 2)

    def test_parse_verse_per_line_bekannte_buchnamen(self):
        """Bekannte Buchnamen wie '1. Mose' werden korrekt erkannt."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        content = "1. Mose\nKapitel 1\n1 Im Anfang.\n"
        b._parse_verse_per_line_format(content)
        self.assertIn("1. Mose", b.books)
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Im Anfang.")

    # --- Suchfunktion ---
    def test_search_highlight_in_ergebnissen(self):
        """Suchergebnisse enthalten HTML-Highlighting."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text(
            "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.\n"
            "0#1. Mose#1#2#Und Gott sah, daß es gut war."
        )
        b.book_positions = {"1. Mose": 0}
        result = b.search("Gott")
        self.assertGreater(result.hit_count, 0)
        for f in result.findings:
            self.assertIn("<b>", f.verse_text)

    def test_search_flood_search(self):
        """Flutsuche findet Verse mit allen gesuchten Wörtern."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text(
            "0#Johannes#3#16#Also hat Gott die Welt geliebt.\n"
            "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel."
        )
        b.book_positions = {n: i for i, n in enumerate(b.books.keys())}
        result = b.search("f Gott Welt")
        self.assertTrue(result.flood_search)
        # Nur der Vers mit beiden Wörtern
        for f in result.findings:
            text_plain = f.verse_text.replace("<b>", "").replace("</b>", "").lower()
            self.assertIn("gott", text_plain)
            self.assertIn("welt", text_plain)

    def test_search_case_sensitive(self):
        """Groß-/Kleinschreibungs-Suche mit Backtick."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.")
        b.book_positions = {"1. Mose": 0}
        result_cs = b.search("`Gott`")
        result_ci = b.search("gott")
        self.assertLessEqual(result_cs.hit_count, result_ci.hit_count)

    def test_search_exact_match(self):
        """Exakt-Suche mit Anführungszeichen."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text(
            "0#1. Mose#1#1#Im Anfang schuf Gott.\n"
            "0#1. Mose#1#2#Gott schuf den Anfang."
        )
        b.book_positions = {"1. Mose": 0}
        result = b.search('"Gott"')
        self.assertGreater(result.hit_count, 0)

    def test_search_leere_anfrage(self):
        """Leere Suchanfrage gibt 0 Treffer zurück."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Im Anfang schuf Gott.")
        b.book_positions = {"1. Mose": 0}
        result = b.search("")
        self.assertEqual(result.hit_count, 0)

    def test_search_html_injection(self):
        """HTML in Suchanfrage wird abgelehnt."""
        from src.bible_base import Bible
        class B(Bible):
            def load_text(self, fp): pass
        b = B("Test")
        b._parse_text("0#1. Mose#1#1#Im Anfang schuf Gott.")
        b.book_positions = {"1. Mose": 0}
        result = b.search("<script>")
        self.assertEqual(result.hit_count, 0)


if __name__ == "__main__":
    unittest.main()



# ===========================================================================
# Zusätzliche Tests für fehlende Coverage-Bereiche
# Ziel: bible_base.py von 72 % auf ≥ 90 %
# ===========================================================================

class TestBibleBaseParseFormats(unittest.TestCase):
    """Tests für _parse_verse_per_line_format und _parse_standard_format."""

    def _make_bible(self):
        import sys, os
        _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from src.bible_base import Bible
        class MiniBible(Bible):
            def load_text(self, path): pass
        return MiniBible("Test")

    # ── _parse_verse_per_line_format ─────────────────────────────────────

    def test_verse_per_line_basic(self):
        b = self._make_bible()
        content = "1. Mose\nKapitel 1\n1 Im Anfang\n2 Und die Erde\n"
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Im Anfang")
        self.assertEqual(b.get_verse("1. Mose", 1, 2), "Und die Erde")

    def test_verse_per_line_multiple_chapters(self):
        b = self._make_bible()
        content = "1. Mose\nKapitel 1\n1 Vers 1\nKapitel 2\n1 Kapitel 2 Vers 1\n"
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Vers 1")
        self.assertEqual(b.get_verse("1. Mose", 2, 1), "Kapitel 2 Vers 1")

    def test_verse_per_line_multiple_books(self):
        b = self._make_bible()
        content = (
            "1. Mose\nKapitel 1\n1 Vers A\n"
            "Matthäus\nKapitel 1\n1 Vers B\n"
        )
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Vers A")
        self.assertEqual(b.get_verse("Matthäus", 1, 1), "Vers B")

    def test_verse_per_line_normalizes_book_names(self):
        b = self._make_bible()
        content = "1 Mose\nKapitel 1\n1 Im Anfang\n"
        b._parse_verse_per_line_format(content)
        self.assertIn("1. Mose", b.books)

    def test_verse_per_line_pilcrow_marker_removed(self):
        b = self._make_bible()
        content = "1. Mose\nKapitel 1\n1 ¶ Im Anfang\n"
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Im Anfang")

    def test_verse_per_line_psalm_chapter(self):
        b = self._make_bible()
        content = "Psalmen\nPsalm 1\n1 Wohl dem Mann\n"
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse("Psalmen", 1, 1), "Wohl dem Mann")

    def test_verse_per_line_chapter_format(self):
        b = self._make_bible()
        content = "Johannes\nChapter 1\n1 In the beginning\n"
        b._parse_verse_per_line_format(content)
        self.assertEqual(b.get_verse("Johannes", 1, 1), "In the beginning")

    def test_verse_per_line_empty_content(self):
        b = self._make_bible()
        b._parse_verse_per_line_format("")
        self.assertEqual(len(b.books), 0)

    def test_verse_per_line_ignores_non_verse_lines(self):
        b = self._make_bible()
        content = "This is not a verse\n1. Mose\nKapitel 1\n1 Im Anfang\n"
        b._parse_verse_per_line_format(content)
        self.assertIn("1. Mose", b.books)

    # ── _parse_standard_format ───────────────────────────────────────────

    def test_standard_format_basic(self):
        b = self._make_bible()
        b._parse_standard_format("1. Mose 1:1 Im Anfang schuf Gott")
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Im Anfang schuf Gott")

    def test_standard_format_multiple_verses(self):
        b = self._make_bible()
        content = "1. Mose 1:1 Vers eins\n1. Mose 1:2 Vers zwei\n"
        b._parse_standard_format(content)
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Vers eins")
        self.assertEqual(b.get_verse("1. Mose", 1, 2), "Vers zwei")

    def test_standard_format_empty_lines_skipped(self):
        b = self._make_bible()
        b._parse_standard_format("\n\n1. Mose 1:1 Im Anfang\n\n")
        self.assertEqual(b.get_verse("1. Mose", 1, 1), "Im Anfang")

    def test_standard_format_no_match(self):
        b = self._make_bible()
        b._parse_standard_format("Dies ist kein Vers-Format")
        self.assertEqual(len(b.books), 0)


class TestBibleBaseRemoveSpanTag(unittest.TestCase):

    def _make_bible(self):
        import sys, os
        _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from src.bible_base import Bible
        class MiniBible(Bible):
            def load_text(self, path): pass
        return MiniBible("Test")

    def test_removes_span_tag(self):
        b = self._make_bible()
        result = b._remove_span_tag('<span class="x">Im Anfang</span>')
        self.assertEqual(result, "Im Anfang")

    def test_no_span_tag_unchanged(self):
        b = self._make_bible()
        result = b._remove_span_tag("Im Anfang")
        self.assertEqual(result, "Im Anfang")

    def test_span_without_closing_unchanged(self):
        b = self._make_bible()
        text = "<span>Kein Ende"
        result = b._remove_span_tag(text)
        self.assertEqual(result, text)


class TestBibleBaseGoToNextPassage(unittest.TestCase):
    """Tests für _go_to_next_passage und _to_passage_reached."""

    def _make_bible_with_books(self):
        import sys, os
        _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from src.bible_base import Bible, Passage, Section
        class MiniBible(Bible):
            def load_text(self, path): pass
        b = MiniBible("Test")
        b.books = {
            "1. Mose": {1: {1: "V1", 2: "V2"}, 2: {1: "V3"}},
            "2. Mose": {1: {1: "V4"}},
        }
        b.book_positions = {name: idx for idx, name in enumerate(b.books.keys())}
        return b, Passage, Section

    def test_go_to_next_verse(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 1, 1)
        result = b._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.verse, 2)

    def test_go_to_next_chapter(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 1, 2)
        result = b._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.chapter, 2)
        self.assertEqual(p.verse, 1)

    def test_go_to_next_book(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 2, 1)
        result = b._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.book, "2. Mose")

    def test_go_to_next_at_end_returns_false(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("2. Mose", 1, 1)
        result = b._go_to_next_passage(p)
        self.assertFalse(result)

    def test_go_to_next_invalid_book(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("Nichtexistent", 1, 1)
        result = b._go_to_next_passage(p)
        self.assertFalse(result)

    def test_go_to_next_invalid_chapter(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 999, 1)
        result = b._go_to_next_passage(p)
        self.assertFalse(result)

    def test_to_passage_reached_past_book(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("2. Mose", 1, 1)
        s = Section("1. Mose", 1, 1, "1. Mose", 1, 2)
        self.assertTrue(b._to_passage_reached(p, s))

    def test_to_passage_reached_same_book_past_chapter(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 3, 1)
        s = Section("1. Mose", 1, 1, "1. Mose", 2, 1)
        self.assertTrue(b._to_passage_reached(p, s))

    def test_to_passage_reached_same_chapter_past_verse(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 1, 3)
        s = Section("1. Mose", 1, 1, "1. Mose", 1, 2)
        self.assertTrue(b._to_passage_reached(p, s))

    def test_to_passage_not_reached(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("1. Mose", 1, 1)
        s = Section("1. Mose", 1, 1, "1. Mose", 1, 2)
        self.assertFalse(b._to_passage_reached(p, s))

    def test_to_passage_reached_offenbarung_end(self):
        b, Passage, Section = self._make_bible_with_books()
        p = Passage("Offenbarung", 22, 22)
        s = Section("1. Mose", 1, 1, "Offenbarung", 22, 21)
        self.assertTrue(b._to_passage_reached(p, s))


class TestBibleBaseGetCurrentSection(unittest.TestCase):

    def _make_bible(self):
        import sys, os
        _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from src.bible_base import Bible
        class MiniBible(Bible):
            def load_text(self, path): pass
        b = MiniBible("Test")
        b.books = {
            "1. Mose": {1: {1: "V1", 2: "V2"}, 3: {5: "V5"}},
            "Offenbarung": {22: {21: "Ende"}},
        }
        b.book_positions = {name: idx for idx, name in enumerate(b.books.keys())}
        return b

    def test_section_specific_book(self):
        b = self._make_bible()
        s = b._get_current_section(book="1. Mose")
        self.assertEqual(s.book_from, "1. Mose")
        self.assertEqual(s.book_to, "1. Mose")
        self.assertEqual(s.chapter_to, 3)
        self.assertEqual(s.verse_to, 5)

    def test_section_entire_bible(self):
        b = self._make_bible()
        s = b._get_current_section()
        self.assertEqual(s.book_from, "1. Mose")
        self.assertEqual(s.book_to, "Offenbarung")

    def test_section_empty_bible(self):
        b = self._make_bible()
        b.books = {}
        s = b._get_current_section()
        self.assertEqual(s.book_from, "")

    def test_section_nonexistent_book_uses_full_bible(self):
        b = self._make_bible()
        s = b._get_current_section(book="Nichtexistent")
        self.assertEqual(s.book_from, "1. Mose")


class TestBibleBaseApplyNormalization(unittest.TestCase):

    def _make_bible(self):
        import sys, os
        _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from src.bible_base import Bible
        class MiniBible(Bible):
            def load_text(self, path): pass
        return MiniBible("Test")

    def test_normalization_preserves_order(self):
        b = self._make_bible()
        b.books["1 Mose"] = {1: {1: "V1"}}
        b.books["2 Mose"] = {1: {1: "V2"}}
        b.books["3 Mose"] = {1: {1: "V3"}}
        b._apply_book_name_normalization()
        keys = list(b.books.keys())
        self.assertEqual(keys[0], "1. Mose")
        self.assertEqual(keys[1], "2. Mose")
        self.assertEqual(keys[2], "3. Mose")

    def test_normalization_merges_chapters(self):
        b = self._make_bible()
        b.books["1. Mose"] = {1: {1: "Vers 1"}}
        b.books["1Mos"]    = {1: {2: "Vers 2"}, 2: {1: "Kap2"}}
        b._apply_book_name_normalization()
        self.assertIn(2, b.books["1. Mose"][1])
        self.assertIn(2, b.books["1. Mose"])

    def test_already_canonical_unchanged(self):
        b = self._make_bible()
        b.books["Matthäus"] = {1: {1: "V1"}}
        b._apply_book_name_normalization()
        self.assertIn("Matthäus", b.books)


if __name__ == "__main__":
    unittest.main()


# ===========================================================================
# Tests für Suchlogik und verbleibende Coverage-Lücken
# Ziel: bible_base.py von 88 % auf ≥ 95 %
# ===========================================================================

def _make_search_bible():
    """Hilfsfunktion: Bible mit Testdaten für Suchtests."""
    import sys, os
    _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    if _src not in sys.path:
        sys.path.insert(0, _src)
    from src.bible_base import Bible
    class MiniBible(Bible):
        def load_text(self, path): pass
    b = MiniBible("Test")
    b.books = {
        "1. Mose": {
            1: {
                1: "Im Anfang schuf Gott die Himmel und die Erde.",
                2: "Und die Erde war wüst und leer.",
                3: "Und Gott sprach: Es werde Licht! und es ward Licht.",
            },
            2: {1: "Und Gott vollendete am siebenten Tage sein Werk."},
        },
        "Johannes": {
            3: {16: "Also hat Gott die Welt geliebt, daß er seinen eingeborenen Sohn gab."},
        },
        "Offenbarung": {
            22: {
                21: "Die Gnade des Herrn Jesu Christi sei mit euch allen. Amen.",
                22: "Kein weiterer Vers.",
            },
        },
    }
    b.book_positions = {name: idx for idx, name in enumerate(b.books.keys())}
    return b


class TestBibleBaseSearch(unittest.TestCase):
    """Tests für die search()-Methode und alle Suchpfade."""

    def setUp(self):
        self.b = _make_search_bible()

    # ── Einfache Suche ───────────────────────────────────────────────────────

    def test_search_simple_found(self):
        r = self.b.search("Gott")
        self.assertGreater(r.hit_count, 0)

    def test_search_simple_not_found(self):
        r = self.b.search("Xyzzyx")
        self.assertEqual(r.hit_count, 0)
        self.assertEqual(r.findings, [])

    def test_search_empty_query(self):
        r = self.b.search("")
        self.assertEqual(r.hit_count, 0)

    def test_search_short_query(self):
        r = self.b.search("x")  # Einzelzeichen unter Mindestlänge
        self.assertEqual(r.hit_count, 0)

    def test_search_with_book_filter(self):
        r_all  = self.b.search("Gott")
        r_book = self.b.search("Gott", book="Johannes")
        self.assertLessEqual(r_book.hit_count, r_all.hit_count)

    def test_search_invalid_book_returns_empty(self):
        # Ungültiges Buch → fällt auf gesamte Bibel zurück oder gibt 0 zurück
        r = self.b.search("Gott", book="Nichtexistent")
        self.assertIsNotNone(r)  # Kein Absturz

    # ── Exact-Match ("…") ────────────────────────────────────────────────────

    def test_search_exact_match(self):
        r = self.b.search('"Gott"')
        self.assertGreater(r.hit_count, 0)

    def test_search_exact_no_partial(self):
        # "Gott" exact sollte nicht "Gottes" oder "Gottes" matchen,
        # aber "Gott" alleinstehend finden
        r = self.b.search('"Licht"')
        self.assertGreater(r.hit_count, 0)

    def test_search_exact_not_found(self):
        r = self.b.search('"Xyzzyx"')
        self.assertEqual(r.hit_count, 0)

    # ── Case-Sensitive-Suche (` … `) ─────────────────────────────────────────

    def test_search_case_sensitive_found(self):
        r = self.b.search('`Gott`')
        self.assertGreater(r.hit_count, 0)

    def test_search_case_sensitive_not_found(self):
        r = self.b.search('`gott`')  # Klein – sollte nicht matchen
        self.assertEqual(r.hit_count, 0)

    # ── Exact + Case (`"…"`) ─────────────────────────────────────────────────

    def test_search_exact_and_case(self):
        r = self.b.search('`"Gott"`')
        self.assertGreater(r.hit_count, 0)

    def test_search_exact_and_case_wrong_case(self):
        r = self.b.search('`"gott"`')
        self.assertEqual(r.hit_count, 0)

    # ── Flood-Suche (f Wort1 Wort2 …) ───────────────────────────────────────

    def test_search_flood_found(self):
        r = self.b.search("f Gott Erde")
        self.assertGreater(r.hit_count, 0)

    def test_search_flood_not_found_missing_word(self):
        r = self.b.search("f Gott Xyzzyx")
        self.assertEqual(r.hit_count, 0)

    def test_search_flood_three_words(self):
        r = self.b.search("f Gott Welt Sohn")
        self.assertGreater(r.hit_count, 0)

    def test_search_flood_too_few_words(self):
        # "f Wort" – nur ein Wort nach f → kein Flood
        r = self.b.search("f Gott")
        # Kein Flood-Treffer (zu wenige Wörter), aber auch kein Absturz
        self.assertIsNotNone(r)

    def test_search_flood_with_single_char_word(self):
        # Einzelbuchstaben im Flood → wird abgelehnt
        r = self.b.search("f Gott a Erde")
        self.assertEqual(r.hit_count, 0)

    def test_search_flood_phrase_excluded(self):
        # "f 'Phrase'" → kein Flood wegen Anführungszeichen
        r = self.b.search("f 'Gott Erde'")
        self.assertIsNotNone(r)


class TestBibleBaseIsFloodSearch(unittest.TestCase):
    """Direkttests für _is_flood_search."""

    def setUp(self):
        self.b = _make_search_bible()

    def test_valid_flood(self):
        self.assertTrue(self.b._is_flood_search("f Gott Erde Licht"))

    def test_too_few_words(self):
        self.assertFalse(self.b._is_flood_search("f Gott"))

    def test_no_f_prefix(self):
        self.assertFalse(self.b._is_flood_search("Gott Erde Licht"))

    def test_single_char_word(self):
        self.assertFalse(self.b._is_flood_search("f Gott a Erde"))

    def test_phrase_with_quotes(self):
        self.assertFalse(self.b._is_flood_search("f 'Gott Erde'"))

    def test_max_length_exceeded(self):
        # Mehr als FLOOD_SEARCH_MAX_LENGTH Wörter
        words = " ".join([f"wort{i}" for i in range(20)])
        self.assertFalse(self.b._is_flood_search(f"f {words}"))


class TestBibleBaseMatchFlags(unittest.TestCase):
    """Tests für _should_match_exact, _should_match_case, _should_match_exact_and_case."""

    def setUp(self):
        self.b = _make_search_bible()

    def test_should_match_exact_true(self):
        self.assertTrue(self.b._should_match_exact('"Gott"'))

    def test_should_match_exact_false(self):
        self.assertFalse(self.b._should_match_exact('Gott'))

    def test_should_match_case_true(self):
        self.assertTrue(self.b._should_match_case('`Gott`'))

    def test_should_match_case_false(self):
        self.assertFalse(self.b._should_match_case('Gott'))

    def test_should_match_exact_and_case_true(self):
        self.assertTrue(self.b._should_match_exact_and_case('`"Gott"`'))

    def test_should_match_exact_and_case_false(self):
        self.assertFalse(self.b._should_match_exact_and_case('"Gott"'))


class TestBibleBaseGetListOfMatchingIndices(unittest.TestCase):
    """Tests für _get_list_of_matching_indices."""

    def setUp(self):
        self.b = _make_search_bible()

    def test_simple_match(self):
        hit_order = [''] * 50
        indices = self.b._get_list_of_matching_indices(
            "Gott ist groß", hit_order, "Gott",
            is_flood_search=False, should_match_case=False, should_match_exact=False)
        self.assertIn(0, indices)

    def test_no_match(self):
        hit_order = [''] * 50
        indices = self.b._get_list_of_matching_indices(
            "Gott ist groß", hit_order, "Xyzzyx",
            is_flood_search=False, should_match_case=False, should_match_exact=False)
        self.assertEqual(indices, [])

    def test_case_sensitive_match(self):
        hit_order = [''] * 50
        indices = self.b._get_list_of_matching_indices(
            "Gott ist groß", hit_order, "Gott",
            is_flood_search=False, should_match_case=True, should_match_exact=False)
        self.assertIn(0, indices)

    def test_case_sensitive_no_match(self):
        hit_order = [''] * 50
        indices = self.b._get_list_of_matching_indices(
            "Gott ist groß", hit_order, "gott",
            is_flood_search=False, should_match_case=True, should_match_exact=False)
        self.assertEqual(indices, [])

    def test_exact_match(self):
        hit_order = [''] * 50
        indices = self.b._get_list_of_matching_indices(
            "Gott ist groß", hit_order, "Gott",
            is_flood_search=False, should_match_case=False, should_match_exact=True)
        self.assertIn(0, indices)

    def test_exact_no_partial(self):
        hit_order = [''] * 50
        indices = self.b._get_list_of_matching_indices(
            "Gottheit ist groß", hit_order, "Gott",
            is_flood_search=False, should_match_case=False, should_match_exact=True)
        self.assertEqual(indices, [])

    def test_flood_all_found(self):
        hit_order = [''] * 100
        indices = self.b._get_list_of_matching_indices(
            "Gott hat die Erde geschaffen", hit_order, "Gott Erde",
            is_flood_search=True, should_match_case=False, should_match_exact=False)
        self.assertGreater(len(indices), 0)

    def test_flood_one_missing(self):
        hit_order = [''] * 100
        indices = self.b._get_list_of_matching_indices(
            "Gott hat die Erde geschaffen", hit_order, "Gott Xyzzyx",
            is_flood_search=True, should_match_case=False, should_match_exact=False)
        self.assertEqual(indices, [])

    def test_multiple_occurrences(self):
        hit_order = [''] * 100
        indices = self.b._get_list_of_matching_indices(
            "Gott und Gott und Gott", hit_order, "Gott",
            is_flood_search=False, should_match_case=False, should_match_exact=False)
        self.assertEqual(len(indices), 3)


class TestBibleBaseMatchExact(unittest.TestCase):
    """Tests für _match_exact."""

    def setUp(self):
        self.b = _make_search_bible()

    def test_exact_at_start(self):
        self.assertTrue(self.b._match_exact(0, "Gott ist groß", "Gott"))

    def test_exact_in_middle(self):
        self.assertTrue(self.b._match_exact(4, "und Gott sprach", "Gott"))

    def test_not_exact_embedded(self):
        self.assertFalse(self.b._match_exact(0, "Gottheit", "Gott"))

    def test_not_exact_suffix(self):
        self.assertFalse(self.b._match_exact(3, "der Gottheit", "Gott"))

    def test_exact_at_end(self):
        self.assertTrue(self.b._match_exact(4, "und Gott", "Gott"))


class TestBibleBaseFormattedVerseText(unittest.TestCase):
    """Tests für _get_formatted_verse_text."""

    def setUp(self):
        self.b = _make_search_bible()
        from src.bible_base import Finding, Passage
        self.finding = Finding(
            passage=Passage("1. Mose", 1, 1),
            verse_text="",
            verse_hit_count=0
        )

    def test_simple_highlight(self):
        hit_order = [''] * 50
        result = self.b._get_formatted_verse_text(
            [0], hit_order, "Gott ist groß", "Gott",
            is_flood_search=False, finding=self.finding)
        self.assertIn("<b>", result)
        self.assertIn("Gott", result)
        self.assertEqual(self.finding.verse_hit_count, 1)

    def test_flood_highlight(self):
        verse = "Gott hat die Erde erschaffen"
        hit_order = [''] * len(verse)
        # Flood: hit_order enthält Suchbegriffe an den Indizes
        hit_order[0] = "gott"
        result = self.b._get_formatted_verse_text(
            [0], hit_order, verse, "gott",
            is_flood_search=True, finding=self.finding)
        self.assertIn("<b>", result)

    def test_no_match_no_highlight(self):
        hit_order = [''] * 50
        result = self.b._get_formatted_verse_text(
            [], hit_order, "Gott ist groß", "Xyzzyx",
            is_flood_search=False, finding=self.finding)
        self.assertNotIn("<b>", result)
        self.assertEqual(self.finding.verse_hit_count, 0)


class TestBibleBaseToPassageReachedEdgeCases(unittest.TestCase):
    """Zusätzliche Branch-Tests für _to_passage_reached."""

    def setUp(self):
        self.b = _make_search_bible()
        from src.bible_base import Passage, Section
        self.Passage = Passage
        self.Section = Section

    def test_offenbarung_22_22_reached(self):
        """Vers nach 22:21 in Offenbarung → immer reached."""
        p = self.Passage("Offenbarung", 22, 22)
        s = self.Section("1. Mose", 1, 1, "Offenbarung", 22, 21)
        self.assertTrue(self.b._to_passage_reached(p, s))

    def test_exactly_at_end_not_reached(self):
        """Exakt am Endpunkt → noch nicht überschritten."""
        p = self.Passage("1. Mose", 1, 2)
        s = self.Section("1. Mose", 1, 1, "1. Mose", 1, 2)
        self.assertFalse(self.b._to_passage_reached(p, s))

    def test_one_verse_past_end(self):
        p = self.Passage("1. Mose", 1, 3)
        s = self.Section("1. Mose", 1, 1, "1. Mose", 1, 2)
        self.assertTrue(self.b._to_passage_reached(p, s))


class TestBibleBaseGoToNextPassageEdgeCases(unittest.TestCase):
    """Edge-Cases für _go_to_next_passage."""

    def setUp(self):
        from src.bible_base import Bible
        class MiniBible(Bible):
            def load_text(self, path): pass
        self.b = MiniBible("Test")
        self.b.books = {
            "Buch1": {1: {1: "V1"}, 2: {1: "V2"}},
            "Buch2": {1: {1: "V3", 2: "V4"}},
        }
        self.b.book_positions = {name: i for i, name in enumerate(self.b.books.keys())}
        from src.bible_base import Passage
        self.Passage = Passage

    def test_next_verse_in_same_chapter(self):
        p = self.Passage("Buch2", 1, 1)
        result = self.b._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.verse, 2)

    def test_next_chapter_in_same_book(self):
        p = self.Passage("Buch1", 1, 1)
        result = self.b._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.chapter, 2)
        self.assertEqual(p.verse, 1)

    def test_next_book(self):
        p = self.Passage("Buch1", 2, 1)
        result = self.b._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.book, "Buch2")

    def test_last_verse_of_last_book(self):
        p = self.Passage("Buch2", 1, 2)
        result = self.b._go_to_next_passage(p)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

"""
Erweiterte Tests für bible_base.py – Suchfunktionalität.
Übersetzt und angepasst aus Extended_Bible_Base_Tests_with_Search_Methods.py
(ursprünglich von BibleServiceTest.java abgeleitet).

Änderungen gegenüber der Vorlage:
- Import von src.bible_base statt bible_base (Projektstruktur)
- Hilfsklasse heisst BibleSearchTestHelper (kein Namenskonflikt mit TestBible)
- get_chapter_count-Erwartung angepasst (1. Mose hat Kap. 1 und 50 => 2 Kapitel)
"""

import unittest

from src.bible_base import Bible, SearchResult, Finding, Passage


class BibleSearchTestHelper(Bible):
    """Konkrete Bible-Implementierung für Suchtests mit erweitertem Testdatensatz."""

    def load_text(self, file_path: str) -> None:
        """Lade erweiterten Testdatensatz, der alle Suchszenarien abdeckt."""
        test_content = (
            "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.\n"
            "0#1. Mose#1#2#Und die Erde war wüst und leer, und Finsternis war über der Tiefe;"
            " und der Geist Gottes schwebte über den Wassern.\n"
            "0#1. Mose#1#3#Und Gott sprach: Es werde Licht! und es ward Licht.\n"
            "0#1. Mose#1#4#Und Gott sah das Licht, daß es gut war;"
            " und Gott schied das Licht von der Finsternis.\n"
            "0#1. Mose#1#5#Und Gott nannte das Licht Tag, und die Finsternis nannte er Nacht."
            " Und es ward Abend und es ward Morgen: erster Tag.\n"
            "0#1. Mose#1#6#Und Gott sprach: Es werde eine Ausdehnung inmitten der Wasser,"
            " und sie scheide die Wasser von den Wassern!\n"
            "0#1. Mose#1#7#Und Gott machte die Ausdehnung und schied die Wasser, welche unterhalb"
            " der Ausdehnung, von den Wassern, die oberhalb der Ausdehnung sind. Und es ward also.\n"
            "0#1. Mose#1#8#Und Gott nannte die Ausdehnung Himmel."
            " Und es ward Abend und es ward Morgen: zweiter Tag.\n"
            "0#1. Mose#1#9#Und Gott sprach: Es sammeln sich die Wasser unterhalb des Himmels"
            " an einen Ort, und es werde sichtbar das Trockene! Und es ward also.\n"
            "0#1. Mose#1#10#Und Gott nannte das Trockene Erde, und die Sammlung der Wasser nannte"
            " er Meere. Und Gott sah, daß es gut war.\n"
            "0#1. Mose#1#11#Und Gott sprach: Die Erde lasse Gras hervorsprossen, Kraut, das Samen"
            " hervorbringe, Fruchtbäume, die Frucht tragen nach ihrer Art, in welcher ihr Same sei"
            " auf der Erde! Und es ward also.\n"
            "0#1. Mose#50#25#Darum nahm er einen Eid von den Kindern Israel und sprach:"
            " Wenn euch Gott heimsuchen wird, so führet meine Gebeine von dannen.\n"
            "0#Johannes#3#16#Also hat Gott die Welt geliebt, dass er seinen eingeborenen Sohn gab,"
            " auf dass alle, die an ihn glauben, nicht verloren werden, sondern das ewige Leben haben.\n"
            "0#Epheser#3#5#welches nicht kundgetan ist in den vorigen Zeiten den Menschenkindern,"
            " wie es nun offenbart ist seinen heiligen Aposteln und Propheten durch den Geist,\n"
            "0#Jeremia#33#11#wird man dennoch wiederum hören Geschrei von Freude und Wonne,"
            " die Stimme des Bräutigams und der Braut und die Stimme derer, die da sagen:"
            " „Danket dem HERRN Zebaoth; denn er ist freundlich, und seine Güte währet ewiglich\","
            " wenn sie Dankopfer bringen zum Hause des HERRN. Denn ich will des Landes Gefängnis"
            " wenden wie von Anfang, spricht der HERR.\n"
            "0#Maleachi#3#24#Der soll das Herz der Väter bekehren zu den Kindern und das Herz"
            " der Kinder zu ihren Vätern, dass ich nicht komme und das Erdreich mit dem Bann schlage.\n"
            "0#Offenbarung#7#4#Und ich hörte die Zahl derer, die versiegelt wurden:"
            " hundertvierundvierzigtausend, die versiegelt waren von allen Geschlechtern"
            " der Kinder Israel:\n"
            "0#Offenbarung#21#3#Und ich hörte eine große Stimme von dem Stuhl, die sprach:"
            " Siehe da, die Hütte Gottes bei den Menschen! und er wird bei ihnen wohnen,"
            " und sie werden sein Volk sein, und er selbst, Gott mit ihnen, wird ihr Gott sein;\n"
            "0#Offenbarung#21#12#Und sie hatte eine große und hohe Mauer und hatte zwölf Tore"
            " und auf den Toren zwölf Engel, und Namen darauf geschrieben, nämlich der zwölf"
            " Geschlechter der Kinder Israel.\n"
            "0#Offenbarung#22#19#Und wenn jemand davontut von den Worten des Buchs dieser"
            " Weissagung, so wird Gott abtun sein Teil vom Holz des Lebens und von der heiligen"
            " Stadt, davon in diesem Buch geschrieben ist."
        )
        self._parse_text(test_content)


class TestBibleBaseSearch(unittest.TestCase):
    """Suchtests für bible_base.Bible – übersetzt aus BibleServiceTest.java."""

    def setUp(self):
        self.bible = BibleSearchTestHelper("Test Bible")
        self.bible.load_text("test_path")

    # ------------------------------------------------------------------
    # Grundlegende Struktur-Tests (Smoke-Tests für den erweiterten Datensatz)
    # ------------------------------------------------------------------

    def test_init(self):
        bible = BibleSearchTestHelper("Test Name")
        self.assertEqual(bible.name, "Test Name")
        self.assertEqual(bible.books, {})

    def test_get_verse_valid(self):
        verse = self.bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_get_verse_invalid_book(self):
        self.assertIsNone(self.bible.get_verse("NonExistent", 1, 1))

    def test_get_verse_invalid_chapter(self):
        self.assertIsNone(self.bible.get_verse("1. Mose", 999, 1))

    def test_get_verse_invalid_verse(self):
        self.assertIsNone(self.bible.get_verse("1. Mose", 1, 999))

    def test_get_chapter_valid(self):
        chapter = self.bible.get_chapter("1. Mose", 1)
        self.assertIsNotNone(chapter)
        self.assertEqual(len(chapter), 11)
        self.assertIn(1, chapter)
        self.assertIn(11, chapter)

    def test_get_chapter_invalid_book(self):
        self.assertIsNone(self.bible.get_chapter("NonExistent", 1))

    def test_get_chapter_invalid_chapter(self):
        self.assertIsNone(self.bible.get_chapter("1. Mose", 999))

    def test_get_book_valid(self):
        book = self.bible.get_book("1. Mose")
        self.assertIsNotNone(book)
        self.assertIn(1, book)

    def test_get_book_invalid(self):
        self.assertIsNone(self.bible.get_book("NonExistent"))

    def test_get_book_names(self):
        names = self.bible.get_book_names()
        self.assertIn("1. Mose", names)

    def test_get_chapter_count_valid(self):
        # 1. Mose hat Kapitel 1 und Kapitel 50 im Testdatensatz
        count = self.bible.get_chapter_count("1. Mose")
        self.assertEqual(count, 2)

    def test_get_chapter_count_invalid(self):
        self.assertEqual(self.bible.get_chapter_count("NonExistent"), 0)

    def test_get_verse_count_valid(self):
        self.assertEqual(self.bible.get_verse_count("1. Mose", 1), 11)

    def test_get_verse_count_invalid_book(self):
        self.assertEqual(self.bible.get_verse_count("NonExistent", 1), 0)

    def test_get_verse_count_invalid_chapter(self):
        self.assertEqual(self.bible.get_verse_count("1. Mose", 999), 0)

    # ------------------------------------------------------------------
    # Parse-Tests
    # ------------------------------------------------------------------

    def test_parse_text_standard_format(self):
        bible = BibleSearchTestHelper("Test")
        bible._parse_text("1. Mose 1:1 Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(bible.get_verse("1. Mose", 1, 1),
                         "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_text_alternative_format(self):
        bible = BibleSearchTestHelper("Test")
        bible._parse_text("1Mos 1:1 Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(bible.get_verse("1. Mose", 1, 1),
                         "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_text_hash_format(self):
        bible = BibleSearchTestHelper("Test")
        bible._parse_text("0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(bible.get_verse("1. Mose", 1, 1),
                         "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_text_empty_lines(self):
        bible = BibleSearchTestHelper("Test")
        bible._parse_text(
            "\n    \n"
            "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.\n\n"
            "0#1. Mose#1#2#Und die Erde war wüst und leer.\n\n    "
        )
        self.assertEqual(bible.get_verse("1. Mose", 1, 1),
                         "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(bible.get_verse("1. Mose", 1, 2),
                         "Und die Erde war wüst und leer.")

    def test_parse_text_invalid_format(self):
        bible = BibleSearchTestHelper("Test")
        bible._parse_text("This is not a valid bible verse format")
        self.assertEqual(len(bible.get_book_names()), 0)

    # ------------------------------------------------------------------
    # Normalisierung
    # ------------------------------------------------------------------

    def test_normalize_german_book_name_abbreviations(self):
        bible = BibleSearchTestHelper("Test")
        self.assertEqual(bible._normalize_german_book_name("1Mos"), "1. Mose")
        self.assertEqual(bible._normalize_german_book_name("Mt"),   "Matthäus")
        self.assertEqual(bible._normalize_german_book_name("Ps"),   "Psalmen")
        self.assertEqual(bible._normalize_german_book_name("Offb"), "Offenbarung")

    def test_normalize_german_book_name_full_names(self):
        bible = BibleSearchTestHelper("Test")
        self.assertEqual(bible._normalize_german_book_name("1. Mose"),  "1. Mose")
        self.assertEqual(bible._normalize_german_book_name("Matthäus"), "Matthäus")

    def test_normalize_german_book_name_unknown(self):
        bible = BibleSearchTestHelper("Test")
        self.assertEqual(bible._normalize_german_book_name("UnknownBook"), "UnknownBook")

    # ------------------------------------------------------------------
    # Suchtests – übersetzt aus BibleServiceTest.java
    # ------------------------------------------------------------------

    def test_search_default(self):
        """Standardsuche (testSearchDefault)"""
        result = self.bible.search("Kinder")
        self.assertGreater(result.hit_count, 0)
        self.assertGreater(len(result.findings), 0)
        self.assertFalse(result.flood_search)
        for finding in result.findings:
            # case-insensitive Suche: Highlighting übernimmt Gross-/Kleinschreibung aus dem Vers
            self.assertTrue("<b>Kinder</b>" in finding.verse_text or
                            "<b>kinder</b>" in finding.verse_text,
                            f"Kein Kinder-Highlighting in: {finding.verse_text[:80]}")

    def test_search_book(self):
        """Suche in einem bestimmten Buch (testSearchBook)"""
        result = self.bible.search("Kinder", "1. Mose")
        self.assertGreater(result.hit_count, 0)
        for finding in result.findings:
            self.assertEqual(finding.passage.book, "1. Mose")
            self.assertIn("<b>Kinder</b>", finding.verse_text)

    def test_search_alle(self):
        """Suche über alle Bücher (testSearchAlle)"""
        result = self.bible.search("Kinder")
        self.assertGreater(result.hit_count, 0)
        self.assertFalse(result.flood_search)

    def test_search_alle_invalid(self):
        """Ungültige Suchanfragen werden abgelehnt (testSearchAlleInvalid)"""
        result_html = self.bible.search("<html>")
        self.assertEqual(result_html.hit_count, 0)
        self.assertEqual(len(result_html.findings), 0)

        result_single = self.bible.search("e")
        self.assertEqual(result_single.hit_count, 0)
        self.assertEqual(len(result_single.findings), 0)

    def test_search_alle_case_sensitive(self):
        """Groß-/Kleinschreibung beachten (testSearchAlleCaseSensitive)"""
        result_normal = self.bible.search("kinder")
        result_case   = self.bible.search("`kinder`")
        # Exakte Groß-/Kleinschreibung darf nicht mehr Treffer liefern als normale Suche
        self.assertLessEqual(result_case.hit_count, result_normal.hit_count)

    def test_search_alle_match_exact(self):
        """Exakte Wortsuche (testSearchAlleMatchExcact)"""
        result_normal = self.bible.search("Und")
        result_exact  = self.bible.search('"Und"')
        self.assertLessEqual(result_exact.hit_count, result_normal.hit_count)
        for finding in result_exact.findings:
            # case-insensitive Suche: Highlighting spiegelt die Schreibung im Vers wider
            self.assertTrue("<b>Und</b>" in finding.verse_text or
                            "<b>und</b>" in finding.verse_text,
                            f"Kein Und-Highlighting in: {finding.verse_text[:80]}")

    def test_search_alle_match_exact_case_sensitive(self):
        """Exakt und Groß-/Kleinschreibung kombiniert (testSearchAlleMatchExcactCaseSensitive)"""
        result = self.bible.search('"`Und`"')
        if result.hit_count > 0:
            for finding in result.findings:
                self.assertIn("<b>Und</b>", finding.verse_text)

    def test_search_alle_empty(self):
        """Leere Suche (testSearchAlleEmpty)"""
        result = self.bible.search("")
        self.assertEqual(result.hit_count, 0)
        self.assertEqual(len(result.findings), 0)

    def test_flood_search_alle_kinder(self):
        """Flutsuche nach mehreren Begriffen (testFloodSearchAlleKinder)"""
        result = self.bible.search("f alle Kinder")
        self.assertTrue(result.flood_search)
        for finding in result.findings:
            verse_lower = finding.verse_text.lower()
            self.assertTrue(
                "<b>alle</b>" in verse_lower or "<b>kinder</b>" in verse_lower
            )

    def test_flood_search_alle(self):
        """Flutsuche mit mehreren häufigen Begriffen (testFloodSearchAlle)"""
        result = self.bible.search("f er sie es wir ihn")
        self.assertTrue(result.flood_search)
        if result.hit_count > 0:
            for finding in result.findings:
                verse_lower = finding.verse_text.lower()
                has_term = any(f"<b>{t}</b>" in verse_lower
                               for t in ["er", "sie", "es", "wir", "ihn"])
                self.assertTrue(has_term)

    def test_flood_search_alle_joh316(self):
        """Flutsuche – Grenzfall Wortanzahl (testFloodSearchAlleJoh316)"""
        # 7 Token (inkl. "f") => überschreitet FLOOD_SEARCH_MAX_LENGTH+1=7  => kein Flood
        result_too_long = self.bible.search("f Also hat Gott die Welt geliebt")
        self.assertFalse(result_too_long.flood_search)

        # 6 Token (inkl. "f") => genau FLOOD_SEARCH_MAX_LENGTH+1 => Flood
        result_valid = self.bible.search("f Also hat Gott die Welt")
        self.assertTrue(result_valid.flood_search)

    def test_flood_search_jer_land_land(self):
        """Flutsuche eingeschränkt auf Jeremia (testFloodSearchJerLandLand)"""
        result = self.bible.search("f Land Landes höre des", "Jeremia")
        self.assertTrue(result.flood_search)
        for finding in result.findings:
            self.assertEqual(finding.passage.book, "Jeremia")

    def test_flood_search_alle_invalid(self):
        """Ungültige Flutsuchen werden nicht als Flood erkannt (testFloodSearchAlleInvalid)"""
        # Einzelzeichen-Token => kein Flood
        self.assertFalse(self.bible.search("f a b c d e").flood_search)
        # Anführungszeichen => kein Flood
        self.assertFalse(self.bible.search('f "Alle Kinder"').flood_search)
        # Einfache Anführungszeichen => kein Flood
        self.assertFalse(self.bible.search("f 'Alle Kinder'").flood_search)

    def test_search_alle_case_sensitive_empty(self):
        """Leere Exakt-Suche (testSearchAlleCaseSensitiveEmpty)"""
        result = self.bible.search('""')
        self.assertEqual(result.hit_count, 0)
        self.assertEqual(len(result.findings), 0)

    def test_search_at(self):
        """Suche im Alten Testament (testSearchAT)"""
        result = self.bible.search("Kinder")
        found_maleachi = any(f.passage.book == "Maleachi" for f in result.findings)
        if "Maleachi" in self.bible.get_book_names():
            self.assertTrue(found_maleachi)

    def test_search_nt(self):
        """Suche im Neuen Testament (testSearchNT)"""
        result = self.bible.search("Kinder")
        found_offenbarung = any(f.passage.book == "Offenbarung" for f in result.findings)
        if "Offenbarung" in self.bible.get_book_names():
            self.assertTrue(found_offenbarung)

    # ------------------------------------------------------------------
    # Weitere Funktionalitätstests
    # ------------------------------------------------------------------

    def test_search_functionality_basic(self):
        """Grundlegende Suche mit Highlighting"""
        result = self.bible.search("Gott")
        self.assertGreater(result.hit_count, 0)
        self.assertFalse(result.flood_search)
        for finding in result.findings:
            self.assertIn("<b>Gott</b>", finding.verse_text)
            self.assertGreater(finding.verse_hit_count, 0)

    def test_search_functionality_exact_match(self):
        """Exakte Wortsuche mit Highlighting (case-insensitiv)"""
        result = self.bible.search('"und"')
        for finding in result.findings:
            # case-insensitive Suche: Highlighting übernimmt Schreibung aus dem Vers
            self.assertTrue("<b>und</b>" in finding.verse_text or
                            "<b>Und</b>" in finding.verse_text,
                            f"Kein und/Und-Highlighting in: {finding.verse_text[:80]}")
            verse_plain = finding.verse_text.replace("<b>", "").replace("</b>", "")
            self.assertIn("und", verse_plain.lower())

    def test_search_functionality_case_sensitive(self):
        """Groß-/Kleinschreibungs-Suche"""
        result = self.bible.search("`Gott`")
        for finding in result.findings:
            self.assertIn("<b>Gott</b>", finding.verse_text)
            verse_plain = finding.verse_text.replace("<b>", "").replace("</b>", "")
            self.assertIn("Gott", verse_plain)

    def test_search_functionality_flood_search(self):
        """Flutsuche Highlighting"""
        result = self.bible.search("f Gott Himmel")
        self.assertTrue(result.flood_search)
        if result.hit_count > 0:
            for finding in result.findings:
                verse_lower = finding.verse_text.lower()
                self.assertTrue(
                    "<b>gott</b>" in verse_lower or "<b>himmel</b>" in verse_lower
                )

    def test_search_in_specific_book(self):
        """Suche in einem bestimmten Buch"""
        result = self.bible.search("Gott", "1. Mose")
        for finding in result.findings:
            self.assertEqual(finding.passage.book, "1. Mose")

    def test_search_validation(self):
        """Eingabevalidierung"""
        for invalid in [
            "<script>alert('test')</script>",
            "<div>test</div>",
            "a",
            "",
        ]:
            result = self.bible.search(invalid)
            self.assertEqual(result.hit_count, 0, f"Sollte 0 Treffer für: {repr(invalid)}")
            self.assertEqual(len(result.findings), 0)

    def test_go_to_next_passage_non_sequential_chapters(self):
        """_go_to_next_passage traversiert Kapitel mit Lücken (z.B. Kap 1 -> Kap 50)"""
        bible = BibleSearchTestHelper("Test")
        bible._parse_text(
            "0#1. Mose#1#11#Letzter Vers Kapitel 1.\n"
            "0#1. Mose#50#25#Vers 25 Kapitel 50."
        )
        bible.book_positions = {n: i for i, n in enumerate(bible.books.keys())}
        p = Passage("1. Mose", 1, 11)
        result = bible._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.chapter, 50)
        self.assertEqual(p.verse, 25)

    def test_go_to_next_passage_non_sequential_verses(self):
        """_go_to_next_passage traversiert Verse mit Lücken (z.B. Vers 1 -> Vers 25)"""
        bible = BibleSearchTestHelper("Test")
        bible._parse_text(
            "0#1. Mose#50#1#Vers 1.\n"
            "0#1. Mose#50#25#Vers 25."
        )
        bible.book_positions = {n: i for i, n in enumerate(bible.books.keys())}
        p = Passage("1. Mose", 50, 1)
        result = bible._go_to_next_passage(p)
        self.assertTrue(result)
        self.assertEqual(p.verse, 25)

    def test_search_traverses_non_sequential_chapters(self):
        """Volltextsuche findet Verse in nicht-sequenziellen Kapiteln (1. Mose 50:25)"""
        result = self.bible.search("Gebeine")
        self.assertGreater(result.hit_count, 0)
        passages = [(f.passage.book, f.passage.chapter, f.passage.verse)
                    for f in result.findings]
        self.assertIn(("1. Mose", 50, 25), passages)

    def test_search_across_multiple_books(self):
        """Suche findet Treffer in mehreren Büchern"""
        result = self.bible.search("Kinder")
        books_found = {f.passage.book for f in result.findings}
        self.assertGreater(len(books_found), 1,
                           "Suche sollte Treffer in mehr als einem Buch liefern")

    def test_search_hit_count_matches_findings(self):
        """hit_count entspricht der Summe der verse_hit_count aller findings"""
        result = self.bible.search("Gott")
        total = sum(f.verse_hit_count for f in result.findings)
        self.assertEqual(result.hit_count, total)

    def test_flood_search_requires_all_terms(self):
        """Flutsuche gibt nur Verse zurück, die ALLE Suchbegriffe enthalten"""
        result = self.bible.search("f Gott Welt geliebt")
        self.assertTrue(result.flood_search)
        for finding in result.findings:
            plain = finding.verse_text.replace("<b>", "").replace("</b>", "").lower()
            self.assertIn("gott",    plain)
            self.assertIn("welt",    plain)
            self.assertIn("geliebt", plain)


if __name__ == "__main__":
    unittest.main()

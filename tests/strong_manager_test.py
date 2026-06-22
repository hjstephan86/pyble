"""
strong_manager_test.py – Tests für src/strong_manager.py
Ziel: Coverage von 23 % auf ≥ 90 %
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from xml.etree import ElementTree as ET

_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _src not in sys.path:
    sys.path.insert(0, _src)

from strong_manager import (
    StrongManager, StrongEntry, StrongUsage,
    _parse_mscope, BOOK_NUMBER_TO_NAME, BOOK_NUMBER_TO_DISPLAY,
)


# ── Hilfsfunktion: minimales Konkordanz-XML ──────────────────────────────────

def _make_konkordanz_xml(items: list[dict]) -> str:
    """Erzeugt ein minimales Zefania-Konkordanz-XML als String."""
    root = ET.Element("ITEMS")
    for it in items:
        item_el = ET.SubElement(root, "item", id=it["id"])
        ET.SubElement(item_el, "title").text = it.get("title", "")
        para = ET.SubElement(item_el, "paragraph")
        style = ET.SubElement(para, "STYLE")
        style.tail = it.get("tail", " 5 ")
        for desc in it.get("descs", []):
            d = ET.SubElement(item_el, "description")
            ET.SubElement(d, "title").text = desc.get("title", "")
            for mscope in desc.get("mscopes", []):
                ET.SubElement(d, "reflink", mscope=mscope)
    return ET.tostring(root, encoding="unicode")


def _write_xml(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".xml",
                                    delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


# ── _parse_mscope ────────────────────────────────────────────────────────────

class TestParseMscope(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(_parse_mscope("1;1;1"), (1, 1, 1))
        self.assertEqual(_parse_mscope("40;3;16"), (40, 3, 16))

    def test_invalid_not_three_parts(self):
        self.assertIsNone(_parse_mscope("1;1"))
        self.assertIsNone(_parse_mscope(""))
        self.assertIsNone(_parse_mscope("1;1;1;1"))

    def test_invalid_non_numeric(self):
        self.assertIsNone(_parse_mscope("a;b;c"))
        self.assertIsNone(_parse_mscope("1;x;1"))


# ── BOOK_NUMBER_TO_NAME / DISPLAY ────────────────────────────────────────────

class TestBookNumberToName(unittest.TestCase):

    def test_first_book(self):
        self.assertEqual(BOOK_NUMBER_TO_NAME[1], "1. Mose")

    def test_last_book(self):
        self.assertEqual(BOOK_NUMBER_TO_NAME[66], "Offenbarung")

    def test_nt_book(self):
        self.assertEqual(BOOK_NUMBER_TO_NAME[40], "Matthäus")
        self.assertEqual(BOOK_NUMBER_TO_NAME[45], "Römer")

    def test_display_equals_name(self):
        self.assertIs(BOOK_NUMBER_TO_DISPLAY, BOOK_NUMBER_TO_NAME)

    def test_all_66_books_present(self):
        self.assertEqual(len(BOOK_NUMBER_TO_NAME), 66)


# ── StrongManager.load ────────────────────────────────────────────────────────

class TestStrongManagerLoad(unittest.TestCase):

    def setUp(self):
        self.mgr = StrongManager()

    def test_load_missing_konkordanz_prints_warning(self):
        with patch("builtins.print") as mp:
            self.mgr.load(texts_dir="/nonexistent")
        mp.assert_called_once()
        self.assertIn("Warning", str(mp.call_args))

    def test_not_loaded_after_missing_file(self):
        self.mgr.load(texts_dir="/nonexistent")
        self.assertFalse(self.mgr.is_loaded)

    def test_load_minimal_hebrew_entry(self):
        xml = _make_konkordanz_xml([{
            "id": "H1",
            "title": "ab (awb)",
            "tail": " 15 ",
            "descs": [{"title": "Vater, 381", "mscopes": ["1;1;1", "1;1;2"]}],
        }])
        path = _write_xml(xml)
        try:
            with tempfile.TemporaryDirectory() as d:
                sf_dir = os.path.join(d, "sf_konkordanz")
                os.makedirs(sf_dir)
                konkordanz = os.path.join(sf_dir, "konkordanz_fixed.xml")
                with open(konkordanz, "w", encoding="utf-8") as f:
                    f.write(xml)
                with patch("builtins.print"):
                    self.mgr.load(texts_dir=d)
        finally:
            os.unlink(path)

        self.assertTrue(self.mgr.is_loaded)
        entry = self.mgr.lookup_by_number("H1")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.language, "hebrew")
        self.assertEqual(entry.title, "ab (awb)")
        self.assertEqual(entry.total_count, 15)
        self.assertEqual(len(entry.usages), 1)
        self.assertEqual(entry.usages[0].german_word, "Vater")
        self.assertEqual(entry.usages[0].count, 381)

    def test_load_minimal_greek_entry(self):
        xml = _make_konkordanz_xml([{
            "id": "G26",
            "title": "agape",
            "tail": " 10 ",
            "descs": [{"title": "Liebe, 10"}],
        }])
        with tempfile.TemporaryDirectory() as d:
            sf_dir = os.path.join(d, "sf_konkordanz")
            os.makedirs(sf_dir)
            konkordanz = os.path.join(sf_dir, "konkordanz_fixed.xml")
            with open(konkordanz, "w", encoding="utf-8") as f:
                f.write(xml)
            with patch("builtins.print"):
                self.mgr.load(texts_dir=d)

        entry = self.mgr.lookup_by_number("G26")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.language, "greek")

    def test_load_entry_without_id_skipped(self):
        xml = _make_konkordanz_xml([{"id": "", "title": "skip me"}])
        with tempfile.TemporaryDirectory() as d:
            sf_dir = os.path.join(d, "sf_konkordanz")
            os.makedirs(sf_dir)
            konkordanz = os.path.join(sf_dir, "konkordanz_fixed.xml")
            with open(konkordanz, "w", encoding="utf-8") as f:
                f.write(xml)
            with patch("builtins.print"):
                self.mgr.load(texts_dir=d)
        self.assertEqual(len(self.mgr.entries), 0)

    def test_load_entry_desc_without_comma(self):
        """description-Titel ohne Komma-Zahl → count aus reflink-Anzahl."""
        xml = _make_konkordanz_xml([{
            "id": "H2",
            "title": "test",
            "descs": [{"title": "Vater", "mscopes": ["1;1;1", "1;2;3"]}],
        }])
        with tempfile.TemporaryDirectory() as d:
            sf_dir = os.path.join(d, "sf_konkordanz")
            os.makedirs(sf_dir)
            with open(os.path.join(sf_dir, "konkordanz_fixed.xml"),
                      "w", encoding="utf-8") as f:
                f.write(xml)
            with patch("builtins.print"):
                self.mgr.load(texts_dir=d)
        entry = self.mgr.lookup_by_number("H2")
        self.assertEqual(entry.usages[0].count, 2)  # 2 reflinks

    def test_load_invalid_mscope_skipped(self):
        xml = _make_konkordanz_xml([{
            "id": "H3",
            "title": "test",
            "descs": [{"title": "Wort, 1",
                        "mscopes": ["invalid", "1;1;1"]}],
        }])
        with tempfile.TemporaryDirectory() as d:
            sf_dir = os.path.join(d, "sf_konkordanz")
            os.makedirs(sf_dir)
            with open(os.path.join(sf_dir, "konkordanz_fixed.xml"),
                      "w", encoding="utf-8") as f:
                f.write(xml)
            with patch("builtins.print"):
                self.mgr.load(texts_dir=d)
        entry = self.mgr.lookup_by_number("H3")
        self.assertEqual(len(entry.usages[0].refs), 1)  # nur valide ref

    def test_load_with_strongs_xml(self):
        """Wenn strongs_xml existiert, wird _enrich_from_strongs aufgerufen (pass)."""
        xml = _make_konkordanz_xml([{"id": "H1", "title": "test"}])
        with tempfile.TemporaryDirectory() as d:
            sf_dir = os.path.join(d, "sf_konkordanz")
            sf_strongs = os.path.join(d, "sf_strongs")
            os.makedirs(sf_dir); os.makedirs(sf_strongs)
            with open(os.path.join(sf_dir, "konkordanz_fixed.xml"),
                      "w", encoding="utf-8") as f:
                f.write(xml)
            strongs_path = os.path.join(
                sf_strongs,
                "SF_2022-02-27_GER_LUTH1912_(LUTHER_1912_mit_Strongs).xml")
            with open(strongs_path, "w", encoding="utf-8") as f:
                f.write("<root/>")
            with patch("builtins.print"):
                self.mgr.load(texts_dir=d)
        self.assertTrue(self.mgr.is_loaded)


# ── lookup_by_number ─────────────────────────────────────────────────────────

class TestLookupByNumber(unittest.TestCase):

    def setUp(self):
        self.mgr = StrongManager()
        self.mgr.entries["H1"] = StrongEntry("H1", "hebrew", "ab", 15, [])
        self.mgr.entries["G26"] = StrongEntry("G26", "greek", "agape", 10, [])

    def test_lookup_by_full_id(self):
        self.assertIsNotNone(self.mgr.lookup_by_number("H1"))
        self.assertIsNotNone(self.mgr.lookup_by_number("G26"))

    def test_lookup_case_insensitive(self):
        self.assertIsNotNone(self.mgr.lookup_by_number("h1"))
        self.assertIsNotNone(self.mgr.lookup_by_number("g26"))

    def test_lookup_numeric_prefers_hebrew(self):
        result = self.mgr.lookup_by_number("1")
        self.assertIsNotNone(result)
        self.assertEqual(result.strong_id, "H1")

    def test_lookup_numeric_falls_back_to_greek(self):
        result = self.mgr.lookup_by_number("26")
        self.assertIsNotNone(result)

    def test_lookup_nonexistent(self):
        self.assertIsNone(self.mgr.lookup_by_number("H9999"))


# ── search_by_word ────────────────────────────────────────────────────────────

class TestSearchByWord(unittest.TestCase):

    def setUp(self):
        self.mgr = StrongManager()
        self.mgr.entries["H1"] = StrongEntry(
            "H1", "hebrew", "ab",  15,
            [StrongUsage("Vater", 381, []), StrongUsage("Väter", 20, [])])
        self.mgr.entries["H2"] = StrongEntry(
            "H2", "hebrew", "em", 220,
            [StrongUsage("Mutter", 220, [])])
        self.mgr.entries["G3"] = StrongEntry(
            "G3", "greek", "pater", 413,
            [StrongUsage("Vater", 413, [])])

    def test_empty_query_returns_empty(self):
        self.assertEqual(self.mgr.search_by_word(""), [])
        self.assertEqual(self.mgr.search_by_word("   "), [])

    def test_finds_by_german_word(self):
        results = self.mgr.search_by_word("Vater")
        ids = [e.strong_id for e in results]
        self.assertIn("H1", ids)
        self.assertIn("G3", ids)

    def test_filter_by_language_hebrew(self):
        results = self.mgr.search_by_word("Vater", language="hebrew")
        self.assertTrue(all(e.language == "hebrew" for e in results))

    def test_filter_by_language_greek(self):
        results = self.mgr.search_by_word("Vater", language="greek")
        self.assertTrue(all(e.language == "greek" for e in results))

    def test_finds_by_title(self):
        results = self.mgr.search_by_word("pater")
        self.assertTrue(any(e.strong_id == "G3" for e in results))

    def test_partial_match(self):
        results = self.mgr.search_by_word("Vät")
        self.assertTrue(any(e.strong_id == "H1" for e in results))

    def test_no_match(self):
        results = self.mgr.search_by_word("Xyzzyx")
        self.assertEqual(results, [])

    def test_exact_match_ranked_first(self):
        results = self.mgr.search_by_word("Vater")
        # Exakter Treffer soll vor Teiltreffern stehen
        self.assertIn(results[0].strong_id, ["H1", "G3"])


# ── entry_to_dict ─────────────────────────────────────────────────────────────

class TestEntryToDict(unittest.TestCase):

    def setUp(self):
        self.mgr = StrongManager()
        self.entry = StrongEntry(
            strong_id="H1",
            language="hebrew",
            title="ab (awb)",
            total_count=15,
            usages=[
                StrongUsage("Vater", 381, [(1, 1, 1), (40, 3, 16)]),
                StrongUsage("Väter", 20, []),
            ],
            original_word="אָב",
            transliteration="ab",
            pronunciation="awb",
            definition="Vater",
            etymology="primitives Wort",
        )

    def test_basic_fields(self):
        d = self.mgr.entry_to_dict(self.entry)
        self.assertEqual(d["strong_number"], "H1")
        self.assertEqual(d["language"], "hebrew")
        self.assertEqual(d["title"], "ab (awb)")
        self.assertEqual(d["total_count"], 15)
        self.assertEqual(d["original_word"], "אָב")
        self.assertEqual(d["transliteration"], "ab")

    def test_usages_with_refs(self):
        d = self.mgr.entry_to_dict(self.entry, include_refs=True)
        self.assertEqual(len(d["usages"]), 2)
        refs = d["usages"][0]["refs"]
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0]["book_display"], "1. Mose")
        self.assertEqual(refs[0]["book_api"], "1. Mose")
        self.assertEqual(refs[0]["chapter"], 1)
        self.assertEqual(refs[0]["verse"], 1)
        self.assertIn("1. Mose", refs[0]["label"])

    def test_usages_without_refs(self):
        d = self.mgr.entry_to_dict(self.entry, include_refs=False)
        for usage in d["usages"]:
            self.assertEqual(usage["refs"], [])

    def test_translation_field_max_8_words(self):
        entry = StrongEntry(
            "H99", "hebrew", "t", 1,
            [StrongUsage(f"Wort{i}", i, []) for i in range(10)])
        d = self.mgr.entry_to_dict(entry)
        words = d["translation"].split(", ")
        self.assertLessEqual(len(words), 8)

    def test_original_word_fallback_to_title(self):
        entry = StrongEntry("H2", "hebrew", "FallbackTitle", 1, [])
        d = self.mgr.entry_to_dict(entry)
        self.assertEqual(d["original_word"], "FallbackTitle")

    def test_ref_with_unknown_book_number(self):
        entry = StrongEntry(
            "H5", "hebrew", "t", 1,
            [StrongUsage("Test", 1, [(999, 1, 1)])])
        d = self.mgr.entry_to_dict(entry, include_refs=True)
        # Unbekannte Buchnummer → str(999) als Fallback
        self.assertEqual(d["usages"][0]["refs"][0]["book_display"], "999")


# ── is_loaded property ────────────────────────────────────────────────────────

class TestIsLoaded(unittest.TestCase):

    def test_false_initially(self):
        mgr = StrongManager()
        self.assertFalse(mgr.is_loaded)

    def test_true_after_successful_load(self):
        mgr = StrongManager()
        xml = _make_konkordanz_xml([{"id": "H1", "title": "t"}])
        with tempfile.TemporaryDirectory() as d:
            sf_dir = os.path.join(d, "sf_konkordanz")
            os.makedirs(sf_dir)
            with open(os.path.join(sf_dir, "konkordanz_fixed.xml"),
                      "w", encoding="utf-8") as f:
                f.write(xml)
            with patch("builtins.print"):
                mgr.load(texts_dir=d)
        self.assertTrue(mgr.is_loaded)


if __name__ == "__main__":
    unittest.main()

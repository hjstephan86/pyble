"""
Strong-Konkordanz Manager (Zefania XML Format)
Nutzt die SF_2022-02-27 Luther 1912 Konkordanz und Strongs-XML-Dateien.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET


# Buchname-Mapping: Nummer (mscope) → Deutscher Name (Luther 1912)
BOOK_NUMBER_TO_NAME: Dict[int, str] = {
    1: "1. Mose", 2: "2. Mose", 3: "3. Mose", 4: "4. Mose", 5: "5. Mose",
    6: "Josua", 7: "Richter", 8: "Rut", 9: "1. Samuel", 10: "2. Samuel",
    11: "1. Könige", 12: "2. Könige", 13: "1. Chronik", 14: "2. Chronik",
    15: "Esra", 16: "Nehemia", 17: "Ester", 18: "Hiob", 19: "Psalmen",
    20: "Sprüche", 21: "Prediger", 22: "Hohelied", 23: "Jesaja",
    24: "Jeremia", 25: "Klagelieder", 26: "Hesekiel", 27: "Daniel",
    28: "Hosea", 29: "Joel", 30: "Amos", 31: "Obadja", 32: "Jona",
    33: "Micha", 34: "Nahum", 35: "Habakuk", 36: "Zefanja", 37: "Haggai",
    38: "Sacharja", 39: "Maleachi", 40: "Matthäus", 41: "Markus",
    42: "Lukas", 43: "Johannes", 44: "Apostelgeschichte", 45: "Römer",
    46: "1. Korinther", 47: "2. Korinther", 48: "Galater", 49: "Epheser",
    50: "Philipper", 51: "Kolosser", 52: "1. Thessalonicher",
    53: "2. Thessalonicher", 54: "1. Timotheus", 55: "2. Timotheus",
    56: "Titus", 57: "Philemon", 58: "Hebräer", 59: "Jakobus",
    60: "1. Petrus", 61: "2. Petrus", 62: "1. Johannes", 63: "2. Johannes",
    64: "3. Johannes", 65: "Judas", 66: "Offenbarung",
}

# Anzeige-Buchname – identisch mit BOOK_NUMBER_TO_NAME (kanonisch)
BOOK_NUMBER_TO_DISPLAY = BOOK_NUMBER_TO_NAME


@dataclass
class StrongUsage:
    """Eine Übersetzungsvariante mit ihren Bibelreferenzen."""
    german_word: str          # z.B. "Vater"
    count: int                # Anzahl Vorkommen
    refs: List[Tuple[int, int, int]]  # [(book_num, chapter, verse), ...]


@dataclass
class StrongEntry:
    strong_id: str            # z.B. "H1", "G25"
    language: str             # "hebrew" oder "greek"
    title: str                # z.B. "ab (awb)"
    total_count: int          # Gesamtvorkommen in Luther 1912
    usages: List[StrongUsage] # Deutsche Übersetzungsvarianten mit Refs
    # Felder aus altem Strong-System (Fallback wenn SF nicht vorhanden)
    original_word: str = ""
    transliteration: str = ""
    pronunciation: str = ""
    definition: str = ""
    etymology: str = ""
    translation: str = ""


def _parse_mscope(mscope: str) -> Optional[Tuple[int, int, int]]:
    """Parsiert 'book;chapter;verse' aus dem mscope-Attribut."""
    parts = mscope.split(";")
    if len(parts) == 3:
        try:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            pass
    return None


class StrongManager:
    """Lädt und verwaltet die Zefania-Format Strong-Konkordanz."""

    def __init__(self):
        self.entries: Dict[str, StrongEntry] = {}
        self._loaded = False

    def load(self, texts_dir: str = "texts") -> None:
        konkordanz_xml = Path(texts_dir) / "sf_konkordanz" / "konkordanz_fixed.xml"
        strongs_xml    = Path(texts_dir) / "sf_strongs" / "SF_2022-02-27_GER_LUTH1912_(LUTHER_1912_mit_Strongs).xml"

        if not konkordanz_xml.exists():
            print(f"Warning: Konkordanz XML nicht gefunden: {konkordanz_xml}")
            return

        self._load_konkordanz(str(konkordanz_xml))
        if strongs_xml.exists():
            self._enrich_from_strongs(str(strongs_xml))

        self._loaded = True
        h = sum(1 for k in self.entries if k.startswith("H"))
        g = sum(1 for k in self.entries if k.startswith("G"))
        print(f"Loaded SF Strong concordance: {len(self.entries)} entries (H={h}, G={g})")

    def _load_konkordanz(self, file_path: str) -> None:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for item in root.findall("item"):
            sid = (item.get("id") or "").strip().upper()
            if not sid:
                continue

            language = "hebrew" if sid.startswith("H") else "greek"
            title    = (item.findtext("title") or "").strip()

            # Gesamtanzahl steht im tail des <STYLE>-Elements innerhalb von <paragraph>
            total_count = 0
            para_el = item.find("paragraph")
            if para_el is not None:
                style_el = para_el.find("STYLE")
                tail_text = (style_el.tail if style_el is not None else None) or (para_el.text or "")
                m = re.search(r"(\d+)", tail_text)
                if m:
                    total_count = int(m.group(1))

            # Übersetzungsvarianten aus <description>-Tags
            usages: List[StrongUsage] = []
            for desc in item.findall("description"):
                desc_title = (desc.findtext("title") or "").strip()
                # Format: "Vater, 381" oder "Vater"
                word = desc_title
                count = 0
                cm = re.match(r"^(.+),\s*(\d+)$", desc_title)
                if cm:
                    word  = cm.group(1).strip()
                    count = int(cm.group(2))
                else:
                    # Einzelreferenz ohne Komma-Zahl
                    count = len(desc.findall("reflink"))

                refs = []
                for reflink in desc.findall("reflink"):
                    mscope = reflink.get("mscope", "")
                    parsed = _parse_mscope(mscope)
                    if parsed:
                        refs.append(parsed)

                usages.append(StrongUsage(german_word=word, count=count, refs=refs))

            self.entries[sid] = StrongEntry(
                strong_id=sid,
                language=language,
                title=title,
                total_count=total_count,
                usages=usages,
            )

    def _enrich_from_strongs(self, file_path: str) -> None:
        """Lädt zusätzliche Metadaten (Originalwort, Aussprache) aus dem
        Strongs-XML, falls vorhanden – wird nur für die Anzeige genutzt."""
        # Die Strongs-XML enthält keine separaten Strong-Dictionary-Einträge,
        # sondern nur den Bibeltext mit <gr str="...">-Markierungen.
        # Wir können hieraus Originalwörter sammeln, falls gewünscht.
        # Für jetzt reicht die Konkordanz vollständig.
        pass

    # ------------------------------------------------------------------
    # Suche
    # ------------------------------------------------------------------

    def lookup_by_number(self, strong_id: str) -> Optional[StrongEntry]:
        sid = strong_id.strip()
        if sid.isdigit():
            return self.entries.get("H" + sid) or self.entries.get("G" + sid)
        return self.entries.get(sid.upper())

    def search_by_word(self, word: str, language: str = "") -> List[StrongEntry]:
        """Sucht in deutschen Übersetzungsvarianten und Titeln."""
        q = word.strip().lower()
        if not q:
            return []
        results = []
        for entry in self.entries.values():
            if language and entry.language != language.lower():
                continue
            # Nur in Übersetzungsvarianten (german_word) und Titel suchen
            words_haystack = " ".join(u.german_word.lower() for u in entry.usages)
            if q in words_haystack or q in entry.title.lower():
                results.append(entry)

        def rank(e: StrongEntry) -> Tuple[int, int]:
            for u in e.usages:
                if q == u.german_word.lower():
                    return (0, -u.count)
                if q in u.german_word.lower():
                    return (1, -u.count)
            if q in e.title.lower():
                return (2, -e.total_count)
            return (3, -e.total_count)

        results.sort(key=rank)
        return results

    # ------------------------------------------------------------------
    # Serialisierung
    # ------------------------------------------------------------------

    def entry_to_dict(self, entry: StrongEntry, include_refs: bool = True) -> dict:
        usages_out = []
        for u in entry.usages:
            refs_out = []
            if include_refs:
                for (book_num, ch, vs) in u.refs:
                    book_display = BOOK_NUMBER_TO_DISPLAY.get(book_num, str(book_num))
                    book_api    = BOOK_NUMBER_TO_NAME.get(book_num, str(book_num))
                    refs_out.append({
                        "book_display": book_display,
                        "book_api": book_api,
                        "chapter": ch,
                        "verse": vs,
                        "label": f"{book_display} {ch},{vs}"
                    })
            usages_out.append({
                "german_word": u.german_word,
                "count": u.count,
                "refs": refs_out,
            })

        return {
            "strong_number": entry.strong_id,
            "language": entry.language,
            "title": entry.title,
            "total_count": entry.total_count,
            "usages": usages_out,
            # Kompatibilitätsfelder für strong.html
            "original_word": entry.original_word or entry.title,
            "transliteration": entry.transliteration,
            "pronunciation": entry.pronunciation,
            "definition": entry.definition,
            "etymology": entry.etymology,
            "translation": ", ".join(u.german_word for u in entry.usages[:8]),
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded

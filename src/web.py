from bible_base import Bible

# Mapping from the English book titles as they appear in web.txt to the
# canonical German names used by the German translations (Luther, Schlachter,
# Elberfelder). This allows the parallel-view and other pages to request the
# same book across all four translations.
WEB_TO_GERMAN: dict = {
    "Genesis":          "1. Mose",
    "Exodus":           "2. Mose",
    "Leviticus":        "3. Mose",
    "Numbers":          "4. Mose",
    "Deuteronomy":      "5. Mose",
    "Joshua":           "Josua",
    "Judges":           "Richter",
    "Ruth":             "Rut",
    "1 Samuel":         "1. Samuel",
    "2 Samuel":         "2. Samuel",
    "1 Kings":          "1. Könige",
    "2 Kings":          "2. Könige",
    "1 Chronicles":     "1. Chronik",
    "2 Chronicles":     "2. Chronik",
    "Ezra":             "Esra",
    "Nehemiah":         "Nehemia",
    "Esther":           "Ester",
    "Job":              "Hiob",
    "Psalms":           "Psalmen",
    "Proverbs":         "Sprüche",
    "Ecclesiastes":     "Prediger",
    "Song of Solomon":  "Hohelied",
    "Isaiah":           "Jesaja",
    "Jeremiah":         "Jeremia",
    "Lamentations":     "Klagelieder",
    "Ezekiel":          "Hesekiel",
    "Daniel":           "Daniel",
    "Hosea":            "Hosea",
    "Joel":             "Joel",
    "Amos":             "Amos",
    "Obadiah":          "Obadja",
    "Jonah":            "Jona",
    "Micah":            "Micha",
    "Nahum":            "Nahum",
    "Habakkuk":         "Habakuk",
    "Zephaniah":        "Zefanja",
    "Haggai":           "Haggai",
    "Zechariah":        "Sacharja",
    "Malachi":          "Maleachi",
    "Matthew":          "Matthäus",
    "Mark":             "Markus",
    "Luke":             "Lukas",
    "John":             "Johannes",
    "Acts":             "Apostelgeschichte",
    "Romans":           "Römer",
    "1 Corinthians":    "1. Korinther",
    "2 Corinthians":    "2. Korinther",
    "Galatians":        "Galater",
    "Ephesians":        "Epheser",
    "Philippians":      "Philipper",
    "Colossians":       "Kolosser",
    "1 Thessalonians":  "1. Thessalonicher",
    "2 Thessalonians":  "2. Thessalonicher",
    "1 Timothy":        "1. Timotheus",
    "2 Timothy":        "2. Timotheus",
    "Titus":            "Titus",
    "Philemon":         "Philemon",
    "Hebrews":          "Hebräer",
    "James":            "Jakobus",
    "1 Peter":          "1. Petrus",
    "2 Peter":          "2. Petrus",
    "1 John":           "1. Johannes",
    "2 John":           "2. Johannes",
    "3 John":           "3. Johannes",
    "Jude":             "Judas",
    "Revelation":       "Offenbarung",
}


class WorldEnglishBible(Bible):
    """World English Bible Translation"""

    def __init__(self):
        super().__init__("WEB")

    def load_text(self, file_path: str) -> None:
        """Load World English Bible text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self._parse_verse_per_line_format(content)
                self._rename_books_to_german()
        except Exception as e:
            print(f"Error loading World English Bible from {file_path}: {e}")

    def _rename_books_to_german(self) -> None:
        """Rename all English book titles to their German equivalents so that
        /api/WEB/4%20Mose/1 works just like the German translations."""
        new_books = {}
        for eng_name, data in self.books.items():
            german_name = WEB_TO_GERMAN.get(eng_name, eng_name)
            new_books[german_name] = data
        self.books = new_books
    
    def _normalize_english_book_name(self, book_name: str) -> str:
        """Normalize English book names to consistent format"""
        # Common English book name mappings and abbreviations
        name_mappings = {
            "Gen": "Genesis",
            "Exo": "Exodus",
            "Lev": "Leviticus", 
            "Num": "Numbers",
            "Deu": "Deuteronomy",
            "Jos": "Joshua",
            "Jdg": "Judges",
            "Rut": "Ruth",
            "1Sa": "1 Samuel",
            "2Sa": "2 Samuel", 
            "1Ki": "1 Kings",
            "2Ki": "2 Kings",
            "1Ch": "1 Chronicles",
            "2Ch": "2 Chronicles",
            "Ezr": "Ezra",
            "Neh": "Nehemiah",
            "Est": "Esther",
            "Job": "Job",
            "Psa": "Psalms",
            "Pro": "Proverbs",
            "Ecc": "Ecclesiastes",
            "Son": "Song of Solomon",
            "Isa": "Isaiah",
            "Jer": "Jeremiah",
            "Lam": "Lamentations",
            "Eze": "Ezekiel",
            "Dan": "Daniel",
            "Hos": "Hosea",
            "Joe": "Joel",
            "Amo": "Amos",
            "Oba": "Obadiah",
            "Jon": "Jonah",
            "Mic": "Micah",
            "Nah": "Nahum",
            "Hab": "Habakkuk",
            "Zep": "Zephaniah",
            "Hag": "Haggai",
            "Zec": "Zechariah",
            "Mal": "Malachi",
            "Mat": "Matthew",
            "Mar": "Mark",
            "Luk": "Luke",
            "Joh": "John",
            "Act": "Acts",
            "Rom": "Romans",
            "1Co": "1 Corinthians",
            "2Co": "2 Corinthians",
            "Gal": "Galatians",
            "Eph": "Ephesians",
            "Phi": "Philippians",
            "Col": "Colossians",
            "1Th": "1 Thessalonians",
            "2Th": "2 Thessalonians",
            "1Ti": "1 Timothy",
            "2Ti": "2 Timothy",
            "Tit": "Titus",
            "Phm": "Philemon",
            "Heb": "Hebrews",
            "Jas": "James",
            "1Pe": "1 Peter",
            "2Pe": "2 Peter",
            "1Jo": "1 John",
            "2Jo": "2 John",
            "3Jo": "3 John",
            "Jud": "Jude",
            "Rev": "Revelation"
        }
        
        # Also handle full names that might need normalization
        full_name_mappings = {
            "1 Sam": "1 Samuel",
            "2 Sam": "2 Samuel",
            "1 Kin": "1 Kings",
            "2 Kin": "2 Kings", 
            "1 Chr": "1 Chronicles",
            "2 Chr": "2 Chronicles",
            "1 Cor": "1 Corinthians",
            "2 Cor": "2 Corinthians",
            "1 The": "1 Thessalonians",
            "2 The": "2 Thessalonians",
            "1 Tim": "1 Timothy",
            "2 Tim": "2 Timothy",
            "1 Pet": "1 Peter",
            "2 Pet": "2 Peter",
            "1 Joh": "1 John",
            "2 Joh": "2 John",
            "3 Joh": "3 John"
        }
        
        # Try abbreviation mapping first
        if book_name in name_mappings:
            return name_mappings[book_name]
        
        # Try full name mapping
        if book_name in full_name_mappings:
            return full_name_mappings[book_name]
        
        # Return as-is if no mapping found
        return book_name
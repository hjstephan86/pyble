from bible_base import Bible

# Mapping from the French book titles as they appear in segond1910.txt to the
# canonical German names used by the German translations (Luther, Schlachter,
# Elberfelder). This allows the parallel-view and other pages to request the
# same book across all four translations.
SEGOND1910_TO_GERMAN: dict = {
    "Genèse":           "1. Mose",
    "Exode":            "2. Mose",
    "Lévitique":        "3. Mose",
    "Nombres":          "4. Mose",
    "Deutéronome":      "5. Mose",
    "Josué":            "Josua",
    "Juges":            "Richter",
    "Ruth":             "Rut",
    "1 Samuel":         "1. Samuel",
    "2 Samuel":         "2. Samuel",
    "1 Rois":           "1. Könige",
    "2 Rois":           "2. Könige",
    "1 Chroniques":     "1. Chronik",
    "2 Chroniques":     "2. Chronik",
    "Esdras":           "Esra",
    "Néhémie":          "Nehemia",
    "Esther":           "Ester",
    "Job":              "Hiob",
    "Psaumes":          "Psalmen",
    "Proverbes":        "Sprüche",
    "L'Ecclésiaste":    "Prediger",
    "Cantique des Cantiques":  "Hohelied",
    "Ésaïe":            "Jesaja",
    "Jérémie":          "Jeremia",
    "Lamentations":     "Klagelieder",
    "Ézéchiel":         "Hesekiel",
    "Daniel":           "Daniel",
    "Osée":             "Hosea",
    "Joël":             "Joel",
    "Amos":             "Amos",
    "Abdias":           "Obadja",
    "Jonas":            "Jona",
    "Michée":           "Micha",
    "Nahum":            "Nahum",
    "Habacuc":          "Habakuk",
    "Sophonie":         "Zefanja",
    "Aggée":            "Haggai",
    "Zacharie":         "Sacharja",
    "Malachie":         "Maleachi",
    "Matthieu":         "Matthäus",
    "Marc":             "Markus",
    "Luc":              "Lukas",
    "Jean":             "Johannes",
    "Actes":            "Apostelgeschichte",
    "Romains":          "Römer",
    "1 Corinthiens":    "1. Korinther",
    "2 Corinthiens":    "2. Korinther",
    "Galates":          "Galater",
    "Éphésiens":        "Epheser",
    "Philippiens":      "Philipper",
    "Colossiens":       "Kolosser",
    "1 Thessaloniciens":"1. Thessalonicher",
    "2 Thessaloniciens":"2. Thessalonicher",
    "1 Timothée":       "1. Timotheus",
    "2 Timothée":       "2. Timotheus",
    "Tite":             "Titus",
    "Philémon":         "Philemon",
    "Hébreux":          "Hebräer",
    "Jacques":          "Jakobus",
    "1 Pierre":         "1. Petrus",
    "2 Pierre":         "2. Petrus",
    "1 Jean":           "1. Johannes",
    "2 Jean":           "2. Johannes",
    "3 Jean":           "3. Johannes",
    "Jude":             "Judas",
    "Apocalypse":       "Offenbarung",
}


class Segond1910(Bible):
    """Louis Segond 1910 French Bible Translation"""

    def __init__(self):
        super().__init__("Segond 1910")

    def load_text(self, file_path: str) -> None:
        """Load Segond 1910 bible text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Normalize French chapter markers to English for the parser
                content = content.replace("Chapitre", "Chapter")
                content = content.replace("Psaume", "Psalm")
                self._parse_verse_per_line_format(content)
                self._rename_books_to_german()
        except Exception as e:
            print(f"Error loading Segond 1910 from {file_path}: {e}")

    def _rename_books_to_german(self) -> None:
        """Rename all French book titles to their German equivalents so that
        /api/Segond1910/4%20Mose/1 works just like the German translations."""
        new_books = {}
        for fr_name, data in self.books.items():
            german_name = SEGOND1910_TO_GERMAN.get(fr_name, fr_name)
            new_books[german_name] = data
        self.books = new_books

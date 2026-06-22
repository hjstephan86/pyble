from bible_base import Bible


class Schlachter1951(Bible):
    """Schlachter 1951 German Bible Translation"""

    def __init__(self):
        super().__init__("Schlachter 1951")

    def load_text(self, file_path: str) -> None:
        """Load Schlachter 1951 bible text from file.
        Normalisierung der Buchbezeichner übernimmt _parse_verse_per_line_format
        via _apply_book_name_normalization (Bible.BOOK_NAME_MAP).
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self._parse_verse_per_line_format(file.read())
        except Exception as e:
            print(f"Error loading Schlachter 1951 from {file_path}: {e}")

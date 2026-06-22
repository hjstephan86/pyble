import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Passage:
    """A single book/chapter/verse reference"""
    book: str
    chapter: int
    verse: int


@dataclass
class Section:
    """A range of the bible to search in, from one passage to another"""
    book_from: str
    chapter_from: int
    verse_from: int
    book_to: str
    chapter_to: int
    verse_to: int


@dataclass
class Finding:
    """A single search hit: the passage and its (highlighted) verse text"""
    passage: Passage
    verse_text: str
    verse_hit_count: int = 0


@dataclass
class SearchResult:
    """The overall result of a search() call"""
    findings: List[Finding] = field(default_factory=list)
    hit_count: int = 0
    flood_search: bool = False


class Bible(ABC):
    """Abstract base class for Bible translations"""

    # Wrap a search term in double quotes for an exact (whole word) match,
    # e.g. '"Liebe"'. Wrap it in backticks for a case-sensitive search,
    # e.g. '`HERR`'. Both can be combined, e.g. '`"HERR"`'.
    SEARCH_MATCH_EXACT_SYMBOL = '"'
    SEARCH_MATCH_CASE_SYMBOL = '`'

    # "f word1 word2 ..." searches for verses containing ALL of the given
    # words (in any order). Max number of space-separated tokens, including
    # the leading "f".
    FLOOD_SEARCH_MAX_LENGTH = 6

    def __init__(self, name: str):
        self.name = name
        self.books: Dict[str, Dict[int, Dict[int, str]]] = {}
        self.book_positions: Dict[str, int] = {}
    
    @abstractmethod
    def load_text(self, file_path: str) -> None:
        """Load bible text from file - must be implemented by subclasses"""
        pass
    
    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """Get a specific verse"""
        if book in self.books:
            if chapter in self.books[book]:
                if verse in self.books[book][chapter]:
                    return self.books[book][chapter][verse]
        return None
    
    def get_chapter(self, book: str, chapter: int) -> Optional[Dict[int, str]]:
        """Get all verses in a chapter"""
        if book in self.books:
            if chapter in self.books[book]:
                return self.books[book][chapter]
        return None
    
    def get_book(self, book: str) -> Optional[Dict[int, Dict[int, str]]]:
        """Get all chapters in a book"""
        if book in self.books:
            return self.books[book]
        return None
    
    def get_book_names(self) -> List[str]:
        """Get list of all book names"""
        return list(self.books.keys())
    
    def get_chapter_count(self, book: str) -> int:
        """Get number of chapters in a book"""
        if book in self.books:
            return len(self.books[book])
        return 0
    
    def get_verse_count(self, book: str, chapter: int) -> int:
        """Get number of verses in a chapter"""
        if book in self.books and chapter in self.books[book]:
            return len(self.books[book][chapter])
        return 0
    
    def _parse_verse_per_line_format(self, content: str) -> None:
        """Parse the 'verse per line' eBible.org text format used by
        Luther1912, Schlachter1951, Elberfelder1905 and WEB text dumps.

        Layout of these files:

            <Title>

            <copyright notice...>


            <Book Name>

            Kapitel 1 / Chapter 1

            1 Verse text that may
            wrap onto the next line(s)
            2 Next verse text...

            Kapitel 2 / Chapter 2
            ...

            <Next Book Name>

            Kapitel 1 / Chapter 1
            ...
        """
        import re

        chapter_re = re.compile(r'^(?:Kapitel|Chapter|Psalm)\s+(\d+)$')
        verse_re = re.compile(r'^(\d+)\s+(.*)$')
        # Strip pilcrow/paragraph markers some translations insert at the
        # start of a verse (e.g. "1 ¶ Im Anfang ...")
        marker_re = re.compile(r'^[¶\s]+')

        lines = [line.strip() for line in content.split('\n')]
        n = len(lines)

        current_book: Optional[str] = None
        current_chapter: Optional[int] = None
        current_verse: Optional[int] = None
        verse_buffer: List[str] = []

        def flush_verse() -> None:
            if current_verse is not None and current_book is not None and current_chapter is not None:
                text = ' '.join(verse_buffer).strip()
                text = marker_re.sub('', text)
                self.books[current_book][current_chapter][current_verse] = text

        i = 0
        while i < n:
            line = lines[i]

            if not line:
                i += 1
                continue

            chap_match = chapter_re.match(line)
            if chap_match:
                flush_verse()
                verse_buffer = []
                current_verse = None
                current_chapter = int(chap_match.group(1))
                if current_book is not None and current_chapter not in self.books[current_book]:
                    self.books[current_book][current_chapter] = {}
                i += 1
                continue

            # Look ahead: is this line a book title, i.e. is the next
            # non-empty line "Kapitel 1" / "Chapter 1" (the start of a new
            # book)? A "Kapitel N" with N > 1 just continues the current book.
            # This must be checked BEFORE the verse-number check below,
            # since book titles like "2 Mose" or "1 Samuel" would otherwise
            # be mistaken for "verse 2" / "verse 1".
            j = i + 1
            while j < n and not lines[j]:
                j += 1
            next_chap_match = chapter_re.match(lines[j]) if j < n else None
            if next_chap_match and int(next_chap_match.group(1)) == 1:
                flush_verse()
                verse_buffer = []
                current_verse = None
                current_book = line
                if current_book not in self.books:
                    self.books[current_book] = {}
                current_chapter = None
                i += 1
                continue

            verse_match = verse_re.match(line)
            if verse_match and current_book is not None and current_chapter is not None:
                flush_verse()
                current_verse = int(verse_match.group(1))
                verse_buffer = [verse_match.group(2)]
                i += 1
                continue

            # Otherwise: continuation of the current verse's text
            if current_verse is not None:
                verse_buffer.append(line)
            i += 1

        flush_verse()
        self._apply_book_name_normalization()

    def _parse_standard_format(self, content: str) -> None:
        """Parse standard bible format: 'BookName Chapter:Verse Text'"""
        import re
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match verse patterns like "Genesis 1:1" or "1. Mose 1:1"
            verse_match = re.match(r'^(.+?)\s+(\d+):(\d+)\s+(.+)$', line)
            if verse_match:
                book_name = verse_match.group(1).strip()
                chapter_num = int(verse_match.group(2))
                verse_num = int(verse_match.group(3))
                verse_text = verse_match.group(4).strip()
                
                # Initialize book if not exists
                if book_name not in self.books:
                    self.books[book_name] = {}
                
                # Initialize chapter if not exists
                if chapter_num not in self.books[book_name]:
                    self.books[book_name][chapter_num] = {}
                
                # Add verse
                self.books[book_name][chapter_num][verse_num] = verse_text

    def search(self, search_text: str, book: str = None) -> SearchResult:
        """
        Search for text in the bible
        Translated from Java Bible.search() method
        """
        search_result = SearchResult(findings=[], hit_count=0, flood_search=False)

        if not self._is_search_valid(search_text):
            return search_result

        # Build the book-order lookup used by _to_passage_reached()
        self.book_positions = {name: idx for idx, name in enumerate(self.books.keys())}

        # Determine search section
        section = self._get_current_section(book)
        
        # Current passage starts at beginning of section
        current_passage = Passage(
            book=section.book_from,
            chapter=section.chapter_from,
            verse=section.verse_from
        )

        search_text_clean = self._get_search_text(search_text)

        # Determine search type
        should_match_exact = False
        should_match_case = False
        
        if self._is_flood_search(search_text_clean):
            search_result.flood_search = True
        else:
            if self._should_match_exact_and_case(search_text_clean):
                should_match_exact = True
                should_match_case = True
            elif self._should_match_exact(search_text_clean):
                should_match_exact = True
            elif self._should_match_case(search_text_clean):
                should_match_case = True

        # Perform the search
        search_result.hit_count = self._search_impl(
            search_result, section, current_passage, search_text_clean,
            should_match_exact, should_match_case
        )

        return search_result

    def _is_search_valid(self, search_text: str) -> bool:
        """Check if search text is valid (no HTML tags, minimum length)"""
        pattern = re.compile(r'<[^>]+>')
        if pattern.search(search_text):
            return False
        return len(search_text) > 1

    def _is_flood_search(self, search_text: str) -> bool:
        """Check if this is a flood search (multiple terms with 'f ' prefix)"""
        # Exact-match-Wrapper => kein Flood
        if (search_text.lower().startswith(f"f {self.SEARCH_MATCH_EXACT_SYMBOL}") and 
            search_text.lower().endswith(self.SEARCH_MATCH_EXACT_SYMBOL)):
            return False

        # Case-match-Wrapper => kein Flood
        if (search_text.lower().startswith(f"f {self.SEARCH_MATCH_CASE_SYMBOL}") and 
            search_text.lower().endswith(self.SEARCH_MATCH_CASE_SYMBOL)):
            return False

        # Einfache Anführungszeichen als Phrase => kein Flood
        if (search_text.lower().startswith("f '") and
                search_text.endswith("'")):
            return False

        search_text_arr = search_text.split(" ")
        if not (search_text.lower().startswith("f ") and
                len(search_text_arr) > 2 and
                len(search_text_arr) <= self.FLOOD_SEARCH_MAX_LENGTH):
            return False

        for i in range(1, len(search_text_arr)):
            if len(search_text_arr[i]) < 2:
                return False

        return True

    def _should_match_case(self, search_text: str) -> bool:
        """Check if search should match case"""
        return (search_text.startswith(self.SEARCH_MATCH_CASE_SYMBOL) and 
                search_text.endswith(self.SEARCH_MATCH_CASE_SYMBOL) and 
                len(search_text) > 1)

    def _should_match_exact(self, search_text: str) -> bool:
        """Check if search should match exact words"""
        return (search_text.startswith(self.SEARCH_MATCH_EXACT_SYMBOL) and 
                search_text.endswith(self.SEARCH_MATCH_EXACT_SYMBOL) and 
                len(search_text) > 1)

    def _should_match_exact_and_case(self, search_text: str) -> bool:
        """Check if search should match both exact and case"""
        return (((search_text.startswith(self.SEARCH_MATCH_CASE_SYMBOL + self.SEARCH_MATCH_EXACT_SYMBOL) and
                  search_text.endswith(self.SEARCH_MATCH_EXACT_SYMBOL + self.SEARCH_MATCH_CASE_SYMBOL)) or
                 (search_text.startswith(self.SEARCH_MATCH_EXACT_SYMBOL + self.SEARCH_MATCH_CASE_SYMBOL) and
                  search_text.endswith(self.SEARCH_MATCH_CASE_SYMBOL + self.SEARCH_MATCH_EXACT_SYMBOL))) and
                len(search_text) > 3)

    def _get_search_text(self, search: str) -> str:
        """Clean and normalize search text"""
        tokens = search.split()
        return " ".join(tokens)

    def _get_current_section(self, book: str = None) -> Section:
        """Get the section to search in"""
        if book and book in self.books:
            # Search in specific book
            last_chapter = max(self.books[book].keys())
            last_verse = max(self.books[book][last_chapter].keys())
            return Section(
                book_from=book,
                chapter_from=1,
                verse_from=1,
                book_to=book,
                chapter_to=last_chapter,
                verse_to=last_verse
            )
        else:
            # Search in entire bible
            book_names = list(self.books.keys())
            if not book_names:
                return Section("", 1, 1, "", 1, 1)
                
            first_book = book_names[0]
            last_book = book_names[-1]
            
            last_chapter = max(self.books[last_book].keys())
            last_verse = max(self.books[last_book][last_chapter].keys())
            
            return Section(
                book_from=first_book,
                chapter_from=1,
                verse_from=1,
                book_to=last_book,
                chapter_to=last_chapter,
                verse_to=last_verse
            )

    def _search_impl(self, search_result: SearchResult, section: Section, 
                    current_passage: Passage, search_text: str,
                    match_exact: bool, match_case: bool) -> int:
        """Main search implementation"""
        findings = []
        hit_count = 0

        # Clean search text based on flags
        if search_result.flood_search:
            search_text = search_text[2:]  # Remove "f " prefix
        elif match_exact and match_case:
            search_text = search_text[2:-2]  # Remove both symbols
        elif not match_exact and match_case:
            search_text = search_text[1:-1]  # Remove case symbols
        elif match_exact and not match_case:
            search_text = search_text[1:-1]  # Remove exact symbols

        if len(search_text) == 0:
            search_result.findings = findings
            return hit_count

        while True:
            # Get verse text
            verse_text = self.get_verse(
                current_passage.book, 
                current_passage.chapter, 
                current_passage.verse
            )
            
            if verse_text is None:
                break

            # Remove span tags (for Chinese version compatibility)
            verse_text = self._remove_span_tag(verse_text)

            # Find matching indices
            hit_order = [""] * len(verse_text)
            indices = self._get_list_of_matching_indices(
                verse_text, hit_order, search_text,
                search_result.flood_search, match_case, match_exact
            )

            if indices:
                finding = Finding(
                    passage=Passage(
                        current_passage.book,
                        current_passage.chapter,
                        current_passage.verse
                    ),
                    verse_text="",
                    verse_hit_count=0
                )
                
                finding.verse_text = self._get_formatted_verse_text(
                    indices, hit_order, verse_text, search_text,
                    search_result.flood_search, finding
                )
                
                findings.append(finding)
                hit_count += finding.verse_hit_count

            # Move to next passage
            if not self._go_to_next_passage(current_passage):
                break
                
            if self._to_passage_reached(current_passage, section):
                break

        search_result.findings = findings
        return hit_count

    def _remove_span_tag(self, verse_text: str) -> str:
        """Remove span tags from verse text"""
        if verse_text.startswith("<span") and verse_text.endswith("</span>"):
            k = verse_text.find(">")
            if k >= 0:
                verse_text = verse_text[k+1:-7]
        return verse_text

    def _get_list_of_matching_indices(self, verse_text: str, hit_order: List[str],
                                     search_text: str, is_flood_search: bool,
                                     should_match_case: bool, should_match_exact: bool) -> List[int]:
        """Find all matching indices in verse text"""
        indices = []
        
        if is_flood_search:
            search_text_arr = search_text.split(" ")
            verse_text_lower = verse_text.lower()
            
            for search_term in search_text_arr:
                search_term_lower = search_term.lower()
                index = verse_text_lower.find(search_term_lower)
                
                if index < 0:
                    return []  # If any term not found, return empty
                    
                while index >= 0:
                    if index < len(hit_order):
                        hit_order[index] = search_term_lower
                    indices.append(index)
                    index = verse_text_lower.find(search_term_lower, index + 1)
        else:
            search_verse = verse_text if should_match_case else verse_text.lower()
            search_term = search_text if should_match_case else search_text.lower()
            
            index = search_verse.find(search_term)
            while index >= 0:
                if should_match_exact:
                    if self._match_exact(index, search_verse, search_term):
                        indices.append(index)
                else:
                    indices.append(index)
                index = search_verse.find(search_term, index + 1)

        return sorted(set(indices))

    def _match_exact(self, index: int, verse_text: str, search_text: str) -> bool:
        """Check if match is exact (whole word)"""
        char_before = verse_text[index - 1] if index > 0 else ' '
        char_after = verse_text[index + len(search_text)] if (index + len(search_text)) < len(verse_text) else ' '
        
        regex_pattern = r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]'
        
        return ((re.match(regex_pattern, char_before) or char_before == ' ') and
                (re.match(regex_pattern, char_after) or char_after == ' '))

    def _get_formatted_verse_text(self, indices: List[int], hit_order: List[str],
                                 verse_text: str, search_text: str,
                                 is_flood_search: bool, finding: Finding) -> str:
        """Format verse text with highlighting"""
        if is_flood_search:
            verse_hit_count = 0
            result_text = verse_text
            offset = 0
            
            for i in range(len(hit_order)):
                if hit_order[i]:
                    start_pos = i + offset
                    end_pos = start_pos + len(hit_order[i])
                    
                    result_text = (result_text[:start_pos] + 
                                 "<b>" + 
                                 result_text[start_pos:end_pos] + 
                                 "</b>" + 
                                 result_text[end_pos:])
                    
                    offset += 7  # Length of "<b>" + "</b>"
                    verse_hit_count += 1
            
            finding.verse_hit_count = verse_hit_count
        else:
            result_text = verse_text
            offset = 0
            
            for index in indices:
                start_pos = index + offset
                end_pos = start_pos + len(search_text)
                
                result_text = (result_text[:start_pos] + 
                             "<b>" + 
                             result_text[start_pos:end_pos] + 
                             "</b>" + 
                             result_text[end_pos:])
                
                offset += 7  # Length of "<b>" + "</b>"
            
            finding.verse_hit_count = len(indices)

        return result_text

    def _go_to_next_passage(self, current_passage: Passage) -> bool:
        """Move to next verse, chapter, or book (handles non-sequential verse/chapter numbers)"""
        # Check existence
        if current_passage.book not in self.books:
            return False
        if current_passage.chapter not in self.books[current_passage.book]:
            return False

        # Try next verse (handles gaps like verse 11 -> verse 25)
        current_chapter_verses = self.books[current_passage.book][current_passage.chapter]
        next_verses = [v for v in current_chapter_verses if v > current_passage.verse]
        if next_verses:
            current_passage.verse = min(next_verses)
            return True

        # Try next chapter (handles gaps like chapter 1 -> chapter 50)
        remaining_chapters = [c for c in self.books[current_passage.book]
                               if c > current_passage.chapter]
        if remaining_chapters:
            current_passage.chapter = min(remaining_chapters)
            chapter_verses = self.books[current_passage.book][current_passage.chapter]
            if chapter_verses:
                current_passage.verse = min(chapter_verses.keys())
                return True

        # Try next book
        book_names = list(self.books.keys())
        try:
            current_index = book_names.index(current_passage.book)
            if current_index + 1 < len(book_names):
                current_passage.book = book_names[current_index + 1]
                if self.books[current_passage.book]:
                    current_passage.chapter = min(self.books[current_passage.book].keys())
                    chapter_verses = self.books[current_passage.book][current_passage.chapter]
                    if chapter_verses:
                        current_passage.verse = min(chapter_verses.keys())
                        return True
        except ValueError:
            pass

        return False

    def _to_passage_reached(self, current_passage: Passage, section: Section) -> bool:
        """Check if we've reached the end of the search section"""
        current_book_pos = self.book_positions.get(current_passage.book, 0)
        section_book_pos = self.book_positions.get(section.book_to, 0)
        
        # Past the end book
        if current_book_pos > section_book_pos:
            return True
        
        # Same book, past end chapter
        if (current_book_pos == section_book_pos and 
            current_passage.chapter > section.chapter_to):
            return True
        
        # Same book and chapter, past end verse
        if (current_book_pos == section_book_pos and 
            current_passage.chapter == section.chapter_to and 
            current_passage.verse > section.verse_to):
            return True
        
        # Special case: Revelation 22:21 (end of bible)
        if (current_passage.book == "Offenbarung" and 
            current_passage.chapter == 22 and 
            current_passage.verse > 21):
            return True
        
        return False

    def _parse_text(self, content: str) -> None:
        """Parse Elberfelder 1905 specific format"""
        import re

        lines = content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Text format might use German book names like "1. Mose", "2. Mose", etc.
            patterns = [
                # Standard format: "1. Mose 1:1 Am Anfang schuf Gott..."
                r"^(.+?)\s+(\d+):(\d+)\s+(.+)$",
                # Alternative format with book numbers: "1Mos 1:1 Am Anfang..."
                r"^(\w+)\s+(\d+):(\d+)\s+(.+)$",
                # Alternative format: "0#1. Mose#1#1#Am Anfang schuf Gott..."
                r"^\d+#(.+?)#(\d+)#(\d+)#(.+)$",
            ]

            verse_match = None
            for pattern in patterns:
                verse_match = re.match(pattern, line)
                if verse_match:
                    break

            if verse_match:
                book_name = self._normalize_german_book_name(
                    verse_match.group(1).strip()
                )
                chapter_num = int(verse_match.group(2))
                verse_num = int(verse_match.group(3))
                verse_text = verse_match.group(4).strip()

                # Initialize book if not exists
                if book_name not in self.books:
                    self.books[book_name] = {}

                # Initialize chapter if not exists
                if chapter_num not in self.books[book_name]:
                    self.books[book_name][chapter_num] = {}

                # Add verse
                self.books[book_name][chapter_num][verse_num] = verse_text

    # Kanonische Buchbezeichner – werden von allen Übersetzungen verwendet.
    # Schlüssel decken Kurzformen (Luther-Abkürzungen) UND Rohbezeichner
    # aus den eBible-Textdateien ab (z.B. "1 Mose", "Koenige", "Roemers").
    BOOK_NAME_MAP: Dict[str, str] = {
        # ── Kurzformen (Luther-Abkürzungen) ──────────────────────────────
        "1Mos": "1. Mose",       "2Mos": "2. Mose",
        "3Mos": "3. Mose",       "4Mos": "4. Mose",     "5Mos": "5. Mose",
        "Jos": "Josua",          "Ri": "Richter",        "Ruth": "Rut",
        "1Sam": "1. Samuel",     "2Sam": "2. Samuel",
        "1Kön": "1. Könige",     "2Kön": "2. Könige",
        "1Chr": "1. Chronik",    "2Chr": "2. Chronik",
        "Esr": "Esra",           "Neh": "Nehemia",       "Est": "Ester",
        "Hi": "Hiob",            "Ps": "Psalmen",        "Spr": "Sprüche",
        "Pred": "Prediger",      "Hld": "Hohelied",
        "Jes": "Jesaja",         "Jer": "Jeremia",       "Kla": "Klagelieder",
        "Hes": "Hesekiel",       "Dan": "Daniel",        "Hos": "Hosea",
        "Joe": "Joel",           "Am": "Amos",           "Ob": "Obadja",
        "Jon": "Jona",           "Mi": "Micha",          "Nah": "Nahum",
        "Mica": "Micha",
        "Hab": "Habakuk",        "Zef": "Zefanja",       "Hag": "Haggai",
        "Sach": "Sacharja",      "Mal": "Maleachi",
        "Mt": "Matthäus",        "Mk": "Markus",         "Lk": "Lukas",
        "Joh": "Johannes",       "Apg": "Apostelgeschichte",
        "Röm": "Römer",
        "1Kor": "1. Korinther",  "2Kor": "2. Korinther",
        "Gal": "Galater",        "Eph": "Epheser",       "Phil": "Philipper",
        "Kol": "Kolosser",
        "1Thess": "1. Thessalonicher", "2Thess": "2. Thessalonicher",
        "1Tim": "1. Timotheus",  "2Tim": "2. Timotheus",
        "Tit": "Titus",          "Phlm": "Philemon",     "Hebr": "Hebräer",
        "Jak": "Jakobus",
        "1Petr": "1. Petrus",    "2Petr": "2. Petrus",
        "1Joh": "1. Johannes",   "2Joh": "2. Johannes",  "3Joh": "3. Johannes",
        "Jud": "Judas",          "Offb": "Offenbarung",
        # ── Rohbezeichner aus eBible-Textdateien (Elberfelder, Schlachter) ─
        "1 Mose": "1. Mose",     "2 Mose": "2. Mose",
        "3 Mose": "3. Mose",     "4 Mose": "4. Mose",   "5 Mose": "5. Mose",
        "Rut": "Rut",
        "1 Samuel": "1. Samuel", "2 Samuel": "2. Samuel",
        "1 Koenige": "1. Könige","2 Koenige": "2. Könige",
        "1 Chronik": "1. Chronik","2 Chronik": "2. Chronik",
        "Job": "Hiob",
        "Psalm": "Psalmen",
        "Sprueche": "Sprüche",
        "Matthaeus": "Matthäus",
        "Roemers": "Römer",
        "1 Korinther": "1. Korinther", "2 Korinther": "2. Korinther",
        "1 Thessalonicher": "1. Thessalonicher",
        "2 Thessalonicher": "2. Thessalonicher",
        "1 Timotheus": "1. Timotheus", "2 Timotheus": "2. Timotheus",
        "Hebraeer": "Hebräer",
        "1 Petrus": "1. Petrus", "2 Petrus": "2. Petrus",
        "1 Johannes": "1. Johannes","2 Johannes": "2. Johannes",
        "3 Johannes": "3. Johannes",
        "Zephanja": "Zefanja",
        # ── Schlachter-Abkürzungen ────────────────────────────────────────
        "1Mos.": "1. Mose",      "2Mos.": "2. Mose",
        "3Mos.": "3. Mose",      "4Mos.": "4. Mose",    "5Mos.": "5. Mose",
        "1Sam.": "1. Samuel",    "2Sam.": "2. Samuel",
        "1Kön.": "1. Könige",    "2Kön.": "2. Könige",
        "1Chr.": "1. Chronik",   "2Chr.": "2. Chronik",
        "1Kor.": "1. Korinther", "2Kor.": "2. Korinther",
        "1Thess.": "1. Thessalonicher","2Thess.": "2. Thessalonicher",
        "1Tim.": "1. Timotheus", "2Tim.": "2. Timotheus",
        "1Petr.": "1. Petrus",   "2Petr.": "2. Petrus",
        "1Joh.": "1. Johannes",  "2Joh.": "2. Johannes", "3Joh.": "3. Johannes",
    }

    def _normalize_german_book_name(self, book_name: str) -> str:
        """Gibt den kanonischen deutschen Buchnamen zurück.
        Unbekannte Namen werden unverändert zurückgegeben."""
        return self.BOOK_NAME_MAP.get(book_name, book_name)

    def _apply_book_name_normalization(self) -> None:
        """Normalisiert alle Buchschlüssel in self.books nach dem Laden.
        Behält dabei die ursprüngliche Einfügereihenfolge bei.
        Wird von load_text()-Implementierungen aufgerufen."""
        normalized: Dict[str, Dict[int, Dict[int, str]]] = {}
        for raw, data in self.books.items():
            canonical = self._normalize_german_book_name(raw)
            if canonical in normalized:
                for chap, verses in data.items():
                    if chap in normalized[canonical]:
                        normalized[canonical][chap].update(verses)
                    else:
                        normalized[canonical][chap] = verses
            else:
                normalized[canonical] = data
        self.books = normalized
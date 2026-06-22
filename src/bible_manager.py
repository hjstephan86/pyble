from typing import Dict, List, Optional
from pathlib import Path
from bible_base import Bible
from luther1912 import Luther1912
from web import WorldEnglishBible
from schlachter1951 import Schlachter1951
from elberfelder1905 import Elberfelder1905
from segond1910 import Segond1910

class BibleManager:
    """Manages multiple Bible translations"""
    
    def __init__(self):
        self.bibles: Dict[str, Bible] = {}
    
    def load_bibles(self, texts_dir: str = "texts/"):
        """Load all bible texts from directory"""
        texts_path = Path(texts_dir)
        if not texts_path.exists():
            print(f"Warning: Texts directory {texts_dir} not found")
            return
        
        # Map file patterns to bible classes
        bible_mappings = {
            'luther1912': Luther1912,
            'luther': Luther1912,
            'web': WorldEnglishBible,
            'world_english': WorldEnglishBible,
            'schlachter1951': Schlachter1951,
            'schlachter': Schlachter1951,
            'elberfelder1905': Elberfelder1905,
            'elberfelder': Elberfelder1905,
            'segond1910': Segond1910,
            'segond': Segond1910,
        }
        
        for file_path in texts_path.glob("*.txt"):
            filename = file_path.stem.lower()
            
            # Try to match filename to known translations
            bible_class = None
            for pattern, cls in bible_mappings.items():
                if pattern in filename:
                    bible_class = cls
                    break
            
            # If no specific class found, skip or use a generic approach
            if bible_class is None:
                print(f"Warning: No specific parser found for {filename}, skipping")
                continue
            
            # Create and load bible
            bible = bible_class()
            bible.load_text(str(file_path))
            
            if bible.books:  # Only add if successfully loaded
                self.bibles[bible.name.upper()] = bible
                print(f"Loaded {bible.name} with {len(bible.books)} books")
            else:
                print(f"Warning: No content loaded from {filename}")
    
    def get_bible(self, translation: str) -> Optional[Bible]:
        """Get a specific bible translation (case-insensitive), O(1)."""
        return self.bibles.get(translation.upper())

    def get_translation_names(self) -> List[str]:
        """Get list of available translations (original display names)."""
        return [bible.name for bible in self.bibles.values()]
        
    def search_bible(self, query: str, translation: str = None, book: str = None) -> Dict:
        """
        Search for text in one or all bible translations
        
        Args:
            query: Search text
            translation: Specific translation to search (if None, search all)
            book: Specific book to search (if None, search entire bible)
            
        Returns:
            Dictionary with search results
        """
        all_results = []
        total_hits = 0

        if translation:
            # Search in specific translation
            bible = self.get_bible(translation)
            if bible:
                search_result = bible.search(query, book)
                for finding in search_result.findings:
                    all_results.append({
                        "book": finding.passage.book,
                        "chapter": finding.passage.chapter,
                        "verse": finding.passage.verse,
                        "text": finding.verse_text,
                        "translation": bible.name,
                        "hit_count": finding.verse_hit_count
                    })
                total_hits += search_result.hit_count
        else:
            # Search in all translations
            for bible_name, bible in self.bibles.items():
                search_result = bible.search(query, book)
                for finding in search_result.findings:
                    all_results.append({
                        "book": finding.passage.book,
                        "chapter": finding.passage.chapter,
                        "verse": finding.passage.verse,
                        "text": finding.verse_text,
                        "translation": bible.name,
                        "hit_count": finding.verse_hit_count
                    })
                total_hits += search_result.hit_count

        return {
            "results": all_results,
            "total": total_hits,
            "query": query,
            "translation": translation,
            "book": book
        }
import re
import logging
from collections import Counter
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional
from models import VerseResponse, ChapterResponse, BookResponse, BibleListResponse
from bible_manager import BibleManager
from strong_manager import StrongManager

logger = logging.getLogger(__name__)

bible_manager = BibleManager()
strong_manager = StrongManager()

IGNORE_WORDS_DE: set = set()
IGNORE_WORDS_EN: set = set()

# Übersetzungen, die Englisch verwenden
ENGLISH_TRANSLATIONS = {"WEB", "KJV", "KJV1611", "NKJV", "NIV", "ESV"}


def load_ignore_words(file_path: str = "ignore_words_de.txt") -> set:
    """Lädt die Liste der zu ignorierenden (Füll-)Wörter aus einer Textdatei."""
    words = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                words.add(line.lower())
    except FileNotFoundError:
        print(f"Warning: Ignore word list {file_path} not found")
    return words


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup- und Shutdown-Logik via lifespan context manager."""
    global IGNORE_WORDS_DE, IGNORE_WORDS_EN
    bible_manager.load_bibles()
    strong_manager.load()
    IGNORE_WORDS_DE = load_ignore_words("ignore_words_de.txt")
    IGNORE_WORDS_EN = load_ignore_words("ignore_words_en.txt")
    print(f"Loaded {len(IGNORE_WORDS_DE)} ignore words (DE), {len(IGNORE_WORDS_EN)} (EN)")
    yield
    # Hier könnten Shutdown-Aufräumarbeiten stehen


# Initialize FastAPI app
app = FastAPI(
    title="Bible API",
    description="REST API for reading Bible texts across different translations",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Web Interface Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML interface"""
    translations = bible_manager.get_translation_names()
    return templates.TemplateResponse(request, "home.html", {
        "translations": translations
    })

@app.get("/home.html", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/read.html", response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse(request, "read.html")
    
@app.get("/read", response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse(request, "read.html")

@app.get("/search.html", response_class=HTMLResponse)
async def search_page(request: Request):
    return templates.TemplateResponse(request, "search.html")

@app.get("/count.html", response_class=HTMLResponse)
async def count_page(request: Request):
    return templates.TemplateResponse(request, "count.html")

@app.get("/strong.html", response_class=HTMLResponse)
async def strong_page(request: Request):
    return templates.TemplateResponse(request, "strong.html")

@app.get("/parallel.html", response_class=HTMLResponse)
async def parallel_page(request: Request):
    return templates.TemplateResponse(request, "parallel.html")

@app.get("/about.html", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse(request, "about.html")
    
# API Endpoints
@app.get("/api/translations", response_model=BibleListResponse)
async def list_translations():
    """Get list of available Bible translations"""
    return BibleListResponse(translations=bible_manager.get_translation_names())

@app.get("/api/{translation}/books")
async def get_books(translation: str):
    """Get list of books for a specific translation"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    books = []
    for book_name in bible.get_book_names():
        books.append({
            "name": book_name,
            "chapters": bible.get_chapter_count(book_name)
        })
    
    return {"translation": translation, "books": books}

@app.get("/api/strong/number/{strong_id}")
async def get_strong_by_number(strong_id: str):
    """Nachschlagen eines Strong-Eintrags per Nummer, z.B. H1, G25, 430"""
    if not strong_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Strong-Konkordanz noch nicht geladen")

    entry = strong_manager.lookup_by_number(strong_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Strong-Nummer '{strong_id}' nicht gefunden")

    return strong_manager.entry_to_dict(entry)


@app.get("/api/strong/word")
async def search_strong_by_word(word: str, language: str = ""):
    """
    Suche nach einem Wort in der Strong-Konkordanz.
    language: 'hebrew', 'greek' oder '' (beide)
    """
    if not strong_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Strong-Konkordanz noch nicht geladen")

    if not word or len(word.strip()) < 2:
        raise HTTPException(status_code=400, detail="Suchbegriff muss mindestens 2 Zeichen lang sein")

    results = strong_manager.search_by_word(word.strip(), language)

    return {
        "query": word,
        "language": language or "all",
        "total": len(results),
        "results": [strong_manager.entry_to_dict(e) for e in results[:50]],
    }


@app.get("/api/{translation}/{book}")
async def get_book(translation: str, book: str):
    """Get entire book with all chapters and verses"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    book_data = bible.get_book(book)
    if book_data is None:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found in {translation}")
    
    return BookResponse(
        book=book,
        chapters=book_data,
        translation=translation
    )

@app.get("/api/{translation}/{book}/{chapter:int}")
async def get_chapter(translation: str, book: str, chapter: int):
    """Get specific chapter with all verses"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    chapter_data = bible.get_chapter(book, chapter)
    if chapter_data is None:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter} not found in {book} ({translation})")
    
    return ChapterResponse(
        book=book,
        chapter=chapter,
        verses=chapter_data,
        translation=translation
    )

@app.get("/api/{translation}/{book}/{chapter:int}/{verse:int}")
async def get_verse(translation: str, book: str, chapter: int, verse: int):
    """Get specific verse"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    verse_text = bible.get_verse(book, chapter, verse)
    if verse_text is None:
        raise HTTPException(status_code=404, detail=f"Verse {verse} not found in {book} {chapter} ({translation})")
    
    return VerseResponse(
        book=book,
        chapter=chapter,
        verse=verse,
        text=verse_text,
        translation=translation
    )

@app.get("/api/{translation}/{book}/chapters")
async def get_chapter_list(translation: str, book: str):
    """Get list of chapters in a book"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    if book not in bible.books:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found in {translation}")
    
    chapters = []
    for chapter_num in sorted(bible.books[book].keys()):
        chapters.append({
            "chapter": chapter_num,
            "verses": bible.get_verse_count(book, chapter_num)
        })
    
    return {"translation": translation, "book": book, "chapters": chapters}

@app.get("/api/{translation}/{book}/chapter-count")
async def get_chapter_count(translation: str, book: str):
    """Get number of chapters in a book (used by count.html)"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")

    if book not in bible.books:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found in {translation}")

    return {"translation": translation, "book": book, "chapters": bible.get_chapter_count(book)}


@app.get("/api/{translation}/{book}/{chapter:int}/verse-count")
async def get_verse_count(translation: str, book: str, chapter: int):
    """Get number of verses in a chapter (used by count.html)"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")

    if book not in bible.books or chapter not in bible.books[book]:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter} not found in {book} ({translation})")

    return {
        "translation": translation,
        "book": book,
        "chapter": chapter,
        "verses": bible.get_verse_count(book, chapter)
    }


@app.get("/api/search")
async def search_bible(
    q: str,
    translation: str = None,
    book: str = None,
    page: int = 1,
    limit: int = 20,
):
    """Search for verses containing the query string"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Search query must be at least 2 characters long"
        )

    search_results = bible_manager.search_bible(
        query=q.strip(),
        translation=translation,
        book=book,
    )

    start_index = (page - 1) * limit
    end_index   = start_index + limit

    return {
        "results": search_results["results"][start_index:end_index],
        "total":   search_results["total"],
        "page":    page,
        "limit":   limit,
        "query":   q,
        "translation": translation,
        "book":    book,
    }
        
@app.get("/api/count")
async def count_words(
    translation: str,
    book_from: str,
    chapter_from: int,
    verse_from: int,
    book_to: str,
    chapter_to: int,
    verse_to: int,
):
    """Count word frequencies in a range from (book_from, chapter_from, verse_from)
    to (book_to, chapter_to, verse_to), inclusive. Used by count.html."""
    # Browser-Formulare kodieren Leerzeichen als '+' (application/x-www-form-urlencoded).
    # FastAPI dekodiert '%20' automatisch, aber nicht '+' in Query-Strings → hier normalisieren.
    translation = translation.replace("+", " ")
    book_from   = book_from.replace("+", " ")
    book_to     = book_to.replace("+", " ")

    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")

    book_names = list(bible.books.keys())
    if book_from not in book_names:
        raise HTTPException(status_code=404, detail=f"Book '{book_from}' not found in {translation}")
    if book_to not in book_names:
        raise HTTPException(status_code=404, detail=f"Book '{book_to}' not found in {translation}")

    start_idx = book_names.index(book_from)
    end_idx = book_names.index(book_to)

    if (start_idx, chapter_from, verse_from) > (end_idx, chapter_to, verse_to):
        raise HTTPException(status_code=400, detail="Startposition liegt hinter der Endposition")

    word_re = re.compile(r"[A-Za-zÄÖÜäöüßẞ]{2,}")
    counts: Counter = Counter()

    for idx in range(start_idx, end_idx + 1):
        book_name = book_names[idx]
        chapters = bible.books[book_name]
        for chapter_num in sorted(chapters.keys()):
            verses = chapters[chapter_num]
            for verse_num in sorted(verses.keys()):
                if idx == start_idx and (chapter_num, verse_num) < (chapter_from, verse_from):
                    continue
                if idx == end_idx and (chapter_num, verse_num) > (chapter_to, verse_to):
                    continue
                for word in word_re.findall(verses[verse_num]):
                    counts[word.lower()] += 1

    # Ignore-Liste passend zur Übersetzungssprache wählen
    ignore_list = (
        IGNORE_WORDS_EN
        if translation.upper() in ENGLISH_TRANSLATIONS
        else IGNORE_WORDS_DE
    )

    counted_words = []
    ignored_words = []
    for word, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        entry = {"word": word, "count": count}
        if word in ignore_list:
            ignored_words.append(entry)
        else:
            counted_words.append(entry)

    return {
        "section": {
            "book_from": book_from,
            "chapter_from": chapter_from,
            "verse_from": verse_from,
            "book_to": book_to,
            "chapter_to": chapter_to,
            "verse_to": verse_to,
        },
        "total_unique_words": len(counted_words) + len(ignored_words),
        "summary": {
            "total_counted": len(counted_words),
            "total_ignored": len(ignored_words),
        },
        "counted_words": counted_words,
        "ignored_words": ignored_words,
    }
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from pydantic import BaseModel
from typing import Dict, List

class VerseResponse(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str
    translation: str

class ChapterResponse(BaseModel):
    book: str
    chapter: int
    verses: Dict[int, str]
    translation: str

class BookResponse(BaseModel):
    book: str
    chapters: Dict[int, Dict[int, str]]
    translation: str

class BibleListResponse(BaseModel):
    translations: List[str]
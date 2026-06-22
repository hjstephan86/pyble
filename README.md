# pyble – Bible Reader FastAPI Application

Eine FastAPI-Webanwendung zum Lesen von Bibeltexten in mehreren Übersetzungen.

## Projektstruktur

```
pyble/
├── pyproject.toml                   # Projektkonfiguration & Abhängigkeiten
├── conftest.py                      # Server-Fixture für Playwright-Tests
├── src/
│   ├── main.py                      # FastAPI-Einstiegspunkt
│   ├── models.py                    # Pydantic-Datenmodelle
│   ├── bible_base.py                # Abstrakte Basisklasse (inkl. Suchfunktion, Buchbezeichner-Normalisierung)
│   ├── bible_manager.py             # Verwaltet alle geladenen Übersetzungen
│   ├── luther1912.py                # Lutherbibel 1912
│   ├── schlachter1951.py            # Schlachter 1951
│   ├── elberfelder1905.py           # Elberfelder 1905
│   ├── web.py                       # World English Bible
│   ├── strong_manager.py            # Strong-Konkordanz
│   ├── setup-konkordanz.py          # Hilfsskript: Konkordanz aufbereiten
│   ├── ignore_words_de.txt          # Füllwörter für Wortzählung (Deutsch)
│   ├── ignore_words_en.txt          # Füllwörter für Wortzählung (Englisch)
│   ├── templates/                   # HTML-Vorlagen (Jinja2)
│   │   ├── base.html                # Gemeinsames Basis-Template (Nav, CSS)
│   │   ├── home.html
│   │   ├── read.html
│   │   ├── search.html
│   │   ├── count.html
│   │   ├── strong.html
│   │   ├── parallel.html
│   │   └── about.html
│   ├── static/                      # Statische Dateien
│   │   ├── base.css                 # Gemeinsames Stylesheet
│   │   └── favicon.ico
│   └── texts/                       # Bibeltextdateien
│       ├── luther1912.txt
│       ├── schlachter1951.txt
│       ├── elberfelder1905.txt
│       ├── web.txt
│       ├── strong/                  # Strong-Wörterbücher (Hebräisch/Griechisch)
│       ├── sf_strongs/              # Strongs-Nummern für Luther 1912
│       └── sf_konkordanz/           # Konkordanz-Daten
├── tests/
│   ├── bible_base_test.py           # Unit-Tests: Basisklasse & Lücken
│   ├── bible_base_search_test.py    # Unit-Tests: Suchfunktion
│   ├── bible_manager_test.py        # Unit-Tests: BibleManager & Suche
│   ├── elberfelder1905_test.py      # Unit-Tests: Elberfelder 1905
│   ├── luther1912_test.py           # Unit-Tests: Luther 1912
│   ├── schlachter1951_test.py       # Unit-Tests: Schlachter 1951
│   ├── web_test.py                  # Unit-Tests: World English Bible
│   ├── models_test.py               # Unit-Tests: Pydantic-Modelle
│   ├── main_test.py                 # Unit-Tests: FastAPI-Routen & API-Abdeckung
│   ├── strong_manager_test.py       # Unit-Tests: StrongManager
│   └── test_ui_playwright.py        # UI-Tests: alle Templates (Browser)
└── doc/
    ├── coverage/                    # HTML-Coverage-Report (wird automatisch erzeugt)
    └── uml/                         # UML-Diagramme (packages, classes)
```

## Installation

### Voraussetzungen

- Python 3.11 oder neuer

### Projekt installieren

```bash
# Produktionsabhängigkeiten
pip install .

# Inklusive Entwicklungs- und Testwerkzeuge
pip install ".[dev]"
```

Die `requirements.txt` wird nicht mehr benötigt. Alle Abhängigkeiten sind in `pyproject.toml` definiert.

### Browser für Playwright installieren

Nach der Installation der Entwicklungsabhängigkeiten müssen die Browser-Binaries einmalig heruntergeladen werden:

```bash
playwright install chromium
```

## Anwendung starten

```bash
cd src
uvicorn main:app --reload
```

Die Anwendung ist dann erreichbar unter:

- **Web-Oberfläche**: http://localhost:8000
- **API-Dokumentation (Swagger)**: http://localhost:8000/docs
- **API-Dokumentation (ReDoc)**: http://localhost:8000/redoc

### Windows (PowerShell)

```powershell
PS P:\Git\pyble> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
PS P:\Git\pyble> .\venv\Scripts\activate
(venv) PS P:\Git\pyble> cd .\src\
(venv) PS P:\Git\pyble\src> uvicorn main:app --reload
INFO:     Will watch for changes in these directories: ['P:\\Git\\pyble\\src']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [17496] using WatchFiles
INFO:     Started server process [5232]
INFO:     Waiting for application startup.
Loaded Elberfelder1905 with 66 books
Loaded Luther1912 with 66 books
Loaded Schlachter1951 with 66 books
Loaded WEB with 66 books
Loaded SF Strong concordance: 14176 entries (H=8661, G=5515)
Loaded 265 ignore words (DE), 187 (EN)
INFO:     Application startup complete.
INFO:     127.0.0.1:63900 - "GET / HTTP/1.1" 200 OK
```

## Tests ausführen

```bash
pytest -p no:cacheprovider
```

pytest liest die Konfiguration aus `pyproject.toml` und führt automatisch alle Tests aus `tests/` aus.
Gleichzeitig wird ein Code-Coverage-Report erzeugt.

> **Hinweis für Netzlaufwerke (Windows):** Der `-p no:cacheprovider`-Schalter verhindert Fehler beim
> Anlegen des pytest-Cache auf gemappten Netzlaufwerken. Er kann dauerhaft in `pyproject.toml`
> unter `addopts` eingetragen werden.

Die Testsuite umfasst zwei Arten von Tests:

**Unit-Tests** testen die Python-Klassen direkt ohne laufenden Server.

**UI-Tests** (`test_ui_playwright.py`) starten automatisch einen lokalen uvicorn-Server im Hintergrund
und fahren einen Chromium-Browser headless. Die 102 Tests decken alle 7 Templates sowie sämtliche
API-Endpunkte ab:

| Testklasse | Tests | Abgedeckte Bereiche |
|---|---|---|
| `TestNavigation` | 12 | Alle HTML-Routen, Navigationsleiste, Links |
| `TestAPI` | 25 | Alle REST-Endpunkte, 404/400-Fehler, Pagination |
| `TestHomeTemplate` | 5 | Titel, Hero-Section, CTA-Links |
| `TestReadTemplate` | 9 | Übersetzungs-/Buch-/Kapitelauswahl |
| `TestSearchTemplate` | 11 | Suche, Exact-/Flood-Syntax, XSS-Schutz |
| `TestCountTemplate` | 9 | Wortfrequenz-Formular, API-Zählung |
| `TestStrongTemplate` | 12 | Tab-Wechsel, Hebräisch/Griechisch, Wort-Suche |
| `TestParallelTemplate` | 8 | Parallelansicht, Mehrfach-Übersetzungen |
| `TestAboutTemplate` | 5 | Inhalt, Titel, Navigation |
| `TestResponsiveness` | 6 | Mobile-Ansicht, Burger-Menü, Desktop |  

Ausführung (ohne Code Coverage):

```bash
pytest tests/test_ui_playwright.py --no-cov
```

Mit sichtbarem Browserfenster (zur Fehlersuche):

```bash
pytest tests/test_ui_playwright.py --headed
```

Nur Unit-Tests (ohne Server-Start, schnell):

```bash
pytest --ignore=tests/test_ui_playwright.py -p no:cacheprovider
```

### Coverage-Report

Nach dem Testlauf liegt der HTML-Report unter:

```
doc/coverage/index.html
```

Im Terminal erscheint zusätzlich eine kompakte Übersicht der nicht abgedeckten Zeilen.

## UML-Diagramme

Voraussetzung: Graphviz installiert (z.B. nach `C:\Users\...\Graphviz-15.0.0-win32\`).

```powershell
mkdir doc\uml
pyreverse -o dot -p pyble src\ --output-directory doc\uml
```

### Paketdiagramm

```powershell
C:\Users\...\Graphviz-15.0.0-win32\bin\dot.exe -Tsvg doc\uml\packages_pyble.dot -o doc\uml\packages_pyble.svg
C:\Users\...\Graphviz-15.0.0-win32\bin\dot.exe -Tpdf doc\uml\packages_pyble.dot -o doc\uml\packages_pyble.pdf
```

### Klassendiagramm

```powershell
C:\Users\...\Graphviz-15.0.0-win32\bin\fdp.exe -Tsvg doc\uml\classes_pyble.dot -o doc\uml\classes_pyble.svg
C:\Users\...\Graphviz-15.0.0-win32\bin\fdp.exe -Tpdf doc\uml\classes_pyble.dot -o doc\uml\classes_pyble.pdf
```

`fdp` erzeugt ein kräftebasiertes Layout, das die Klassen gleichmäßiger verteilt als das Standard-`dot`-Layout.

## API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `GET` | `/` | Web-Oberfläche |
| `GET` | `/api/translations` | Verfügbare Übersetzungen |
| `GET` | `/api/{translation}/books` | Bücher einer Übersetzung |
| `GET` | `/api/{translation}/{book}` | Gesamtes Buch |
| `GET` | `/api/{translation}/{book}/{chapter}` | Kapitel mit Versen |
| `GET` | `/api/{translation}/{book}/{chapter}/{verse}` | Einzelner Vers |
| `GET` | `/api/{translation}/{book}/chapters` | Kapitelübersicht |
| `GET` | `/api/{translation}/{book}/chapter-count` | Kapitelanzahl |
| `GET` | `/api/{translation}/{book}/{chapter}/verse-count` | Versanzahl |
| `GET` | `/api/search` | Volltext-Suche |
| `GET` | `/api/count` | Wortfrequenz-Zählung |
| `GET` | `/api/strong/number/{id}` | Strong-Nummer nachschlagen |
| `GET` | `/api/strong/word` | Strong-Wort suchen |

## Übersetzungen erweitern

1. Neue Datei anlegen, z.B. `src/kjv.py`
2. Von `Bible` ableiten und `load_text()` implementieren
3. Klasse in `bible_manager.py` registrieren
4. Textdatei nach `src/texts/` legen

```python
from bible_base import Bible

class KJV(Bible):
    def __init__(self):
        super().__init__("KJV")

    def load_text(self, file_path: str) -> None:
        with open(file_path, encoding="utf-8") as f:
            self._parse_verse_per_line_format(f.read())
```

Die Buchbezeichner-Normalisierung (z.B. `"1 Mose"` → `"1. Mose"`) erfolgt automatisch über
`Bible.BOOK_NAME_MAP` am Ende von `_parse_verse_per_line_format`.

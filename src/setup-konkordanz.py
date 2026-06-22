"""
Einmalig auszuführendes Setup-Skript.
Repariert die SF-Konkordanz-XML (fehlende </item>-Tags) und legt
die korrigierte Datei als texts/sf_konkordanz/konkordanz_fixed.xml ab.

Aufruf (einmalig, aus dem src/-Verzeichnis):
    python setup_konkordanz.py
"""
import re
import sys
from pathlib import Path

SRC_DIR  = Path("texts/sf_konkordanz")
OUT_FILE = Path("texts/sf_konkordanz/konkordanz_fixed.xml")


def main():
    # Quelldatei finden: erste XML in texts/sf_konkordanz/ die NICHT die fixed-Version ist
    if not SRC_DIR.exists():
        print(f"FEHLER: Ordner nicht gefunden: {SRC_DIR}")
        print("Bitte die Konkordanz-XML in texts/sf_konkordanz/ ablegen.")
        sys.exit(1)

    candidates = [
        p for p in SRC_DIR.glob("*.xml")
        if p.name != "konkordanz_fixed.xml"
    ]
    if not candidates:
        print(f"FEHLER: Keine XML-Quelldatei in {SRC_DIR} gefunden.")
        print("Bitte die Konkordanz-XML (aus dem Konkordanz-ZIP) in texts/sf_konkordanz/ ablegen.")
        sys.exit(1)

    src = candidates[0]
    print(f"Quelle: {src} ({src.stat().st_size // 1024} KB)")

    print("Lese Datei …")
    content = src.read_text(encoding="utf-8")

    # Zähle offene/geschlossene <item>-Tags
    open_count  = content.count("<item ")
    close_count = content.count("</item>")
    print(f"  <item>-Tags: {open_count} offen, {close_count} geschlossen")

    if close_count == 0:
        print("Repariere: füge </item> vor jedem <item> und vor </dictionary> ein …")
        # </item> vor jedem <item id="..."> einfügen
        fixed = re.sub(r"(<item id=)", r"</item>\n\1", content)
        # Erstes fälschlicherweise eingefügtes </item> am Dateianfang entfernen
        first_item = re.search(r"<item id=", fixed)
        if first_item and fixed[:first_item.start()].strip().endswith("</item>"):
            fixed = fixed[:first_item.start()].replace("</item>", "", 1) + fixed[first_item.start():]
        # Letztes </item> vor </dictionary>
        fixed = fixed.replace("</dictionary>", "</item>\n</dictionary>")
    else:
        print("Keine Reparatur nötig, kopiere Datei …")
        fixed = content

    print(f"Schreibe {OUT_FILE} …")
    OUT_FILE.write_text(fixed, encoding="utf-8")

    # Kurzer Validierungstest
    from xml.etree import ElementTree as ET
    try:
        tree = ET.parse(str(OUT_FILE))
        items = tree.getroot().findall("item")
        print(f"OK: {len(items)} Einträge erfolgreich geparst.")
    except ET.ParseError as exc:
        print(f"FEHLER beim Parsen: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

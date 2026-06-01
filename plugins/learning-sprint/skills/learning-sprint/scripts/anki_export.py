#!/usr/bin/env python3
"""Build an Anki deck from a cards JSON spec.

Usage:
    python3 anki_export.py cards.json [out_basename]

Input JSON:
{
  "deck": "AWS SAA-C03",
  "cert_slug": "aws-saa-c03",
  "cards": [
    {"id": "saa-0001", "type": "basic",
     "front": "...", "back": "...",
     "domain": "domain1-design-secure", "topics": ["vpc", "s3"]},
    {"id": "saa-c-0001", "type": "cloze",
     "text": "An S3 bucket is {{c1::private}} by default.", "extra": "",
     "domain": "domain1-design-secure", "topics": ["s3"]}
  ]
}

Output (next to the JSON unless out_basename is given):
  <base>.tsv     ALWAYS  — zero-dependency; import via Anki > File > Import.
  <base>.apkg    only if `genanki` is importable — one-click double-click import.

Design notes (verified against the current Anki manual + genanki):
- Tags are hierarchical: "<cert_slug>::<domain>" plus any free topics, so you can
  study one exam domain at a time (Anki search: tag:<cert_slug>::<domain>).
- GUID = the literal stable card id. Re-running and re-importing therefore UPDATES
  existing notes instead of duplicating them, and the .tsv and .apkg paths emit
  IDENTICAL guids, so switching export formats never duplicates a card.
- Both note types map positionally: Basic = (Front, Back); Cloze = (Text, Extra).
"""
import json
import os
import sys


def card_tags(card, cert_slug):
    tags = []
    domain = card.get("domain")
    if domain:
        tags.append(f"{cert_slug}::{domain}" if cert_slug else domain)
    elif cert_slug:
        tags.append(cert_slug)
    tags.extend(card.get("topics", []))
    # Anki tags are space-delimited and cannot themselves contain spaces.
    return " ".join(t.replace(" ", "-") for t in tags if t)


def _clean(value):
    """Field text for #html:true: newlines become <br>, tabs become spaces."""
    return (
        str(value)
        .replace("\t", "    ")
        .replace("\r\n", "\n")
        .replace("\n", "<br>")
    )


def write_tsv(spec, path):
    deck = spec.get("deck", "Learning Sprint")
    cert = spec.get("cert_slug", "")
    lines = [
        "#separator:Tab",
        "#html:true",
        f"#deck:{deck}",
        "#notetype column:1",
        "#tags column:4",
        "#guid column:5",
    ]
    for card in spec["cards"]:
        if card.get("type") == "cloze":
            notetype, f1, f2 = "Cloze", card.get("text", ""), card.get("extra", "")
        else:
            notetype, f1, f2 = "Basic", card.get("front", ""), card.get("back", "")
        row = [notetype, _clean(f1), _clean(f2), card_tags(card, cert), card["id"]]
        lines.append("\t".join(row))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def try_apkg(spec, path):
    """Write a .apkg if genanki is available; return its path, else None."""
    try:
        import genanki
    except ImportError:
        return None

    deck_name = spec.get("deck", "Learning Sprint")
    seed = spec.get("cert_slug") or deck_name

    def stable_id(text):
        h = 0
        for ch in text:
            h = (h * 31 + ord(ch)) & 0x7FFFFFFF
        return h or 1

    deck = genanki.Deck(stable_id(seed), deck_name)

    class StableNote(genanki.Note):
        def __init__(self, *args, stable_key, **kwargs):
            super().__init__(*args, **kwargs)
            self._stable_key = stable_key

        @property
        def guid(self):
            return self._stable_key  # literal id -> matches the TSV guid column

    for card in spec["cards"]:
        if card.get("type") == "cloze":
            model = genanki.CLOZE_MODEL
            fields = [card.get("text", ""), card.get("extra", "")]
        else:
            model = genanki.BASIC_MODEL
            fields = [card.get("front", ""), card.get("back", "")]
        tags = card_tags(card, spec.get("cert_slug", "")).split()
        deck.add_note(
            StableNote(model=model, fields=fields, tags=tags, stable_key=card["id"])
        )
    genanki.Package(deck).write_to_file(path)
    return path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    spec_path = sys.argv[1]
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    if not spec.get("cards"):
        print("No cards in spec.", file=sys.stderr)
        sys.exit(1)
    base = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(spec_path)[0]

    tsv = write_tsv(spec, base + ".tsv")
    print(f"Wrote {tsv}  ({len(spec['cards'])} cards)")

    apkg = try_apkg(spec, base + ".apkg")
    if apkg:
        print(f"Wrote {apkg}  (genanki found — double-click to import)")
    else:
        print("genanki not installed; TSV only. For one-click .apkg: pip install genanki")
    print("Import the .tsv via Anki > File > Import — the directives auto-map every column.")


if __name__ == "__main__":
    main()

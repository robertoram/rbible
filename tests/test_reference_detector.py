import pytest
from rbible.reference_detector import detect_references

def test_simple_reference_detection():
    text = "En Juan 3:16 encontramos"
    refs = detect_references(text)
    assert len(refs) == 1
    assert refs[0]["reference"] == "Juan 3:16"

def test_multiple_references():
    text = "Ver Salmos 23:1 y también Juan 3:16-17"
    refs = detect_references(text)
    assert len(refs) == 2
    assert refs[0]["reference"] == "Salmos 23:1"
    assert refs[1]["reference"] == "Juan 3:16-17"

def test_numbered_books():
    text = "1 Reyes 19:11-12 y 2 Corintios 5:17"
    refs = detect_references(text)
    assert len(refs) == 2
    assert refs[0]["reference"] == "1 Reyes 19:11-12"
    assert refs[1]["reference"] == "2 Corintios 5:17"

def test_accented_books():
    text = "Véase Génesis 1:1"
    refs = detect_references(text)
    assert len(refs) == 1
    assert refs[0]["reference"] == "Génesis 1:1"

def test_no_references():
    text = "This text has no Bible references"
    refs = detect_references(text)
    assert len(refs) == 0

def test_reference_with_spaces():
    text = "  Salmos   23:1  "
    refs = detect_references(text)
    assert len(refs) == 1
    assert refs[0]["reference"] == "Salmos 23:1"

def test_verse_ranges():
    text = "Salmos 23:1-6"
    refs = detect_references(text)
    assert len(refs) == 1
    assert refs[0]["reference"] == "Salmos 23:1-6"
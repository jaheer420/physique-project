# backend/tests/test_parser1.py
import pytest
from physiqueneeds1 import parse_text

def test_parse_simple_idli(monkeypatch):
    # Monkeypatch get_food_by_name to make parser return recognized True for 'idli'
    from physiqueneeds1 import get_food_by_name
    monkeypatch.setattr('physiqueneeds1.get_food_by_name', lambda name: {'food_name_singular':'idli'} if 'idli' in name else None)
    res = parse_text("I ate 4 idlis")
    assert isinstance(res, list)
    # Expect an item with food 'idli' quantity 4
    found = None
    for it in res:
        if 'idli' in it['food']:
            found = it
    assert found is not None
    assert found['quantity'] == 4

def test_parse_rice(monkeypatch):
    monkeypatch.setattr('physiqueneeds1.get_food_by_name', lambda name: {'food_name_singular':'rice'} if 'rice' in name else None)
    res = parse_text("I ate 2 cup rice")
    found = next((it for it in res if 'rice' in it['food']), None)
    assert found is not None
    assert found['quantity'] == 2

def test_parse_tamil_english_mix(monkeypatch):
    monkeypatch.setattr('physiqueneeds1.get_food_by_name', lambda name: {'food_name_singular':'idli'} if 'idli' in name else None)
    res = parse_text("Iniku morning 4 idli sapten")
    found = next((it for it in res if 'idli' in it['food']), None)
    assert found is not None
    assert found['quantity'] == 4

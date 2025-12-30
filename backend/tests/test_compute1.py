# backend/tests/test_compute1.py
import pytest
from physiqueneeds1 import compute_nutrients

# Provide fake get_food_by_name to return the seed "idli" and "rice" rows
IDLI_ROW = {
    "id": 1,
    "food_name_singular": "idli",
    "food_name_plural": "idlis",
    "calories_per_unit": 52,
    "protein_per_unit": 2,
    "carbs_per_unit": 11,
    "fat_per_unit": 0.4,
    "fiber_per_unit": 0.8,
    "sugar_per_unit": 0.2,
    "sodium_per_unit_mg": 128,
    "cholesterol_per_unit_mg": 0,
    "calcium_per_unit_mg": 8,
    "iron_per_unit_mg": 0.4,
    "vitaminA_mcg": 1,
    "vitaminB1_mg": 0.03,
    "vitaminB2_mg": 0.01,
    "vitaminB3_mg": 0.3,
    "vitaminB6_mg": 0.02,
    "vitaminB9_mcg": 4,
    "vitaminB12_mcg": 0,
    "vitaminC_mg": 0.1,
    "vitaminD_mcg": 0,
    "vitaminE_mg": 0.02,
    "vitaminK_mcg": 0.3,
    "unit_name": "piece",
    "grams_per_unit": 55,
    "per_100g": 0
}

RICE_ROW = {
    "id": 2,
    "food_name_singular": "rice",
    "food_name_plural": "rice",
    "calories_per_unit": 130,
    "protein_per_unit": 2.7,
    "carbs_per_unit": 28,
    "fat_per_unit": 0.3,
    "fiber_per_unit": 0.4,
    "sugar_per_unit": 0,
    "sodium_per_unit_mg": 1,
    "cholesterol_per_unit_mg": 0,
    "calcium_per_unit_mg": 10,
    "iron_per_unit_mg": 0.2,
    "vitaminA_mcg": 0,
    "vitaminB1_mg": 0.02,
    "vitaminB2_mg": 0.01,
    "vitaminB3_mg": 1.5,
    "vitaminB6_mg": 0.02,
    "vitaminB9_mcg": 8,
    "vitaminB12_mcg": 0,
    "vitaminC_mg": 0,
    "vitaminD_mcg": 0,
    "vitaminE_mg": 0,
    "vitaminK_mcg": 0,
    "unit_name": "cup",
    "grams_per_unit": 200,
    "per_100g": 1
}

def fake_get_food_by_name(name):
    name = name.lower()
    if "idli" in name:
        return IDLI_ROW
    if "rice" in name:
        return RICE_ROW
    return None

def test_compute_idli(monkeypatch):
    monkeypatch.setattr('physiqueneeds1.get_food_by_name', fake_get_food_by_name)
    parsed = [{"food":"idli","quantity":4,"unit":"piece","raw":"4 idlis","recognized":True}]
    out = compute_nutrients(parsed)
    totals = out["totals"]
    assert totals["calories"] == 208  # 4 * 52
    assert round(totals["protein"], 4) == 8  # 4 * 2

def test_compute_rice(monkeypatch):
    monkeypatch.setattr('physiqueneeds1.get_food_by_name', fake_get_food_by_name)
    parsed = [{"food":"rice","quantity":2,"unit":"cup","raw":"2 cup rice","recognized":True}]
    out = compute_nutrients(parsed)
    totals = out["totals"]
    # 2 cups * 200g = 400g -> (400/100)*130 = 520
    assert totals["calories"] == 520
    # protein: (400/100)*2.7 = 10.8
    assert round(totals["protein"], 4) == round(2.7 * 4, 4)

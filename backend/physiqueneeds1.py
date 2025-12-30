import re
import json
from typing import List, Dict, Any
import spacy

from rapidfuzz import fuzz
from db import get_conn

# -----------------------------
# Load SpaCy safely
# -----------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = spacy.blank("en")

# -----------------------------
# STOPWORDS
# -----------------------------
VERB_STOPWORDS = {
    "i", "ate", "eat", "eaten", "eating",
    "had", "have", "having",
    "consumed", "consume",
    "and", "nd",
    "sapten", "sapidu", "saptinga", "sapdran",
    "iniku", "morning", "evening", "night",
    "breakfast", "lunch", "dinner", "snack", "today"
}

# -----------------------------
# Number words
# -----------------------------
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
    "half": 0.5, "quarter": 0.25,
    "a": 1, "an": 1
}

# -----------------------------
# Regex Patterns
# -----------------------------
QUANTITY_PATTERN = re.compile(
    r"(?P<num>\d+(\.\d+)?|\d+/\d+|"
    + "|".join(NUMBER_WORDS.keys()) + ")"
)

UNIT_ALIASES = {
    "piece": ["piece", "pieces", "pc", "pcs"],
    "cup": ["cup", "cups"],
    "bowl": ["bowl", "bowls"],
    "slice": ["slice", "slices"],
    "tbsp": ["tbsp", "tablespoon", "tablespoons"],
    "tsp": ["tsp", "teaspoon", "teaspoons"],
    "g": ["g", "gram", "grams"],
    "kg": ["kg", "kilogram", "kilograms"]
}

UNIT_LOOKUP = {v: k for k, lst in UNIT_ALIASES.items() for v in lst}

UNIT_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(u) for u in UNIT_LOOKUP.keys()) + r")\b"
)

# -----------------------------
# Number parser
# -----------------------------
def parse_number(text: str) -> float:
    text = text.lower().strip()
    if text in NUMBER_WORDS:
        return NUMBER_WORDS[text]
    if "/" in text:
        try:
            a, b = text.split("/")
            return float(a) / float(b)
        except:
            return 0
    try:
        return float(text)
    except:
        return 0

# -----------------------------
# DB helpers
# -----------------------------
def get_food_by_name(name: str):
    conn = get_conn()
    try:
        c = conn.cursor(dictionary=True)
        c.execute("""
            SELECT * FROM foods
            WHERE LOWER(food_name_singular)=LOWER(%s)
               OR LOWER(food_name_plural)=LOWER(%s)
            LIMIT 1
        """, (name, name))
        return c.fetchone()
    finally:
        conn.close()

def suggest_foods(raw: str, limit: int = 5):
    conn = get_conn()
    try:
        c = conn.cursor()
        like = f"%{raw}%"
        c.execute("""
            SELECT food_name_singular
            FROM foods
            WHERE food_name_singular LIKE %s
               OR food_name_plural LIKE %s
            LIMIT %s
        """, (like, like, limit))
        return [r[0] for r in c.fetchall()]
    finally:
        conn.close()

# ----------------------------------------------------------
# PARSER (ONLY ERROR FIX APPLIED)
# ----------------------------------------------------------
def parse_text(text: str) -> List[Dict[str, Any]]:
    lowered = text.lower()

    # ✅ FIX: split number+unit → 1cup → 1 cup
    lowered = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", lowered)

    lowered = lowered.replace(" and ", ",").replace("&", ",")

    cleaned = " ".join(
        w for w in lowered.split()
        if w not in VERB_STOPWORDS
    )

    matches = []

    for m in QUANTITY_PATTERN.finditer(cleaned):
        qty = parse_number(m.group("num"))

        unit_match = UNIT_PATTERN.search(cleaned, pos=m.end())
        unit = None
        unit_end = None
        if unit_match and unit_match.start() - m.end() < 12:
            unit = UNIT_LOOKUP.get(unit_match.group(0))
            unit_end = unit_match.end()

        food = None
        start_pos = unit_end if unit_end else m.end()
        after = cleaned[start_pos:start_pos + 40]

        food_match = re.search(r"\b[a-zA-Z][a-zA-Z0-9]*\b", after)
        if food_match:
            food = food_match.group(0)
        else:
            before = cleaned[:m.start()]
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]*\b", before)
            if words:
                food = words[-1]

        if not food or food in VERB_STOPWORDS or food in UNIT_LOOKUP:
            continue

        matches.append({
            "food": food,
            "quantity": qty,
            "unit": unit
        })

    combined = {}
    for m in matches:
        if m["food"] in combined:
            combined[m["food"]]["quantity"] += m["quantity"]
        else:
            combined[m["food"]] = m

    final = []
    for food, item in combined.items():
        row = get_food_by_name(food)
        final.append({
            "food": food,
            "quantity": item["quantity"],
            "unit": item["unit"],
            "recognized": row is not None,
            "suggestions": [] if row else suggest_foods(food)
        })

    return final

# ----------------------------------------------------------
# COMPUTE NUTRIENTS (FIXED NAME ONLY)
# ----------------------------------------------------------
def compute_nutrients(parsed_items):
    totals = {
        "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
        "fiber": 0, "sugar": 0,
        "sodium_mg": 0, "cholesterol_mg": 0,
        "calcium_mg": 0, "iron_mg": 0,
        "vitaminA_mcg": 0, "vitaminB1_mg": 0,
        "vitaminB2_mg": 0, "vitaminB3_mg": 0,
        "vitaminB6_mg": 0, "vitaminB9_mcg": 0,
        "vitaminB12_mcg": 0, "vitaminC_mg": 0,
        "vitaminD_mcg": 0, "vitaminE_mg": 0,
        "vitaminK_mcg": 0
    }

    for item in parsed_items:
        if not item["recognized"]:
            continue

        row = get_food_by_name(item["food"])
        qty = item["quantity"]
        unit = item["unit"]

        if row.get("per_100g") == 1:
            grams = qty if unit == "g" else qty * row["grams_per_unit"]
            factor = grams / 100
        else:
            factor = qty

        def mul(v): 
            return float(v or 0) * factor

        totals["calories"] += mul(row["calories_per_unit"])
        totals["protein"] += mul(row["protein_per_unit"])
        totals["carbs"] += mul(row["carbs_per_unit"])
        totals["fat"] += mul(row["fat_per_unit"])

    for k in totals:
        totals[k] = round(totals[k], 4)

    return {"totals": totals, "items": parsed_items}

# ----------------------------------------------------------
# SAVE LOG (UNCHANGED)
# ----------------------------------------------------------
def save_log(user_id, raw_text, parsed_items, totals):
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO user_food_logs (user_id, raw_text, parsed_json, totals_json)
            VALUES (%s, %s, %s, %s)
        """, (user_id, raw_text, json.dumps(parsed_items), json.dumps(totals)))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()









'''import re
import json
from typing import List, Dict, Any
import spacy

from rapidfuzz import fuzz
from db import get_conn

# -----------------------------
# Load SpaCy safely
# -----------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = spacy.blank("en")

# -----------------------------
# STOPWORDS
# -----------------------------
VERB_STOPWORDS = {
    "i", "ate", "eat", "eaten", "eating",
    "had", "have", "having",
    "consumed", "consume",
    "and", "nd",
    "sapten", "sapidu", "saptinga", "sapdran",
    "iniku", "morning", "evening", "night",
    "breakfast", "lunch", "dinner", "snack", "today"
}

# -----------------------------
# Number words
# -----------------------------
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
    "half": 0.5, "quarter": 0.25,
    "a": 1, "an": 1
}

# -----------------------------
# Regex Patterns
# -----------------------------
QUANTITY_PATTERN = re.compile(
    r"(?P<num>\d+(\.\d+)?|\d+/\d+|"
    + "|".join(NUMBER_WORDS.keys()) + ")"
)

UNIT_ALIASES = {
    "piece": ["piece", "pieces", "pc", "pcs"],
    "cup": ["cup", "cups"],
    "bowl": ["bowl", "bowls"],
    "slice": ["slice", "slices"],
    "tbsp": ["tbsp", "tablespoon", "tablespoons"],
    "tsp": ["tsp", "teaspoon", "teaspoons"],
    "g": ["g", "gram", "grams"],
    "kg": ["kg", "kilogram", "kilograms"]
}

UNIT_LOOKUP = {v: k for k, lst in UNIT_ALIASES.items() for v in lst}

UNIT_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(u) for u in UNIT_LOOKUP.keys()) + r")\b"
)

# -----------------------------
# Number parser
# -----------------------------
def parse_number(text: str) -> float:
    text = text.lower().strip()
    if text in NUMBER_WORDS:
        return NUMBER_WORDS[text]
    if "/" in text:
        try:
            a, b = text.split("/")
            return float(a) / float(b)
        except:
            return 0
    try:
        return float(text)
    except:
        return 0

# -----------------------------
# DB helpers
# -----------------------------
def get_food_by_name(name: str):
    conn = get_conn()
    try:
        c = conn.cursor(dictionary=True)
        c.execute("""
            SELECT * FROM foods
            WHERE LOWER(food_name_singular)=LOWER(%s)
               OR LOWER(food_name_plural)=LOWER(%s)
            LIMIT 1
        """, (name, name))
        return c.fetchone()
    finally:
        conn.close()

def suggest_foods(raw: str, limit: int = 5):
    conn = get_conn()
    try:
        c = conn.cursor()
        like = f"%{raw}%"
        c.execute("""
            SELECT food_name_singular
            FROM foods
            WHERE food_name_singular LIKE %s
               OR food_name_plural LIKE %s
            LIMIT %s
        """, (like, like, limit))
        return [r[0] for r in c.fetchall()]
    finally:
        conn.close()

# ----------------------------------------------------------
# PARSER (WORKING – UNCHANGED)
# ----------------------------------------------------------
def parse_text(text: str) -> List[Dict[str, Any]]:
    lowered = text.lower()
    lowered = lowered.replace(" and ", ",").replace("&", ",")

    cleaned = " ".join(
        w for w in lowered.split()
        if w not in VERB_STOPWORDS
    )

    matches = []

    for m in QUANTITY_PATTERN.finditer(cleaned):
        qty = parse_number(m.group("num"))

        unit_match = UNIT_PATTERN.search(cleaned, pos=m.end())
        unit = None
        unit_end = None
        if unit_match and unit_match.start() - m.end() < 12:
            unit = UNIT_LOOKUP.get(unit_match.group(0))
            unit_end = unit_match.end()

        food = None
        start_pos = unit_end if unit_end else m.end()
        after = cleaned[start_pos:start_pos + 40]

        food_match = re.search(r"\b[a-zA-Z][a-zA-Z0-9]*\b", after)
        if food_match:
            food = food_match.group(0)
        else:
            before = cleaned[:m.start()]
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]*\b", before)
            if words:
                food = words[-1]

        if not food or food in VERB_STOPWORDS or food in UNIT_LOOKUP:
            continue

        matches.append({
            "food": food,
            "quantity": qty,
            "unit": unit
        })

    combined = {}
    for m in matches:
        if m["food"] in combined:
            combined[m["food"]]["quantity"] += m["quantity"]
        else:
            combined[m["food"]] = m

    final = []
    for food, item in combined.items():
        row = get_food_by_name(food)
        final.append({
            "food": food,
            "quantity": item["quantity"],
            "unit": item["unit"],
            "recognized": row is not None,
            "suggestions": [] if row else suggest_foods(food)
        })

    return final

# ----------------------------------------------------------
# COMPUTE NUTRIENTS (✅ FIXED – ONLY ERROR PART)
# ----------------------------------------------------------
def compute_nutrients(parsed_items):
    totals = {
        "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
        "fiber": 0, "sugar": 0,
        "sodium_mg": 0, "cholesterol_mg": 0,
        "calcium_mg": 0, "iron_mg": 0,
        "vitaminA_mcg": 0, "vitaminB1_mg": 0,
        "vitaminB2_mg": 0, "vitaminB3_mg": 0,
        "vitaminB6_mg": 0, "vitaminB9_mcg": 0,
        "vitaminB12_mcg": 0, "vitaminC_mg": 0,
        "vitaminD_mcg": 0, "vitaminE_mg": 0,
        "vitaminK_mcg": 0
    }

    for item in parsed_items:
        if not item["recognized"]:
            continue

        row = get_food_by_name(item["food"])
        qty = item["quantity"]
        unit = item["unit"]

        # ✅ ONLY FIX
        if row.get("per_100g") == 1:
            grams = qty if unit == "g" else qty * row["grams_per_unit"]
            factor = grams / 100
        else:
            factor = qty

        def mul(v): return float(v or 0) * factor

        totals["calories"] += mul(row["calories_per_unit"])
        totals["protein"] += mul(row["protein_per_unit"])
        totals["carbs"] += mul(row["carbs_per_unit"])
        totals["fat"] += mul(row["fat_per_unit"])

    for k in totals:
        totals[k] = round(totals[k], 4)

    return {"totals": totals, "items": parsed_items}

# ----------------------------------------------------------
# SAVE LOG (UNCHANGED)
# ----------------------------------------------------------
def save_log(user_id, raw_text, parsed_items, totals):
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO user_food_logs (user_id, raw_text, parsed_json, totals_json)
            VALUES (%s, %s, %s, %s)
        """, (user_id, raw_text, json.dumps(parsed_items), json.dumps(totals)))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()
'''
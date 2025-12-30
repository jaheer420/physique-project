-- backend/models1.sql
-- CREATE TABLE statements and seed data for Physique app

CREATE DATABASE IF NOT EXISTS physique_db;
USE physique_db;

DROP TABLE IF EXISTS foods;
CREATE TABLE foods (
    id INT PRIMARY KEY,
    food_name_singular VARCHAR(100) NOT NULL,
    food_name_plural VARCHAR(100),
    calories_per_unit FLOAT NOT NULL,
    protein_per_unit FLOAT,
    carbs_per_unit FLOAT,
    fat_per_unit FLOAT,
    fiber_per_unit FLOAT,
    sugar_per_unit FLOAT,
    sodium_per_unit_mg FLOAT,
    cholesterol_per_unit_mg FLOAT,
    calcium_per_unit_mg FLOAT,
    iron_per_unit_mg FLOAT,
    vitaminA_mcg FLOAT,
    vitaminB1_mg FLOAT,
    vitaminB2_mg FLOAT,
    vitaminB3_mg FLOAT,
    vitaminB6_mg FLOAT,
    vitaminB9_mcg FLOAT,
    vitaminB12_mcg FLOAT,
    vitaminC_mg FLOAT,
    vitaminD_mcg FLOAT,
    vitaminE_mg FLOAT,
    vitaminK_mcg FLOAT,
    unit_name VARCHAR(50),
    grams_per_unit FLOAT,
    per_100g BOOLEAN DEFAULT 0,
    base_unit VARCHAR(20) DEFAULT NULL
);

-- Seed rows (exact inserts requested)
-- idli (id=1)
INSERT INTO foods (
    id, food_name_singular, food_name_plural,
    calories_per_unit, protein_per_unit, carbs_per_unit, fat_per_unit,
    fiber_per_unit, sugar_per_unit, sodium_per_unit_mg,
    cholesterol_per_unit_mg, calcium_per_unit_mg, iron_per_unit_mg,
    vitaminA_mcg, vitaminB1_mg, vitaminB2_mg, vitaminB3_mg, vitaminB6_mg,
    vitaminB9_mcg, vitaminB12_mcg, vitaminC_mg, vitaminD_mcg, vitaminE_mg, vitaminK_mcg,
    unit_name, grams_per_unit
)
VALUES (
    1, 'idli', 'idlis',
    52, 2, 11, 0.4,
    0.8, 0.2, 128,
    0, 8, 0.4,
    1, 0.03, 0.01, 0.3, 0.02,
    4, 0, 0.1, 0, 0.02, 0.3,
    'piece', 55
);

-- rice (id=2) — cooked rice values (calories per 100g = 130)
INSERT INTO foods (
    id, food_name_singular, food_name_plural,
    calories_per_unit, protein_per_unit, carbs_per_unit, fat_per_unit,
    fiber_per_unit, sugar_per_unit, sodium_per_unit_mg,
    cholesterol_per_unit_mg, calcium_per_unit_mg, iron_per_unit_mg,
    vitaminA_mcg, vitaminB1_mg, vitaminB2_mg, vitaminB3_mg, vitaminB6_mg,
    vitaminB9_mcg, vitaminB12_mcg, vitaminC_mg, vitaminD_mcg, vitaminE_mg, vitaminK_mcg,
    unit_name, grams_per_unit
)
VALUES (
    2, 'rice', 'rice',
    130, 2.7, 28, 0.3,
    0.4, 0, 1,
    0, 10, 0.2,
    0, 0.02, 0.01, 1.5, 0.02,
    8, 0, 0, 0, 0, 0,
    'cup', 200
);

-- After inserting seeds, update rice per_100g to 1 explicitly (calories_per_unit treated as per 100g).
UPDATE foods SET per_100g = 1 WHERE id = 2;

DROP TABLE IF EXISTS user_food_logs;
CREATE TABLE user_food_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_text TEXT,
    parsed_json JSON,
    totals_json JSON
);

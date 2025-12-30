from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from physiqueneeds1 import parse_text, compute_nutrients, save_log
from db import get_conn
from calorie_target import calculate_daily_calories
from workout import workout_bp


import os
from flask import Flask, send_from_directory




app = Flask(__name__)

CORS(app, supports_credentials=True)




app.register_blueprint(workout_bp)


# =====================================================
# HOME
# =====================================================
@app.route("/")
def home():
    return jsonify({"status": "Backend running"})


# =====================================================
# HELPERS
# =====================================================
def get_user_profile(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM user_profiles WHERE user_id=%s",
            (user_id,)
        )
        return cur.fetchone()
    finally:
        conn.close()


def get_today_totals(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
                COALESCE(SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.calories') AS DECIMAL(10,2))),0) calories,
                COALESCE(SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.protein') AS DECIMAL(10,2))),0) protein,
                COALESCE(SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.carbs') AS DECIMAL(10,2))),0) carbs,
                COALESCE(SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.fat') AS DECIMAL(10,2))),0) fat
            FROM user_food_logs
            WHERE user_id=%s AND DATE(timestamp)=CURDATE()
        """, (user_id,))
        r = cur.fetchone()
        return {
            "calories": float(r["calories"] or 0),
            "protein": float(r["protein"] or 0),
            "carbs": float(r["carbs"] or 0),
            "fat": float(r["fat"] or 0),
        }
    finally:
        conn.close()


def get_last_7_days(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
                DATE(timestamp) day,
                SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.calories') AS DECIMAL(10,2))) calories,
                SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.protein') AS DECIMAL(10,2))) protein,
                SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.carbs') AS DECIMAL(10,2))) carbs,
                SUM(CAST(JSON_EXTRACT(totals_json,'$.totals.fat') AS DECIMAL(10,2))) fat
            FROM user_food_logs
            WHERE user_id=%s
              AND DATE(timestamp)>=DATE_SUB(CURDATE(),INTERVAL 6 DAY)
            GROUP BY day
            ORDER BY day
        """, (user_id,))
        return cur.fetchall()
    finally:
        conn.close()


def generate_advice(consumed, target, goal):
    tips = []
    if consumed > target:
        tips.append("⚠️ You exceeded your daily calorie target.")
    else:
        tips.append("✅ Calories are under control.")

    if goal == "loss":
        tips += ["🥗 Avoid rice at night.", "🍳 Increase protein intake."]
    elif goal == "gain":
        tips += ["💪 Increase protein & carbs.", "🍌 Add banana post-workout."]
    return tips


# =====================================================
# UPDATE USER PROFILE
# =====================================================
@app.route("/api/profile/update", methods=["POST"])
def update_profile():
    data = request.json
    user_id = data["user_id"]

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE user_profiles
            SET age=%s,
                height_cm=%s,
                weight_kg=%s,
                gender=%s,
                activity_level=%s,
                goal=%s
            WHERE user_id=%s
        """, (
            data["age"],
            data["height_cm"],
            data["weight_kg"],
            data["gender"],
            data["activity_level"],
            data["goal"],
            user_id
        ))
        conn.commit()
    finally:
        conn.close()

    profile = get_user_profile(user_id)
    daily_target = calculate_daily_calories(profile)

    return jsonify({
        "success": True,
        "daily_target": daily_target,
        "profile": profile
    })


# =====================================================
# LOG FOOD
# =====================================================
@app.route("/api/log", methods=["POST"])
def api_log():
    data = request.json
    parsed = parse_text(data["text"])
    computed = compute_nutrients(parsed)
    save_log(data["user_id"], data["text"], parsed, computed)
    return jsonify({"success": True})


@app.route("/api/logs")
def api_logs():
    user_id = request.args.get("user_id")
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, raw_text, totals_json, timestamp
            FROM user_food_logs
            WHERE user_id=%s
            ORDER BY timestamp DESC
            LIMIT 10
        """, (user_id,))
        return jsonify({"success": True, "logs": cur.fetchall()})
    finally:
        conn.close()


# =====================================================
# TODAY SUMMARY
# =====================================================
@app.route("/api/summary/today/<int:user_id>")
def today_summary(user_id):
    profile = get_user_profile(user_id)
    target = calculate_daily_calories(profile)
    t = get_today_totals(user_id)

    remaining = target - t["calories"]

    return jsonify({
        "daily_target": target,
        "consumed": t["calories"],
        "remaining": max(remaining, 0),
        "exceeded": abs(min(remaining, 0)),
        "protein": round(t["protein"], 2),
        "carbs": round(t["carbs"], 2),
        "fat": round(t["fat"], 2),
        "advice": generate_advice(t["calories"], target, profile["goal"])
    })


# =====================================================
# MACRO SUMMARY
# =====================================================
@app.route("/api/summary/macros/<int:user_id>")
def macro_summary(user_id):
    profile = get_user_profile(user_id)
    consumed = get_today_totals(user_id)

    calories_target = calculate_daily_calories(profile)

    targets = {
        "calories": calories_target,
        "protein": round((calories_target * 0.25) / 4, 1),
        "carbs": round((calories_target * 0.45) / 4, 1),
        "fat": round((calories_target * 0.30) / 9, 1)
    }

    def percent(v, t):
        return min(int((v / t) * 100), 100) if t else 0

    return jsonify({
        "targets": targets,
        "consumed": consumed,
        "progress": {
            k: percent(consumed[k], targets[k]) for k in targets
        }
    })


# =====================================================
# WEEKLY SUMMARY
# =====================================================
@app.route("/api/summary/weekly/<int:user_id>")
def weekly_summary(user_id):
    profile = get_user_profile(user_id)
    target = calculate_daily_calories(profile)
    data = get_last_7_days(user_id)

    met_days = sum(1 for d in data if d["calories"] and d["calories"] <= target)

    avg = lambda k: round(
        sum(d[k] or 0 for d in data) / 7, 2
    )

    return jsonify({
        "average_calories": avg("calories"),
        "average_protein": avg("protein"),
        "average_carbs": avg("carbs"),
        "average_fat": avg("fat"),
        "consistency_percent": int((met_days / 7) * 100),
        "status": "Good progress ✅" if met_days >= 5 else "Needs improvement ⚠️",
        "days": data
    })


# =====================================================
# 🎯 TARGET-BASED FOOD RECOMMENDATION (FIXED)
# =====================================================
@app.route("/api/recommend/target", methods=["POST"])
def recommend_for_target():
    data = request.get_json()

    # -------------------------------
    # 1. Read target calories
    # -------------------------------
    target_calories = float(data.get("target_calories", 0))

    if target_calories <= 0:
        return jsonify({"error": "Target calories must be greater than zero"}), 400

    # -------------------------------
    # 2. Fetch foods from DB (EXTENDED)
    # -------------------------------
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
            food_name_singular AS food,
            calories_per_unit,
            protein_per_unit,
            carbs_per_unit,
            fat_per_unit,
            max_units_per_day,
            allowed_meals,
            pros,
            cons
        FROM foods
    """)
    foods = cur.fetchall()
    conn.close()

    # -------------------------------
    # 3. Safe calculation engine
    # -------------------------------
    remaining_cal = target_calories
    plan = []

    total = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }

    for f in foods:
        if remaining_cal <= 0:
            break

        calories_per_unit = f["calories_per_unit"]
        if not calories_per_unit or calories_per_unit <= 0:
            continue

        max_units = f.get("max_units_per_day") or 1

        # 🔒 REAL-WORLD SAFE QUANTITY
        units = min(
            int(remaining_cal // calories_per_unit),
            int(max_units)
        )

        if units <= 0:
            continue

        calories = units * calories_per_unit
        protein = units * (f["protein_per_unit"] or 0)
        carbs = units * (f["carbs_per_unit"] or 0)
        fat = units * (f["fat_per_unit"] or 0)

        plan.append({
            "food": f["food"],
            "quantity": units,
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "carbs": round(carbs, 1),
            "fat": round(fat, 1),
            "pros": f["pros"],
            "cons": f["cons"]
        })

        total["calories"] += calories
        total["protein"] += protein
        total["carbs"] += carbs
        total["fat"] += fat

        remaining_cal -= calories

    # -------------------------------
    # 4. Response
    # -------------------------------
    return jsonify({
        "target_calories": round(target_calories, 1),
        "recommended_foods": plan,
        "total_nutrition": {
            "calories": round(total["calories"], 1),
            "protein": round(total["protein"], 1),
            "carbs": round(total["carbs"], 1),
            "fat": round(total["fat"], 1)
        }
    })


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
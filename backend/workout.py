# workout.py
import os
import json
from datetime import datetime, date
from flask import Blueprint, request, jsonify

print("🔥 workout.py LOADED")  # DEBUG PROOF

# -------------------------------------------------
# Blueprint
# -------------------------------------------------
workout_bp = Blueprint(
    "workout",
    __name__,
    url_prefix="/api/workout"
)

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "workout_logs")

os.makedirs(LOG_DIR, exist_ok=True)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def get_log_file(user_id):
    """Return today's workout log file for a user"""
    today = date.today().isoformat()
    return os.path.join(LOG_DIR, f"user_{user_id}_{today}.json")


def read_logs(path):
    """Read workout logs from file safely"""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def write_logs(path, data):
    """Atomic write to prevent corruption"""
    temp_path = f"{path}.tmp"
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, path)


# -------------------------------------------------
# POST: Complete workout
# -------------------------------------------------
@workout_bp.route("/complete", methods=["POST", "OPTIONS"])
def complete_workout():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid or missing JSON payload"
        }), 400

    # ---------------------------
    # 1. Validate payload
    # ---------------------------
    required = ["user_id", "workout_name", "sets", "calories_per_set"]
    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing field: {field}"
            }), 400

    try:
        user_id = int(data["user_id"])
        workout_name = str(data["workout_name"])
        sets = int(data["sets"])
        calories_per_set = float(data["calories_per_set"])
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Invalid payload values"
        }), 400

    if sets <= 0 or calories_per_set <= 0:
        return jsonify({
            "success": False,
            "error": "Sets and calories must be positive"
        }), 400

    # ---------------------------
    # 2. Calculate calories
    # ---------------------------
    calories_burned = sets * calories_per_set

    entry = {
        "workout_name": workout_name,
        "sets": sets,
        "calories_per_set": calories_per_set,
        "calories_burned": calories_burned,
        "timestamp": datetime.now().isoformat()
    }

    # ---------------------------
    # 3. File operations
    # ---------------------------
    file_path = get_log_file(user_id)
    logs = read_logs(file_path)
    logs.append(entry)
    write_logs(file_path, logs)

    # ---------------------------
    # 4. Daily total
    # ---------------------------
    total_burned = sum(w.get("calories_burned", 0) for w in logs)

    print("✅ WORKOUT SAVED:", entry)

    # ---------------------------
    # 5. Response
    # ---------------------------
    return jsonify({
        "success": True,
        "today_burned": total_burned,
        "logged_workout": entry
    }), 200


# -------------------------------------------------
# GET: Today's burned calories
# -------------------------------------------------
@workout_bp.route("/today/<int:user_id>", methods=["GET"])
def today_burned(user_id):
    print("🔥 TODAY ROUTE HIT:", user_id)

    file_path = get_log_file(user_id)
    logs = read_logs(file_path)

    total_burned = sum(w.get("calories_burned", 0) for w in logs)

    return jsonify({
        "date": date.today().isoformat(),
        "today_burned": total_burned,
        "workouts_count": len(logs),
        "workouts": logs
    }), 200

def calculate_daily_calories(profile):
    """
    Single source of truth for daily calorie target.
    Uses Mifflin-St Jeor equation with activity & goal adjustment.
    """

    if not profile:
        return 2000  # safe fallback

    # -----------------------------
    # SAFE EXTRACTION
    # -----------------------------
    weight = float(profile.get("weight_kg") or 0)
    height = float(profile.get("height_cm") or 0)
    age = int(profile.get("age") or 0)
    gender = profile.get("gender", "male")
    activity = profile.get("activity_level", "moderate")
    goal = profile.get("goal", "maintain")

    # -----------------------------
    # BMR (UNCHANGED FORMULA)
    # -----------------------------
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # -----------------------------
    # ACTIVITY MULTIPLIER
    # -----------------------------
    activity_map = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "heavy": 1.725
    }

    multiplier = activity_map.get(activity, 1.55)
    tdee = bmr * multiplier

    # -----------------------------
    # GOAL ADJUSTMENT
    # -----------------------------
    if goal == "loss":
        calories = tdee - 500
    elif goal == "gain":
        calories = tdee + 300
    else:
        calories = tdee

    # -----------------------------
    # SAFETY FLOOR
    # -----------------------------
    MIN_CALORIES = 1200
    return int(max(calories, MIN_CALORIES))

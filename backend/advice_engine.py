def generate_advice(consumed, target, goal):
    advice = []

    if consumed > target:
        advice.append("⚠️ You crossed your daily calorie limit.")
    else:
        advice.append("✅ Calories are under control.")

    if goal == "loss":
        advice.append("Avoid rice at night.")
        advice.append("Add protein like eggs or dal.")
    elif goal == "gain":
        advice.append("Increase protein and carbs.")
        advice.append("Post-workout banana recommended.")

    return advice

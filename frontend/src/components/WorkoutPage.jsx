import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./WorkoutPage.css";

const WORKOUTS = {
  "Weight Gain": ["Squats", "Deadlift", "Bench Press", "Overhead Press"],
  "Weight Loss": ["HIIT", "Jump Rope", "Burpees", "Mountain Climbers"],
  Maintain: ["Jogging", "Push-ups", "Plank"],
  Abs: ["Crunches", "Leg Raises", "Plank", "Russian Twist"],
  Legs: ["Squats", "Lunges", "Leg Press"],
  Shoulders: ["Shoulder Press", "Lateral Raises"],
  Arms: ["Bicep Curls", "Tricep Dips", "Hammer Curls"]
};

export default function WorkoutPage() {
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  return (
    <div className="workout-page">
      <div className="workout-glass">
        <button className="back-btn" onClick={() => navigate("/")}>
          ← Back
        </button>

        <h2>Workout Categories</h2>

        <div className="category-grid">
          {Object.keys(WORKOUTS).map((c) => (
            <div
              key={c}
              className={`category-card ${selected === c ? "active" : ""}`}
              onClick={() => setSelected(c)}
            >
              {c}
            </div>
          ))}
        </div>

        {selected && (
          <div className="workout-list">
            <h3>{selected} Workouts</h3>
            <ul>
              {WORKOUTS[selected].map((w) => (
                <li
                  key={w}
                  onClick={() => navigate(`/workout/${w}`)}
                >
                  {w}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

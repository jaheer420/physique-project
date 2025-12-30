import { useNavigate } from "react-router-dom";
import "./Dboard.css";

export default function Dboard() {
  const navigate = useNavigate();

  /* STATIC VALUES (SAFE)
     Later you can replace with API data */
  const caloriesConsumed = 988;
  const calorieTarget = 2200;

  const protein = 42;
  const carbs = 180;
  const fat = 38;

  return (
    <div className="dboard-page">
      <div className="dboard-glass">

        {/* HEADER */}
        <h2>Today</h2>

        {/* HERO CALORIES */}
        <div className="hero-card">
          <div className="hero-value">{caloriesConsumed}</div>
          <div className="hero-label">Calories Consumed</div>

          <div className="hero-sub">
            Target: {calorieTarget} kcal
          </div>
        </div>

        {/* PRIMARY ACTION */}
        <button
          className="primary-btn"
          onClick={() => navigate("/workouts")}
        >
          💪 Start Workout
        </button>

        {/* MACROS */}
        <div className="macro-row">
          <div className="macro-card">
            <span className="macro-value">{protein}g</span>
            <span className="macro-label">Protein</span>
          </div>

          <div className="macro-card">
            <span className="macro-value">{carbs}g</span>
            <span className="macro-label">Carbs</span>
          </div>

          <div className="macro-card">
            <span className="macro-value">{fat}g</span>
            <span className="macro-label">Fat</span>
          </div>
        </div>

        {/* SECONDARY ACTIONS */}
        <div className="secondary-actions">
          <button onClick={() => navigate("/food")}>
            🍽 Log Food
          </button>

          <button onClick={() => navigate("/progress")}>
            📊 View Progress
          </button>
        </div>

      </div>
    </div>
  );
}

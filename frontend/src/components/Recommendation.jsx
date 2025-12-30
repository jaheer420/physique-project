import { useState } from "react";
import { getTargetRecommendation } from "../api";
import { useNavigate } from "react-router-dom";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from "chart.js";

import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

export default function Recommendation() {
  const navigate = useNavigate();

  const [targetCalories, setTargetCalories] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  async function generatePlan() {
    if (!targetCalories) return;

    setLoading(true);
    const res = await getTargetRecommendation({
      target_calories: Number(targetCalories)
    });
    setData(res);
    setLoading(false);
  }

  /* =========================
     CHART DATA (SAFE DERIVED)
  ========================== */

  const pieData =
    data && {
      labels: ["Protein", "Carbs", "Fat"],
      datasets: [
        {
          data: [
            data.total_nutrition.protein * 4,
            data.total_nutrition.carbs * 4,
            data.total_nutrition.fat * 9
          ],
          backgroundColor: ["#4ade80", "#60a5fa", "#facc15"]
        }
      ]
    };

  const barData =
    data && {
      labels: ["Target Calories", "Achieved Calories"],
      datasets: [
        {
          label: "Calories",
          data: [
            data.target_calories,
            data.total_nutrition.calories
          ],
          backgroundColor: ["#93c5fd", "#22c55e"]
        }
      ]
    };

  return (
    <div className="app-container">
      <h2 className="header">
        🎯 Target <span className="needs">Food Plan</span>
      </h2>

      {/* TARGET INPUT */}
      <div className="card">
        <label>Target Calories</label>
        <input
          type="number"
          placeholder="e.g. 2030"
          value={targetCalories}
          onChange={(e) => setTargetCalories(e.target.value)}
        />
        <button onClick={generatePlan}>Generate Plan</button>
      </div>

      {/* LOADING */}
      {loading && (
        <div className="card">
          <p className="muted">Calculating food plan...</p>
        </div>
      )}

      {/* RESULT */}
      {data && (
        <>
          {/* TARGET */}
          <div className="card">
            <h3>🎯 Target</h3>
            <p>Target Calories: {data.target_calories} kcal</p>
          </div>

          {/* FOOD LIST */}
          <div className="card">
            <h3>🍽 Recommended Foods & Quantities</h3>

            {data.recommended_foods.map((f, i) => (
              <p key={i}>
                {f.food} × {f.quantity} → {f.calories} kcal
              </p>
            ))}
          </div>

          {/* TOTAL NUTRITION */}
          <div className="card">
            <h3>📊 Total Nutrition</h3>
            <p>Calories: {data.total_nutrition.calories} kcal</p>
            <p>Protein: {data.total_nutrition.protein} g</p>
            <p>Carbs: {data.total_nutrition.carbs} g</p>
            <p>Fat: {data.total_nutrition.fat} g</p>
          </div>

          {/* PIE CHART */}
          <div className="card">
            <h3>🥧 Macro Calories Split</h3>
            <Pie data={pieData} />
          </div>

          {/* BAR CHART */}
          <div className="card">
            <h3>📊 Target vs Achieved</h3>
            <Bar data={barData} />
          </div>

          {/* EXPLANATION */}
          <div className="card">
            <h3>🧠 Why These Foods?</h3>

            {data.recommended_foods.map((f, i) => (
              <div key={i} style={{ marginBottom: "12px" }}>
                <strong>{f.food}</strong>
                <p>✅ Pros: {f.pros || "Nutritious and beneficial"}</p>
                <p>⚠️ Cons: {f.cons || "Avoid overconsumption"}</p>
              </div>
            ))}
          </div>
        </>
      )}

      <button className="workout-btn" onClick={() => navigate("/")}>
        ⬅ Back to Dashboard
      </button>
    </div>
  );
}

import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import "./WorkoutDetail.css";

import Swal from "sweetalert2";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from "chart.js";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

/* COMPLETE STATIC DATA */
const WORKOUT_DETAILS = {
  Crunches: { muscle: "Abs", sets: 3, reps: 15, rest: "30 sec", calories: 50, difficulty: "Beginner" },
  "Leg Raises": { muscle: "Abs", sets: 3, reps: 12, rest: "40 sec", calories: 60, difficulty: "Intermediate" },
  Plank: { muscle: "Core", sets: 3, reps: "30–60 sec", rest: "45 sec", calories: 70, difficulty: "Intermediate" },
  "Russian Twist": { muscle: "Abs", sets: 3, reps: 20, rest: "30 sec", calories: 55, difficulty: "Intermediate" },

  Squats: { muscle: "Legs", sets: 4, reps: 12, rest: "60 sec", calories: 90, difficulty: "Intermediate" },
  Lunges: { muscle: "Legs", sets: 3, reps: 10, rest: "45 sec", calories: 80, difficulty: "Beginner" },
  "Leg Press": { muscle: "Legs", sets: 4, reps: 12, rest: "60 sec", calories: 100, difficulty: "Intermediate" },

  "Shoulder Press": { muscle: "Shoulders", sets: 4, reps: 10, rest: "60 sec", calories: 85, difficulty: "Intermediate" },
  "Lateral Raises": { muscle: "Shoulders", sets: 3, reps: 12, rest: "45 sec", calories: 60, difficulty: "Beginner" },

  "Bicep Curls": { muscle: "Biceps", sets: 3, reps: 12, rest: "45 sec", calories: 55, difficulty: "Beginner" },
  "Tricep Dips": { muscle: "Triceps", sets: 3, reps: 10, rest: "45 sec", calories: 65, difficulty: "Intermediate" },
  "Hammer Curls": { muscle: "Biceps", sets: 3, reps: 12, rest: "45 sec", calories: 60, difficulty: "Beginner" },

  Deadlift: { muscle: "Full Body", sets: 4, reps: 6, rest: "90 sec", calories: 120, difficulty: "Advanced" },
  "Bench Press": { muscle: "Chest", sets: 4, reps: 8, rest: "90 sec", calories: 110, difficulty: "Intermediate" },
  "Overhead Press": { muscle: "Shoulders", sets: 4, reps: 8, rest: "90 sec", calories: 95, difficulty: "Intermediate" },

  HIIT: { muscle: "Full Body", sets: 5, reps: "30 sec on / 30 sec off", rest: "30 sec", calories: 150, difficulty: "Advanced" },
  "Jump Rope": { muscle: "Cardio", sets: 4, reps: "1 min", rest: "30 sec", calories: 130, difficulty: "Beginner" },
  Burpees: { muscle: "Full Body", sets: 3, reps: 12, rest: "45 sec", calories: 140, difficulty: "Advanced" },
  "Mountain Climbers": { muscle: "Core & Cardio", sets: 4, reps: "30 sec", rest: "30 sec", calories: 120, difficulty: "Intermediate" },

  Jogging: { muscle: "Cardio", sets: 1, reps: "20–30 min", rest: "-", calories: 180, difficulty: "Beginner" },
  "Push-ups": { muscle: "Chest & Arms", sets: 3, reps: 15, rest: "45 sec", calories: 70, difficulty: "Beginner" }
};

export default function WorkoutDetail() {
  const { name } = useParams();
  const navigate = useNavigate();
  const workout = WORKOUT_DETAILS[name];

  const [targetCalories, setTargetCalories] = useState("");
  const [todayBurned, setTodayBurned] = useState(0);
  const [showCharts, setShowCharts] = useState(false);

  if (!workout) {
    return (
      <div className="workout-detail-page">
        <div className="workout-detail-glass">
          <button onClick={() => navigate(-1)}>← Back</button>
          <p>Workout details not found.</p>
        </div>
      </div>
    );
  }

  async function handleComplete() {
    const payload = {
      user_id: 1,
      workout_name: name,
      sets: workout.sets,
      calories_per_set: workout.calories
    };

    try {
      const res = await fetch("/api/workout/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      setTodayBurned(data.today_burned);
      setShowCharts(true);

      Swal.fire({
        icon: "success",
        title: "Workout Logged 🔥",
        html: `
          <b>Burned Today:</b> ${data.today_burned} kcal<br/>
          <b>Target:</b> ${targetCalories || "Not set"} kcal
        `,
        confirmButtonColor: "#22c55e"
      });
    } catch (err) {
      Swal.fire("Error", "❌ Error saving workout", "error");
    }
  }

  const pieData = {
    labels: ["Burned", "Remaining"],
    datasets: [
      {
        data: [
          todayBurned,
          Math.max(targetCalories - todayBurned, 0)
        ],
        backgroundColor: ["#22c55e", "#374151"]
      }
    ]
  };

  const barData = {
    labels: ["Calories"],
    datasets: [
      { label: "Target", data: [targetCalories], backgroundColor: "#3b82f6" },
      { label: "Burned", data: [todayBurned], backgroundColor: "#22c55e" }
    ]
  };

  return (
    <div className="workout-detail-page">
      <div className="workout-detail-glass">

        {/* HEADER */}
        <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>
        <h2>{name}</h2>

        {/* PRIMARY ACTION */}
        <input
          type="number"
          placeholder="Enter daily calorie target"
          value={targetCalories}
          onChange={(e) => setTargetCalories(e.target.value)}
          className="target-input"
        />

        <button className="complete-btn" onClick={handleComplete}>
          ✅ Mark as Completed
        </button>

        {/* DETAILS */}
        <div className="detail-row"><span>Target Muscle</span><span>{workout.muscle}</span></div>
        <div className="detail-row"><span>Sets</span><span>{workout.sets}</span></div>
        <div className="detail-row"><span>Reps / Time</span><span>{workout.reps}</span></div>
        <div className="detail-row"><span>Rest</span><span>{workout.rest}</span></div>
        <div className="detail-row"><span>Calories / Set</span><span>{workout.calories} kcal</span></div>
        <div className="detail-row"><span>Difficulty</span><span>{workout.difficulty}</span></div>

        {/* CHARTS */}
        {showCharts && targetCalories && (
          <div className="charts">
            <div className="chart-box"><Pie data={pieData} /></div>
            <div className="chart-box"><Bar data={barData} /></div>
          </div>
        )}

      </div>
    </div>
  );
}

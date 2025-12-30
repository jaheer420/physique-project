import React, { useEffect, useState } from "react";
import "./theme.css";
import "./App.css";

import {
  postLog,
  getTodaySummary,
  getWeeklySummary,
  fetchLogs,
  getMacroSummary,
  updateProfile
} from "./api";

import { Routes, Route, useNavigate } from "react-router-dom";
import WorkoutPage from "./components/WorkoutPage";
import Recommendation from "./components/Recommendation";
import WorkoutDetail from "./components/WorkoutDetail";

const USER_ID = 1;

// ===============================
// DASHBOARD
// ===============================
function Dashboard() {
  const navigate = useNavigate();

  const [text, setText] = useState("");
  const [today, setToday] = useState(null);
  const [weekly, setWeekly] = useState(null);
  const [logs, setLogs] = useState([]);
  const [macros, setMacros] = useState(null);

  const [profile, setProfile] = useState({
    age: 23,
    height_cm: 170,
    weight_kg: 68,
    gender: "male",
    activity_level: "moderate",
    goal: "loss"
  });

  const [showProfile, setShowProfile] = useState(false);

  // ===============================
  // THEME (NEW — SAFE)
  // ===============================
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "dark"
  );

  useEffect(() => {
    document.body.classList.toggle("theme-light", theme === "light");
    localStorage.setItem("theme", theme);
  }, [theme]);

  function toggleTheme() {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }

  // -------------------------------
  // REFRESH ALL DATA
  // -------------------------------
  async function refresh() {
    try {
      const todayRes = await getTodaySummary(USER_ID);
      setToday(todayRes);

      const weeklyRes = await getWeeklySummary(USER_ID);
      setWeekly(weeklyRes);

      const macroRes = await getMacroSummary(USER_ID);
      setMacros(macroRes);

      const logsRes = await fetchLogs(USER_ID);
      if (logsRes?.success) setLogs(logsRes.logs);
    } catch (err) {
      console.error("Refresh failed:", err);
    }
  }

  // -------------------------------
  // PROFILE SAVE
  // -------------------------------
  async function saveProfile() {
    await updateProfile({
      user_id: USER_ID,
      ...profile
    });
    refresh();
    setShowProfile(false);
  }

  // -------------------------------
  // FOOD LOG SUBMIT
  // -------------------------------
  async function submit() {
    if (!text.trim()) return;
    await postLog(USER_ID, text);
    setText("");
    refresh();
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="app-container">
      {/* HEADER + THEME TOGGLE */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 className="header">
          Physique<span className="needs">Needs</span>
        </h2>

        <button onClick={toggleTheme} style={{ height: 36 }}>
          {theme === "dark" ? "🌙 " : "🌞 "}
        </button>
      </div>

      {/* WORKOUT */}
      <button className="workout-btn" onClick={() => navigate("/workouts")}>
        💪 Explore Workouts
      </button>

      {/* PROFILE */}
      <div className="card info-card profile-toggle">
        <div
          className="profile-header"
          onClick={() => setShowProfile(!showProfile)}
        >
          <h3>Profile & Goal</h3>
          <span className={`chevron ${showProfile ? "open" : ""}`}>⌄</span>
        </div>

        <div className={`profile-body ${showProfile ? "show" : ""}`}>
          {[
            ["Age", "age"],
            ["Height (cm)", "height_cm"],
            ["Weight (kg)", "weight_kg"]
          ].map(([label, key]) => (
            <div className="profile-row" key={key}>
              <label>{label}</label>
              <input
                type="number"
                value={profile[key]}
                onChange={(e) =>
                  setProfile({ ...profile, [key]: Number(e.target.value) })
                }
              />
            </div>
          ))}

          <div className="profile-row">
            <label>Gender</label>
            <select
              value={profile.gender}
              onChange={(e) =>
                setProfile({ ...profile, gender: e.target.value })
              }
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div className="profile-row">
            <label>Activity Level</label>
            <select
              value={profile.activity_level}
              onChange={(e) =>
                setProfile({ ...profile, activity_level: e.target.value })
              }
            >
              <option value="sedentary">Sedentary</option>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="heavy">Heavy</option>
            </select>
          </div>

          <div className="profile-row">
            <label>Goal</label>
            <select
              value={profile.goal}
              onChange={(e) =>
                setProfile({ ...profile, goal: e.target.value })
              }
            >
              <option value="loss">Weight Loss</option>
              <option value="maintain">Maintain</option>
              <option value="gain">Weight Gain</option>
            </select>
          </div>

          <button onClick={saveProfile}>Save Profile</button>
        </div>
      </div>

      {/* FOOD ADVICE */}
      <button
        className="food-advice-btn"
        onClick={() => navigate("/recommendation")}
      >
        🥗 Food Advice
      </button>

      {/* FOOD INPUT */}
      <div className="food-input">
        <input
          placeholder="e.g. I ate 4 idlis"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button onClick={submit}>Add</button>
      </div>

      {/* TODAY */}
      {today && (
        <div className="card hero-card">
          <div className="kcal-big">
            {today.consumed ?? 0}
            <span className="kcal-unit"> kcal</span>
          </div>
          <div className="kcal-row">
            <span>Daily Target</span>
            <span>{today.daily_target ?? 0} kcal</span>
          </div>
          <div className="kcal-row">
            <span>Remaining</span>
            <span>{today.remaining ?? 0} kcal</span>
          </div>
        </div>
      )}

      {/* MACROS */}
      {macros && today && (
        <div className="card progress-card">
          <h3>Daily Macro Progress</h3>

          {["calories", "protein", "carbs", "fat"].map((m) => {
            const target =
              m === "calories"
                ? today.daily_target ?? 0
                : macros.targets?.[m] || 0;

            const consumed = macros.consumed?.[m] || 0;
            const progress =
              target > 0 ? Math.round((consumed / target) * 100) : 0;

            return (
              <div className="progress-wrap" key={m}>
                <div className="progress-label">
                  <span>{m.toUpperCase()}</span>
                  <span>
                    {consumed} / {target}
                  </span>
                </div>

                <div className="progress-bar">
                  <div
                    className={`progress-fill ${m} ${
                      progress > 100 ? "over-limit" : ""
                    }`}
                    style={{ width: `${Math.min(progress, 100)}%` }}
                  >
                    <span className="progress-text">{progress}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* WEEKLY */}
      {weekly && (
        <div className="card info-card">
          <h3>Weekly Summary</h3>
          <p className="weekly-status">
            Consistency: {weekly.consistency_percent}% — {weekly.status}
          </p>
        </div>
      )}

      {/* LOGS */}
      <div className="card info-card">
        <h3>Recent Logs</h3>
        {logs.length === 0 ? (
          <p className="muted">No logs yet</p>
        ) : (
          logs.map((l) => (
            <div key={l.id} className="muted">
              • {l.raw_text} —{" "}
              {JSON.parse(l.totals_json).totals.calories} kcal
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ===============================
// ROUTES
// ===============================
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/workouts" element={<WorkoutPage />} />
      <Route path="/workout/:name" element={<WorkoutDetail />} />
      <Route path="/recommendation" element={<Recommendation />} />
    </Routes>
  );
}

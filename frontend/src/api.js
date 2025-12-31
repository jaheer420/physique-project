// frontend/src/api.js

// ---------------- BACKEND BASE URL ----------------
// ✅ Use env variable, fallback to Render backend (SAFE)
const API_BASE =
  import.meta.env.VITE_API_URL ||
  "https://physique-backend1.onrender.com";

// ---------------- HELPER ----------------
async function safeJson(response) {
  try {
    return await response.json();
  } catch {
    return {};
  }
}

// ---------------------------------------------------
// POST: Add a new food log
// ---------------------------------------------------
export async function postLog(user_id, text) {
  try {
    const response = await fetch(`${API_BASE}/api/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id, text })
    });

    return await safeJson(response);
  } catch (error) {
    console.error("❌ postLog error:", error);
    return { success: false };
  }
}

// ---------------------------------------------------
// GET: Fetch last food logs (ALWAYS ARRAY)
// ---------------------------------------------------
export async function fetchLogs(user_id) {
  try {
    const response = await fetch(
      `${API_BASE}/api/logs?user_id=${user_id}`
    );

    const data = await safeJson(response);

    return {
      success: true,
      logs: Array.isArray(data.logs) ? data.logs : []
    };
  } catch (error) {
    console.error("❌ fetchLogs error:", error);
    return {
      success: false,
      logs: []
    };
  }
}

// ---------------------------------------------------
// POST: Update user profile
// ---------------------------------------------------
export async function updateProfile(profileData) {
  try {
    const response = await fetch(
      `${API_BASE}/api/profile/update`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileData)
      }
    );

    return await safeJson(response);
  } catch (error) {
    console.error("❌ updateProfile error:", error);
    return { success: false };
  }
}

// ---------------------------------------------------
// GET: Today summary
// ---------------------------------------------------
export async function getTodaySummary(user_id) {
  try {
    const response = await fetch(
      `${API_BASE}/api/summary/today/${user_id}`
    );

    return await safeJson(response);
  } catch (error) {
    console.error("❌ getTodaySummary error:", error);
    return null;
  }
}

// ---------------------------------------------------
// GET: Macro summary
// ---------------------------------------------------
export async function getMacroSummary(user_id) {
  try {
    const response = await fetch(
      `${API_BASE}/api/summary/macros/${user_id}`
    );

    return await safeJson(response);
  } catch (error) {
    console.error("❌ getMacroSummary error:", error);
    return null;
  }
}

// ---------------------------------------------------
// GET: Weekly summary
// ---------------------------------------------------
export async function getWeeklySummary(user_id) {
  try {
    const response = await fetch(
      `${API_BASE}/api/summary/weekly/${user_id}`
    );

    return await safeJson(response);
  } catch (error) {
    console.error("❌ getWeeklySummary error:", error);
    return null;
  }
}

// ---------------------------------------------------
// 🎯 TARGET-BASED FOOD RECOMMENDATION (POST)
// ---------------------------------------------------
export async function getTargetRecommendation(payload) {
  try {
    const response = await fetch(
      `${API_BASE}/api/recommend/target`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }
    );

    return await safeJson(response);
  } catch (error) {
    console.error("❌ getTargetRecommendation error:", error);
    return null;
  }
}

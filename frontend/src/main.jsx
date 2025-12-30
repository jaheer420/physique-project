import { StrictMode, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";
import "./theme.css";

/* ===============================
   GLOBAL THEME HANDLER (SAFE)
   =============================== */
function ThemeBootstrap({ children }) {
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") || "dark";

    // Apply theme globally
    document.body.classList.toggle(
      "theme-light",
      savedTheme === "light"
    );
  }, []);

  return children;
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ThemeBootstrap>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeBootstrap>
  </StrictMode>
);

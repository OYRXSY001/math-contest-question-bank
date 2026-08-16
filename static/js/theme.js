/**
 * Theme Toggle — 全息未来主题切换
 * 支持 dark / light / auto 三种模式
 * 偏好保存在 localStorage
 */
(function () {
  const STORAGE_KEY = "holo-theme";
  const THEMES = ["dark", "light", "auto"];
  const ICONS = { dark: "🌙", light: "☀️", auto: "🤖" };

  function getStoredTheme() {
    return localStorage.getItem(STORAGE_KEY) || "auto";
  }

  function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function getEffectiveTheme() {
    const stored = getStoredTheme();
    return stored === "auto" ? getSystemTheme() : stored;
  }

  function applyTheme() {
    const effective = getEffectiveTheme();
    document.documentElement.setAttribute("data-theme", effective);
  }

  function cycleTheme() {
    const current = getStoredTheme();
    const idx = THEMES.indexOf(current);
    const next = THEMES[(idx + 1) % THEMES.length];
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme();
    updateButton(next);
  }

  function updateButton(theme) {
    const btn = document.querySelector(".theme-toggle");
    if (btn) {
      btn.textContent = ICONS[theme] || ICONS.auto;
      btn.setAttribute(
        "aria-label",
        `主题模式：${theme === "dark" ? "暗色" : theme === "light" ? "亮色" : "跟随系统"}`
      );
    }
  }

  // Apply theme ASAP (before DOM ready to avoid flash)
  applyTheme();

  // Init on DOM ready
  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector(".theme-toggle");
    if (btn) {
      updateButton(getStoredTheme());
      btn.addEventListener("click", cycleTheme);
    }

    // Listen for system theme changes (only when in auto mode)
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    mql.addEventListener("change", () => {
      if (getStoredTheme() === "auto") {
        applyTheme();
      }
    });
  });
})();

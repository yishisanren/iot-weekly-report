(() => {
  const root = document.documentElement;
  const themeButton = document.getElementById("theme-toggle");

  const updateThemeButton = () => {
    if (!themeButton) return;
    const isDark = root.dataset.theme === "dark";
    const label = isDark ? "切换为日间模式" : "切换为暗黑模式";
    themeButton.setAttribute("aria-label", label);
    themeButton.setAttribute("title", label);
    themeButton.setAttribute("aria-pressed", String(isDark));
  };

  themeButton?.addEventListener("click", () => {
    const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
    root.dataset.theme = nextTheme;
    try {
      localStorage.setItem("iot-weekly-theme", nextTheme);
    } catch (_) {
      // The selected mode still applies for this page view when storage is unavailable.
    }
    updateThemeButton();
  });

  updateThemeButton();
})();

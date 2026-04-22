(function () {
  var storageKey = "agno-deep-agent-theme";
  var root = document.documentElement;
  var toggle = document.querySelector(".theme-toggle");

  function applyTheme(theme) {
    root.dataset.theme = theme;
    if (!toggle) {
      return;
    }
    var isDark = theme === "dark";
    toggle.textContent = isDark ? "Light" : "Dark";
    toggle.setAttribute("aria-pressed", String(isDark));
  }

  applyTheme(root.dataset.theme || "light");

  if (!toggle) {
    return;
  }

  toggle.addEventListener("click", function () {
    var nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
    try {
      localStorage.setItem(storageKey, nextTheme);
    } catch (error) {
      // Ignore storage errors and still switch the theme for this page view.
    }
    applyTheme(nextTheme);
  });
})();

(function () {
  const STORAGE_KEY = "infosec-notes-theme";
  const root = document.documentElement;

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
    return "light";
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      root.setAttribute("data-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
    }
    updateToggleLabel(theme);
  }

  function updateToggleLabel(theme) {
    const btn = document.querySelector(".theme-toggle");
    if (!btn) return;
    const isDark = theme === "dark";
    btn.setAttribute("aria-pressed", isDark ? "true" : "false");
    btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    const label = btn.querySelector(".theme-toggle-label");
    if (label) {
      label.textContent = isDark ? "Light mode" : "Dark mode";
    }
  }

  function toggleTheme() {
    const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  applyTheme(getPreferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector(".theme-toggle");
    if (btn) btn.addEventListener("click", toggleTheme);

    const tocLinks = document.querySelectorAll(".toc nav a[href^='#']");
    if (tocLinks.length && "IntersectionObserver" in window) {
      const sections = [];
      tocLinks.forEach(function (link) {
        const id = link.getAttribute("href").slice(1);
        const el = document.getElementById(id);
        if (el) sections.push({ id: id, el: el, link: link });
      });

      const observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              tocLinks.forEach(function (l) {
                l.classList.remove("active");
              });
              const match = sections.find(function (s) {
                return s.el === entry.target;
              });
              if (match) match.link.classList.add("active");
            }
          });
        },
        { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
      );

      sections.forEach(function (s) {
        observer.observe(s.el);
      });
    }
  });
})();

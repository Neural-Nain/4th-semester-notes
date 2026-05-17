(function () {
  const STORAGE_KEY = "infosec-notes-theme";
  const root = document.documentElement;

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
    return "dark";
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

  function initMobileNav() {
    const wrapper = document.querySelector(".page-wrapper");
    const sidebar = document.querySelector(".sidebar.toc");
    if (!wrapper || !sidebar) return;

    document.body.classList.add("has-toc-nav");
    wrapper.classList.add("has-toc-nav");
    sidebar.id = sidebar.id || "sidebar-nav";

    let toggle = document.querySelector(".nav-toggle");
    if (!toggle) {
      toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "nav-toggle";
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-controls", sidebar.id);
      toggle.setAttribute("aria-label", "Open page navigation");
      toggle.innerHTML =
        '<span class="nav-toggle-icon" aria-hidden="true">' +
        '<span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span>' +
        '</span><span class="nav-toggle-label">Menu</span>';
      const headerActions = document.querySelector(".header-actions");
      if (headerActions) {
        headerActions.insertBefore(toggle, headerActions.firstChild);
      } else {
        document.body.appendChild(toggle);
      }
    }

    let backdrop = document.querySelector(".nav-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("button");
      backdrop.type = "button";
      backdrop.className = "nav-backdrop";
      backdrop.setAttribute("aria-label", "Close navigation");
      backdrop.hidden = true;
      document.body.appendChild(backdrop);
    }

    function setOpen(open) {
      sidebar.classList.toggle("is-open", open);
      backdrop.classList.toggle("is-visible", open);
      backdrop.hidden = !open;
      document.body.classList.toggle("nav-menu-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close page navigation" : "Open page navigation");
    }

    function closeNav() {
      setOpen(false);
    }

    toggle.addEventListener("click", function () {
      setOpen(!sidebar.classList.contains("is-open"));
    });

    backdrop.addEventListener("click", closeNav);

    sidebar.querySelectorAll('nav a[href^="#"]').forEach(function (link) {
      link.addEventListener("click", closeNav);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && sidebar.classList.contains("is-open")) closeNav();
    });

    window.matchMedia("(min-width: 901px)").addEventListener("change", function (e) {
      if (e.matches) closeNav();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector(".theme-toggle");
    if (btn) btn.addEventListener("click", toggleTheme);

    initMobileNav();

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

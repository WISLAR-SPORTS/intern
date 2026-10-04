/* ==========================================================================
   InternConnect — home.js
   Vanilla JS — no build step.

   Features:
   - Theme toggle
   - Scroll spy
   - Sticky navbar shadow
   - Dual Leaflet maps
   - Django json_script data
   - University/company markers
   - Map search
   - University/company toggle
   - Newsletter form

   Leaflet must be loaded BEFORE this file:
     <link rel="stylesheet"
           href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

     <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
   ========================================================================== */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        initThemeToggle();
        initScrollSpy();
        initStickyNavShadow();
        initMaps();
        initNewsletterForm();
    });


    /* ======================================================================
       THEME TOGGLE
       ====================================================================== */

    function initThemeToggle() {
        var toggle = document.querySelector(".theme-toggle");

        if (!toggle) return;

        var STORAGE_KEY = "ic-theme";
        var root = document.documentElement;

        var saved = null;

        try {
            saved = localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            saved = null;
        }

        var prefersDark =
            window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: dark)").matches;

        var initialTheme = saved || (prefersDark ? "dark" : "light");

        applyTheme(initialTheme);

        toggle.addEventListener("click", function () {
            var current =
                root.getAttribute("data-theme") === "dark"
                    ? "dark"
                    : "light";

            var next = current === "dark" ? "light" : "dark";

            applyTheme(next);

            try {
                localStorage.setItem(STORAGE_KEY, next);
            } catch (e) {
                // Ignore localStorage errors.
            }
        });

        function applyTheme(theme) {
            if (theme === "dark") {
                root.setAttribute("data-theme", "dark");
            } else {
                root.removeAttribute("data-theme");
            }

            toggle.setAttribute(
                "aria-pressed",
                theme === "dark" ? "true" : "false"
            );
        }
    }


    /* ======================================================================
       SCROLL SPY
       ====================================================================== */

    function initScrollSpy() {
        var navLinks = Array.prototype.slice.call(
            document.querySelectorAll(".nav-links a")
        );

        if (!navLinks.length) return;

        var navbar = document.querySelector(".navbar");
        var navHeight = navbar ? navbar.offsetHeight : 0;

        var sections = navLinks
            .map(function (link) {
                var id = link.getAttribute("href");

                if (!id || id.charAt(0) !== "#") {
                    return null;
                }

                var element = document.querySelector(id);

                return element
                    ? {
                          link: link,
                          el: element
                      }
                    : null;
            })
            .filter(Boolean);

        if (!sections.length) return;

        navLinks.forEach(function (link) {
            link.addEventListener("click", function (event) {
                var id = link.getAttribute("href");

                if (!id || id.charAt(0) !== "#") {
                    return;
                }

                var target = document.querySelector(id);

                if (!target) {
                    return;
                }

                event.preventDefault();

                var top =
                    target.getBoundingClientRect().top +
                    window.pageYOffset -
                    navHeight -
                    12;

                window.scrollTo({
                    top: top,
                    behavior: "smooth"
                });

                history.pushState(null, "", id);
            });
        });

        if (!window.IntersectionObserver) {
            return;
        }

        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    var match = sections.find(function (section) {
                        return section.el === entry.target;
                    });

                    if (!match) {
                        return;
                    }

                    sections.forEach(function (section) {
                        section.link.classList.remove("active");
                    });

                    match.link.classList.add("active");
                });
            },
            {
                rootMargin:
                    "-" +
                    (navHeight + 40) +
                    "px 0px -60% 0px",
                threshold: 0
            }
        );

        sections.forEach(function (section) {
            observer.observe(section.el);
        });
    }


    /* ======================================================================
       STICKY NAV SHADOW
       ====================================================================== */

    function initStickyNavShadow() {
        var navbar = document.querySelector(".navbar");

        if (!navbar) return;

        function update() {
            if (window.scrollY > 8) {
                navbar.classList.add("is-scrolled");
            } else {
                navbar.classList.remove("is-scrolled");
            }
        }

        update();

        window.addEventListener("scroll", update, {
            passive: true
        });
    }



    /* ======================================================================
       NEWSLETTER
       ====================================================================== */

    function initNewsletterForm() {
        var form =
            document.querySelector(
                ".newsletter form"
            );

        if (!form) {
            return;
        }

        var input =
            form.querySelector(
                'input[type="email"]'
            );

        var button =
            form.querySelector("button");

        form.addEventListener(
            "submit",
            function (event) {
                event.preventDefault();

                if (!input || !input.value) {
                    return;
                }

                var originalLabel =
                    button
                        ? button.textContent
                        : "";

                setState("sending");

                var formData =
                    new FormData(form);

                fetch(
                    form.action,
                    {
                        method: "POST",
                        body: formData,
                        headers: {
                            "X-Requested-With":
                                "XMLHttpRequest"
                        }
                    }
                )
                    .then(
                        function (response) {
                            if (!response.ok) {
                                throw new Error(
                                    "Request failed"
                                );
                            }

                            setState(
                                "success"
                            );

                            form.reset();
                        }
                    )
                    .catch(
                        function () {
                            setState(
                                "error"
                            );
                        }
                    );


                function setState(
                    state
                ) {
                    clearMessage();

                    if (
                        state === "sending" &&
                        button
                    ) {
                        button.textContent =
                            "Subscribing…";

                        button.disabled =
                            true;
                    }


                    if (
                        state === "success"
                    ) {
                        showMessage(
                            "You're subscribed — welcome aboard.",
                            "success"
                        );

                        resetButton();
                    }


                    if (
                        state === "error"
                    ) {
                        showMessage(
                            "Something went wrong. Please try again.",
                            "error"
                        );

                        resetButton();
                    }
                }


                function resetButton() {
                    if (!button) {
                        return;
                    }

                    button.textContent =
                        originalLabel;

                    button.disabled =
                        false;
                }
            }
        );


        function clearMessage() {
            var existing =
                form.parentNode.querySelector(
                    ".newsletter-message"
                );

            if (existing) {
                existing.remove();
            }
        }


        function showMessage(
            text,
            kind
        ) {
            var message =
                document.createElement("p");

            message.className =
                "newsletter-message newsletter-message--" +
                kind;

            message.textContent =
                text;

            form.parentNode.appendChild(
                message
            );
        }
    }

})();

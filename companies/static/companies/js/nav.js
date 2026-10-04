
document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (!menuToggle || !navLinks) return;

    menuToggle.addEventListener("click", function () {
        navLinks.classList.toggle("mobile-open");

        const isOpen = navLinks.classList.contains("mobile-open");

        menuToggle.setAttribute(
            "aria-label",
            isOpen ? "Close navigation" : "Open navigation"
        );

        menuToggle.textContent = isOpen ? "✕" : "☰";
    });

    /* Close menu after clicking a link */
    navLinks.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            navLinks.classList.remove("mobile-open");
            menuToggle.textContent = "☰";
            menuToggle.setAttribute("aria-label", "Open navigation");
        });
    });

});


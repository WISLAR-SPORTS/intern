/* =========================================================
   INTERNCONNECT - BASE JAVASCRIPT
========================================================= */

(function () {
    "use strict";

    /* =====================================================
       DOM READY
    ===================================================== */

    document.addEventListener("DOMContentLoaded", function () {

        initializeLucideIcons();
        initializeTheme();
        initializeUserMenu();
        initializeMobileProfile();
        initializeProfileModal();
        initializeAIButton();
        initializeEscapeKey();
        initializeOutsideClick();

    });


    /* =====================================================
       LUCIDE ICONS
    ===================================================== */

    function initializeLucideIcons() {

        if (typeof lucide === "undefined") {
            return;
        }

        lucide.createIcons();
    }


    function refreshLucideIcons() {

        if (typeof lucide === "undefined") {
            return;
        }

        lucide.createIcons();
    }


    /* =====================================================
       THEME SYSTEM
    ===================================================== */

    const THEME_KEY = "internconnect-theme";


    function initializeTheme() {

        const themeToggle =
            document.getElementById("theme-toggle");

        const mobileThemeToggle =
            document.getElementById("mobile-theme-toggle");

        const currentTheme =
            localStorage.getItem(THEME_KEY);

        if (currentTheme === "dark") {

            setTheme("dark", false);

        } else {

            setTheme("light", false);

        }


        if (themeToggle) {

            themeToggle.addEventListener(
                "click",
                function () {

                    toggleTheme();

                }
            );

        }


        if (mobileThemeToggle) {

            mobileThemeToggle.addEventListener(
                "click",
                function () {

                    toggleTheme();

                }
            );

        }
    }


    function setTheme(theme, save = true) {

        if (theme === "dark") {

            document.documentElement.setAttribute(
                "data-theme",
                "dark"
            );

        } else {

            document.documentElement.removeAttribute(
                "data-theme"
            );

        }


        if (save) {

            localStorage.setItem(
                THEME_KEY,
                theme
            );

        }


        updateThemeButtons(theme);
    }


    function toggleTheme() {

        const currentTheme =
            document.documentElement.getAttribute(
                "data-theme"
            );

        const newTheme =
            currentTheme === "dark"
                ? "light"
                : "dark";

        setTheme(newTheme, true);
    }


    function updateThemeButtons(theme) {

        const isDark =
            theme === "dark";


        const themeToggle =
            document.getElementById("theme-toggle");

        const mobileThemeToggle =
            document.getElementById(
                "mobile-theme-toggle"
            );


        if (themeToggle) {

            themeToggle.setAttribute(
                "aria-pressed",
                String(isDark)
            );

            themeToggle.setAttribute(
                "aria-label",
                isDark
                    ? "Switch to light mode"
                    : "Switch to dark mode"
            );
        }


        if (mobileThemeToggle) {

            mobileThemeToggle.setAttribute(
                "aria-pressed",
                String(isDark)
            );

            mobileThemeToggle.setAttribute(
                "aria-label",
                isDark
                    ? "Switch to light mode"
                    : "Switch to dark mode"
            );


            const text =
                mobileThemeToggle.querySelector(
                    ".mobile-menu-text strong"
                );

            if (text) {

                text.textContent =
                    isDark
                        ? "Light Mode"
                        : "Dark Mode";
            }


            const description =
                mobileThemeToggle.querySelector(
                    ".mobile-menu-text small"
                );

            if (description) {

                description.textContent =
                    isDark
                        ? "Switch to light appearance"
                        : "Switch appearance";
            }
        }
    }


    /* =====================================================
       USER DROPDOWN
    ===================================================== */

    function initializeUserMenu() {

        const button =
            document.getElementById(
                "user-menu-button"
            );

        const dropdown =
            document.getElementById(
                "user-dropdown"
            );

        const wrapper =
            document.querySelector(
                ".user-menu-wrapper"
            );


        if (!button || !dropdown || !wrapper) {
            return;
        }


        button.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                const isOpen =
                    button.getAttribute(
                        "aria-expanded"
                    ) === "true";

                if (isOpen) {

                    closeUserMenu();

                } else {

                    openUserMenu();

                }
            }
        );
    }


    function openUserMenu() {

        const button =
            document.getElementById(
                "user-menu-button"
            );

        const wrapper =
            document.querySelector(
                ".user-menu-wrapper"
            );


        if (!button || !wrapper) {
            return;
        }


        button.setAttribute(
            "aria-expanded",
            "true"
        );

        wrapper.classList.add("open");
    }


    function closeUserMenu() {

        const button =
            document.getElementById(
                "user-menu-button"
            );

        const wrapper =
            document.querySelector(
                ".user-menu-wrapper"
            );


        if (!button || !wrapper) {
            return;
        }


        button.setAttribute(
            "aria-expanded",
            "false"
        );

        wrapper.classList.remove("open");
    }


    /* =====================================================
       MOBILE PROFILE SHEET
    ===================================================== */

    function initializeMobileProfile() {

        const profileButton =
            document.getElementById(
                "mobile-profile-button"
            );

        const profileSheet =
            document.getElementById(
                "mobile-profile-sheet"
            );


        if (!profileButton || !profileSheet) {
            return;
        }


        profileButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                openMobileProfileSheet();

            }
        );


        const overlay =
            profileSheet.querySelector(
                ".mobile-sheet-overlay"
            );


        if (overlay) {

            overlay.addEventListener(
                "click",
                function () {

                    closeMobileProfileSheet();

                }
            );

        }
    }


    function openMobileProfileSheet() {

        const sheet =
            document.getElementById(
                "mobile-profile-sheet"
            );


        if (!sheet) {
            return;
        }


        sheet.classList.add("active");

        document.body.style.overflow = "hidden";

        closeUserMenu();
    }


    function closeMobileProfileSheet() {

        const sheet =
            document.getElementById(
                "mobile-profile-sheet"
            );


        if (!sheet) {
            return;
        }


        sheet.classList.remove("active");

        if (!isAnyOverlayOpen()) {

            document.body.style.overflow = "";

        }
    }


    /* =====================================================
       PROFILE MODAL
    ===================================================== */

    function initializeProfileModal() {

        const modal =
            document.getElementById(
                "profileModal"
            );


        if (!modal) {
            return;
        }


        modal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === modal ||
                    event.target.classList.contains(
                        "profile-modal-overlay"
                    )
                ) {

                    closeProfileModal();

                }
            }
        );
    }


    window.openProfileModal =
        function () {

            const modal =
                document.getElementById(
                    "profileModal"
                );


            if (!modal) {
                return;
            }


            closeUserMenu();
            closeMobileProfileSheet();


            modal.classList.add("active");

            document.body.style.overflow = "hidden";


            refreshLucideIcons();

        };


    window.closeProfileModal =
        function () {

            const modal =
                document.getElementById(
                    "profileModal"
                );


            if (!modal) {
                return;
            }


            modal.classList.remove("active");


            if (!isAnyOverlayOpen()) {

                document.body.style.overflow = "";

            }
        };


    /* =====================================================
       AI ASSISTANT
    ===================================================== */

    function initializeAIButton() {

        const aiButton =
            document.getElementById(
                "ai-toggle"
            );


        if (!aiButton) {
            return;
        }


        aiButton.addEventListener(
            "click",
            function () {

                openAIAssistant();

            }
        );
    }


    function openAIAssistant() {

        /*
         * IMPORTANT:
         *
         * Your current template does not contain
         * an AI chat panel/modal.
         *
         * Therefore, this function safely redirects
         * to your existing Django AI chat URL.
         */


        const aiLink =
            document.querySelector(
                'a[href*="ai_chat"]'
            );


        if (aiLink) {

            window.location.href =
                aiLink.href;

            return;
        }


        console.warn(
            "AI Assistant link was not found."
        );
    }


    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    function initializeEscapeKey() {

        document.addEventListener(
            "keydown",
            function (event) {

                if (event.key !== "Escape") {
                    return;
                }


                closeUserMenu();
                closeMobileProfileSheet();
                closeProfileModal();

            }
        );
    }


    /* =====================================================
       OUTSIDE CLICK
    ===================================================== */

    function initializeOutsideClick() {

        document.addEventListener(
            "click",
            function (event) {

                const wrapper =
                    document.querySelector(
                        ".user-menu-wrapper"
                    );


                if (
                    wrapper &&
                    !wrapper.contains(event.target)
                ) {

                    closeUserMenu();

                }
            }
        );
    }


    /* =====================================================
       OVERLAY STATE
    ===================================================== */

    function isAnyOverlayOpen() {

        const mobileSheet =
            document.getElementById(
                "mobile-profile-sheet"
            );

        const profileModal =
            document.getElementById(
                "profileModal"
            );


        const mobileOpen =
            mobileSheet &&
            mobileSheet.classList.contains(
                "active"
            );


        const modalOpen =
            profileModal &&
            profileModal.classList.contains(
                "active"
            );


        return Boolean(
            mobileOpen || modalOpen
        );
    }


    /* =====================================================
       PREVENT BODY SCROLL WHEN DROPDOWN IS OPEN
       ONLY FOR MOBILE SHEETS / MODALS
    ===================================================== */

    window.addEventListener(
        "resize",
        function () {

            /*
             * If the screen becomes desktop while
             * the mobile profile sheet is open,
             * close it.
             */

            if (
                window.innerWidth > 768
            ) {

                closeMobileProfileSheet();

            }
        }
    );


    /* =====================================================
       IMAGE FALLBACK
    ===================================================== */

    document.addEventListener(
        "error",
        function (event) {

            const image =
                event.target;


            if (
                image &&
                image.tagName === "IMG"
            ) {

                /*
                 * Avoid repeatedly triggering
                 * the error handler.
                 */

                if (
                    image.dataset.fallbackApplied
                ) {

                    return;

                }


                image.dataset.fallbackApplied =
                    "true";


                image.style.display =
                    "none";
            }

        },
        true
    );


    /* =====================================================
       GLOBAL HELPERS
    ===================================================== */

    window.InternConnect = {

        openUserMenu: openUserMenu,

        closeUserMenu: closeUserMenu,

        openMobileProfileSheet:
            openMobileProfileSheet,

        closeMobileProfileSheet:
            closeMobileProfileSheet,

        openProfileModal:
            window.openProfileModal,

        closeProfileModal:
            window.closeProfileModal,

        toggleTheme:
            toggleTheme,

        setTheme:
            setTheme

    };

})();

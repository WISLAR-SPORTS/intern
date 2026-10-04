document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("consent-form");
    const checkbox = document.getElementById("accept-checkbox");
    const button = document.getElementById("accept-button");
    const error = document.getElementById("consent-error");

    // --------------------------------------
    // Make sure required elements exist
    // --------------------------------------

    if (!form || !checkbox || !button) {
        console.error("Consent form elements not found.");
        return;
    }

    // --------------------------------------
    // Get submit URL from data attribute
    // --------------------------------------

    const submitUrl = form.dataset.submitUrl;

    if (!submitUrl) {
        console.error("Consent submit URL is missing.");
        return;
    }

    // --------------------------------------
    // Enable button only when checkbox is checked
    // --------------------------------------

    checkbox.addEventListener("change", function () {

        button.disabled = !checkbox.checked;

    });

    // --------------------------------------
    // Submit consent
    // --------------------------------------

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        // ----------------------------------
        // Make sure user accepted
        // ----------------------------------

        if (!checkbox.checked) {

            if (error) {
                error.textContent =
                    "You must accept the Terms and Conditions and Privacy Policy.";
            }

            return;
        }

        // ----------------------------------
        // Disable button while saving
        // ----------------------------------

        button.disabled = true;
        button.textContent = "Saving...";

        if (error) {
            error.textContent = "";
        }

        // ----------------------------------
        // Get CSRF token
        // ----------------------------------

        const csrfToken = getCookie("csrftoken");

        if (!csrfToken) {

            console.error("CSRF token not found.");

            if (error) {
                error.textContent =
                    "Security token missing. Please refresh the page and try again.";
            }

            button.disabled = false;
            button.textContent = "Accept and Continue";

            return;
        }

        // ----------------------------------
        // Prepare form data
        // ----------------------------------

        const formData = new FormData(form);

        try {

            const response = await fetch(
                submitUrl,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json"
                    },

                    body: formData,

                    credentials: "same-origin"
                }
            );

            // ----------------------------------
            // Read response safely
            // ----------------------------------

            const contentType =
                response.headers.get("content-type") || "";

            let data = {};

            if (contentType.includes("application/json")) {

                data = await response.json();

            } else {

                throw new Error(
                    "The server returned an unexpected response."
                );
            }

            // ----------------------------------
            // Handle backend errors
            // ----------------------------------

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Unable to save consent."
                );
            }

            // ----------------------------------
            // Consent successfully saved
            // ----------------------------------

            if (data.success) {

                /*
                 * Prefer the URL supplied by Django.
                 *
                 * This is safer than trusting a "next"
                 * parameter from the browser.
                 */

                if (data.redirect_url) {

                    window.location.href =
                        data.redirect_url;

                    return;
                }

                // Fallback
                window.location.href = "/";

                return;
            }

            throw new Error(
                data.error ||
                "Consent was not saved."
            );

        } catch (err) {

            console.error(
                "Consent error:",
                err
            );

            if (error) {

                error.textContent =
                    err.message ||
                    "Something went wrong. Please try again.";

            }

            button.disabled = false;

            button.textContent =
                "Accept and Continue";
        }

    });

    // --------------------------------------
    // Django CSRF cookie helper
    // --------------------------------------

    function getCookie(name) {

        const cookies =
            document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (
                cookie.startsWith(name + "=")
            ) {

                return decodeURIComponent(
                    cookie.substring(
                        name.length + 1
                    )
                );

            }

        }

        return null;
    }

});

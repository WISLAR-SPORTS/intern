(function () {

    window.openApplicationFile = function (previewId) {

        const overlay = document.getElementById(previewId);

        if (!overlay) {
            console.error(
                "Application file overlay not found:",
                previewId
            );

            return;
        }

        overlay.style.display = "flex";

        document.body.style.overflow = "hidden";
    };


    window.closeApplicationFile = function (previewId) {

        const overlay = document.getElementById(previewId);

        if (!overlay) {
            return;
        }

        overlay.style.display = "none";

        document.body.style.overflow = "";
    };


    // --------------------------------------------------------
    // ESC KEY CLOSES OVERLAY
    // --------------------------------------------------------

    document.addEventListener("keydown", function (event) {

        if (event.key !== "Escape") {
            return;
        }

        const overlays = document.querySelectorAll(
            ".application-file-overlay"
        );

        overlays.forEach(function (overlay) {

            if (overlay.style.display === "flex") {

                overlay.style.display = "none";

                document.body.style.overflow = "";

            }

        });

    });

})();


document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("internshipSearch");
    const typeFilter = document.getElementById("typeFilter");
    const internshipGrid = document.getElementById("internshipGrid");
    const noResults = document.getElementById("noResults");

    if (!searchInput || !typeFilter || !internshipGrid) {
        return;
    }

    const cards = internshipGrid.querySelectorAll(".internship-card");

    function filterInternships() {

        const searchTerm = searchInput.value
            .trim()
            .toLowerCase();

        const selectedType = typeFilter.value
            .trim()
            .toLowerCase();

        let visibleCount = 0;

        cards.forEach(function (card) {

            const title = card.dataset.title || "";
            const company = card.dataset.company || "";
            const type = card.dataset.type || "";

            const matchesSearch =
                title.includes(searchTerm) ||
                company.includes(searchTerm);

            const matchesType =
                selectedType === "" ||
                type === selectedType;

            const shouldShow =
                matchesSearch && matchesType;

            card.style.display = shouldShow
                ? ""
                : "none";

            if (shouldShow) {
                visibleCount++;
            }

        });

        if (noResults) {
            noResults.style.display =
                visibleCount === 0
                    ? "block"
                    : "none";
        }

    }

    searchInput.addEventListener(
        "input",
        filterInternships
    );

    typeFilter.addEventListener(
        "change",
        filterInternships
    );

});


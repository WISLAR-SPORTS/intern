

const internshipSearchInput =
    document.getElementById("internshipSearch");

const internshipTypeFilter =
    document.getElementById("typeFilter");

const internshipCards =
    document.querySelectorAll(".internship-card");


function filterInternships() {

    if (
        !internshipSearchInput ||
        !internshipTypeFilter
    ) {
        return;
    }


    const search =
        internshipSearchInput.value
            .toLowerCase()
            .trim();

    const type =
        internshipTypeFilter.value
            .toLowerCase()
            .trim();


    internshipCards.forEach(card => {

        const title =
            (card.dataset.title || "")
                .toLowerCase();

        const company =
            (card.dataset.company || "")
                .toLowerCase();

        const cardType =
            (card.dataset.type || "")
                .toLowerCase();


        const matchesSearch =
            title.includes(search) ||
            company.includes(search);


        const matchesType =
            !type ||
            cardType === type;


        card.style.display =
            matchesSearch && matchesType
                ? ""
                : "none";

    });

}


/* =========================================
   SEARCH
========================================= */

if (internshipSearchInput) {

    internshipSearchInput.addEventListener(
        "input",
        filterInternships
    );

}


/* =========================================
   TYPE FILTER
========================================= */

if (internshipTypeFilter) {

    internshipTypeFilter.addEventListener(
        "change",
        filterInternships
    );

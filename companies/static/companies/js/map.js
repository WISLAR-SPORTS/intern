/* ======================================================================
   MAPS
   ====================================================================== */

function initMaps() {

    var universityMapEl = document.getElementById("university-map");
    var companyMapEl = document.getElementById("company-map");

    if (!universityMapEl && !companyMapEl) {
        return;
    }

    /*
     * Make sure Leaflet is loaded.
     */
    if (typeof window.L === "undefined") {
        console.error(
            "InternConnect: Leaflet is not loaded."
        );
        return;
    }

    /*
     * Read Django JSON.
     */
    var universities = readJSON("universities-data");
    var companies = readJSON("companies-data");

    /*
     * Create university map.
     */
    var universityMap = universityMapEl
        ? buildMap(
            universityMapEl,
            universities,
            "#7C3AED"
        )
        : null;

    /*
     * Create company map.
     */
    var companyMap = companyMapEl
        ? buildMap(
            companyMapEl,
            companies,
            "#F59E0B"
        )
        : null;

    /*
     * Search.
     */
    wireSearch(
        "university-search",
        universityMap
    );

    wireSearch(
        "company-search",
        companyMap
    );

    /*
     * University/company toggle.
     */
    wireNetworkToggle(
        universityMap,
        companyMap
    );

    /*
     * Make sure maps are correctly sized
     * after the browser finishes rendering.
     */
    setTimeout(function () {

        if (universityMap) {
            universityMap.invalidateSize(true);
        }

        if (companyMap) {
            companyMap.invalidateSize(true);
        }

    }, 300);
}


/* ======================================================================
   READ JSON FROM DJANGO
   ====================================================================== */

function readJSON(elementId) {

    var element = document.getElementById(elementId);

    if (!element) {
        console.warn(
            "InternConnect: JSON element not found:",
            elementId
        );

        return [];
    }

    try {

        var data = JSON.parse(
            element.textContent
        );

        if (!Array.isArray(data)) {

            console.warn(
                "InternConnect: Expected an array in #" +
                elementId
            );

            return [];
        }

        return data;

    } catch (error) {

        console.error(
            "InternConnect: Invalid JSON in #" +
            elementId,
            error
        );

        return [];
    }
}


/* ======================================================================
   GET DISPLAY NAME
   ====================================================================== */

function getLabel(item) {

    return (
        item.company_name ||
        item.university_name ||
        item.name ||
        item.title ||
        "Location"
    );
}


/* ======================================================================
   GET LOCATION TEXT
   ====================================================================== */

function getLocationText(item) {

    return (
        item.location ||
        item.city ||
        item.address ||
        ""
    );
}


/* ======================================================================
   GET LATITUDE / LONGITUDE
   ====================================================================== */

function getLatLng(item) {

    var lat =
        item.latitude != null
            ? item.latitude
            : item.lat;

    var lng =
        item.longitude != null
            ? item.longitude
            : item.lng;

    lat = parseFloat(lat);
    lng = parseFloat(lng);

    if (!Number.isFinite(lat)) {
        return null;
    }

    if (!Number.isFinite(lng)) {
        return null;
    }

    if (lat < -90 || lat > 90) {
        return null;
    }

    if (lng < -180 || lng > 180) {
        return null;
    }

    return [lat, lng];
}


/* ======================================================================
   BUILD MAP
   ====================================================================== */

function buildMap(container, items, accentColor) {

    if (!container) {
        return null;
    }

    /*
     * Prevent duplicate initialization.
     */
    if (container._leaflet_id) {

        console.warn(
            "InternConnect: Map already initialized:",
            container.id
        );

        return container.__internConnectMap || null;
    }


    console.log(
        "InternConnect: Building map:",
        container.id
    );

    console.log(
        "InternConnect: Items:",
        items
    );


    /*
     * Create Leaflet map.
     */
    var map = L.map(container, {

        center: [
            0.3476,
            32.5825
        ],

        zoom: 7,

        minZoom: 5,

        maxZoom: 18,

        scrollWheelZoom: false,

        zoomControl: true,

        attributionControl: true

    });


    /*
     * Store map on container.
     */
    container.__internConnectMap = map;


    /*
     * OpenStreetMap tiles.
     *
     * No API key required.
     */
  var tileLayer = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    {
        maxZoom: 19,
        attribution:
            "Tiles &copy; Esri"
    }
).addTo(map);

tileLayer.on("tileload", function (event) {
    console.log("ESRI TILE LOADED:", event.tile.src);
});

tileLayer.on("tileerror", function (event) {
    console.error(
        "ESRI TILE FAILED:",
        event.tile ? event.tile.src : event
    );
});


    /*
     * Marker collection.
     */
    var markers = [];


    /*
     * Create markers.
     */
    items.forEach(function (item) {

        var coords = getLatLng(item);

        if (!coords) {

            console.warn(
                "InternConnect: Invalid coordinates:",
                item
            );

            return;
        }


        var label = String(
            getLabel(item)
        );

        var location = String(
            getLocationText(item) || ""
        );


        /*
         * Custom marker.
         */
        var markerIcon = L.divIcon({

            className:
                "ic-map-marker-label",

            html:

                '<div class="map-marker-wrapper">' +

                    '<span ' +
                        'class="map-marker-dot" ' +
                        'style="background:' +
                        escapeHTML(accentColor) +
                        ';">' +
                    '</span>' +

                    '<span class="map-marker-name">' +
                        escapeHTML(label) +
                    '</span>' +

                '</div>',

            iconSize: [
                220,
                42
            ],

            iconAnchor: [
                8,
                21
            ],

            popupAnchor: [
                0,
                -21
            ]

        });


        /*
         * Add marker.
         */
        var marker = L.marker(
            coords,
            {
                icon: markerIcon
            }
        ).addTo(map);


        /*
         * Popup.
         */
        var popupHTML =
            "<strong>" +
            escapeHTML(label) +
            "</strong>";


        if (location) {

            popupHTML +=
                "<br>" +
                escapeHTML(location);
        }


        marker.bindPopup(
            popupHTML
        );


        /*
         * Search metadata.
         */
        marker.__label =
            label.toLowerCase();


        marker.__location =
            location.toLowerCase();


        marker.__item =
            item;


        markers.push(marker);

    });


    /*
     * Store markers.
     */
    map.__markers = markers;


    /*
     * Fit map to markers.
     */
    fitToMarkers(
        map,
        markers
    );


    /*
     * Give Leaflet another chance to
     * calculate the container size.
     */
    setTimeout(
        function () {

            if (map) {
                map.invalidateSize(true);

                fitToMarkers(
                    map,
                    markers
                );
            }

        },
        250
    );


    setTimeout(
        function () {

            if (map) {
                map.invalidateSize(true);
            }

        },
        800
    );


    /*
     * Browser resize.
     */
    window.addEventListener(
        "resize",
        function () {

            if (!map) {
                return;
            }

            map.invalidateSize(true);

        },
        {
            passive: true
        }
    );


    /*
     * Return map.
     */
    return map;
}


/* ======================================================================
   FIT MAP TO MARKERS
   ====================================================================== */

function fitToMarkers(map, markers) {

    if (!map) {
        return;
    }


    /*
     * No markers.
     */
    if (!markers || !markers.length) {

        map.setView(
            [
                0.3476,
                32.5825
            ],
            7
        );

        return;
    }


    /*
     * One marker.
     */
    if (markers.length === 1) {

        var position =
            markers[0].getLatLng();

        map.setView(
            [
                position.lat,
                position.lng
            ],
            14
        );

        return;
    }


    /*
     * Multiple markers.
     */
    var group =
        L.featureGroup(markers);


    if (!group.getBounds().isValid()) {

        map.setView(
            [
                0.3476,
                32.5825
            ],
            7
        );

        return;
    }


    map.fitBounds(
        group.getBounds(),
        {
            padding: [
                50,
                50
            ],

            maxZoom: 14
        }
    );
}


/* ======================================================================
   MAP SEARCH
   ====================================================================== */

function wireSearch(inputId, map) {

    var input =
        document.getElementById(
            inputId
        );


    if (!input || !map) {
        return;
    }


    var timer = null;


    input.addEventListener(
        "input",
        function () {

            clearTimeout(timer);


            timer = setTimeout(
                function () {

                    applyFilter(
                        map,
                        input.value
                    );

                },
                200
            );

        }
    );
}


/* ======================================================================
   APPLY MAP SEARCH FILTER
   ====================================================================== */

function applyFilter(map, query) {

    if (!map) {
        return;
    }


    var term =
        String(query)
            .trim()
            .toLowerCase();


    var markers =
        map.__markers || [];


    var visible = [];


    markers.forEach(
        function (marker) {

            var matches =

                term === "" ||

                marker.__label.indexOf(
                    term
                ) !== -1 ||

                (
                    marker.__location &&
                    marker.__location.indexOf(
                        term
                    ) !== -1
                );


            var onMap =
                map.hasLayer(marker);


            if (matches && !onMap) {

                marker.addTo(map);

            }


            if (!matches && onMap) {

                map.removeLayer(marker);

            }


            if (matches) {

                visible.push(
                    marker
                );

            }

        }
    );


    /*
     * Empty search.
     */
    if (!term) {

        fitToMarkers(
            map,
            markers
        );

        return;
    }


    /*
     * Matching results.
     */
    if (visible.length) {

        fitToMarkers(
            map,
            visible
        );

        return;
    }


    /*
     * No results.
     *
     * Keep current map position.
     */
}


/* ======================================================================
   UNIVERSITY / COMPANY TOGGLE
   ====================================================================== */

function wireNetworkToggle(
    universityMap,
    companyMap
) {

    var buttons =
        document.querySelectorAll(
            ".network-toggle button"
        );


    if (!buttons.length) {
        return;
    }


    var grid =
        document.querySelector(
            ".maps-grid"
        );


    var universityCard =
        document.querySelector(
            '[data-map-panel="universities"]'
        );


    var companyCard =
        document.querySelector(
            '[data-map-panel="companies"]'
        );


    /*
     * If the cards don't have data-map-panel,
     * find them by map element.
     */
    if (!universityCard) {

        var universityEl =
            document.getElementById(
                "university-map"
            );

        universityCard =
            universityEl
                ? universityEl.closest(
                    ".map-card"
                )
                : null;
    }


    if (!companyCard) {

        var companyEl =
            document.getElementById(
                "company-map"
            );

        companyCard =
            companyEl
                ? companyEl.closest(
                    ".map-card"
                )
                : null;
    }


    /*
     * Update visible map.
     */
    function showMap(target) {

        var isUniversity =
            target === "universities";


        /*
         * Active button.
         */
        buttons.forEach(
            function (button) {

                var buttonTarget =
                    button.getAttribute(
                        "data-map"
                    );


                button.classList.toggle(
                    "active",
                    buttonTarget === target
                );

            }
        );


        /*
         * Desktop:
         *
         * Both maps remain visible.
         *
         * Mobile:
         *
         * Only selected map is visible.
         */
        if (grid) {

            grid.classList.toggle(
                "show-universities",
                isUniversity
            );


            grid.classList.toggle(
                "show-companies",
                !isUniversity
            );

        }


        /*
         * On small screens, control
         * map-card visibility.
         */
        if (
            window.matchMedia(
                "(max-width: 767px)"
            ).matches
        ) {

            if (universityCard) {

                universityCard.classList.toggle(
                    "active-map",
                    isUniversity
                );

            }


            if (companyCard) {

                companyCard.classList.toggle(
                    "active-map",
                    !isUniversity
                );

            }

        } else {

            /*
             * Desktop always shows both.
             */
            if (universityCard) {

                universityCard.classList.add(
                    "active-map"
                );

            }


            if (companyCard) {

                companyCard.classList.add(
                    "active-map"
                );

            }

        }


        /*
         * Refresh selected map after
         * layout has changed.
         */
        var selectedMap =
            isUniversity
                ? universityMap
                : companyMap;


        if (!selectedMap) {
            return;
        }


        setTimeout(
            function () {

                selectedMap.invalidateSize(
                    true
                );


                fitToMarkers(
                    selectedMap,
                    selectedMap.__markers ||
                    []
                );

            },
            150
        );


        setTimeout(
            function () {

                selectedMap.invalidateSize(
                    true
                );

            },
            500
        );

    }


    /*
     * Button events.
     */
    buttons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    var target =
                        button.getAttribute(
                            "data-map"
                        );


                    if (
                        target !==
                            "universities" &&
                        target !==
                            "companies"
                    ) {

                        return;
                    }


                    showMap(
                        target
                    );

                }
            );

        }
    );


    /*
     * Initial state.
     */
    showMap(
        "universities"
    );


    /*
     * If browser changes between
     * mobile and desktop.
     */
    window.addEventListener(
        "resize",
        function () {

            var isMobile =
                window.matchMedia(
                    "(max-width: 767px)"
                ).matches;


            if (!isMobile) {

                if (universityCard) {

                    universityCard.classList.add(
                        "active-map"
                    );

                }


                if (companyCard) {

                    companyCard.classList.add(
                        "active-map"
                    );

                }

            }

            else {

                var activeButton =
                    document.querySelector(
                        ".network-toggle button.active"
                    );


                var target =
                    activeButton
                        ? activeButton.getAttribute(
                            "data-map"
                        )
                        : "universities";


                if (universityCard) {

                    universityCard.classList.toggle(
                        "active-map",
                        target ===
                            "universities"
                    );

                }


                if (companyCard) {

                    companyCard.classList.toggle(
                        "active-map",
                        target ===
                            "companies"
                    );

                }

            }


            setTimeout(
                function () {

                    if (universityMap) {

                        universityMap.invalidateSize(
                            true
                        );

                    }


                    if (companyMap) {

                        companyMap.invalidateSize(
                            true
                        );

                    }

                },
                150
            );

        },
        {
            passive: true
        }
    );
}


/* ======================================================================
   ESCAPE HTML
   ====================================================================== */

function escapeHTML(value) {

    var div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value);


    return div.innerHTML;
}

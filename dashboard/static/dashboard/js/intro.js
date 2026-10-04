/* =====================================================
   INTERNSHIP CONNECT
   AUTOMATED INTRODUCTION
===================================================== */


/* =====================================================
   ELEMENTS
===================================================== */

const intro =
    document.getElementById("intro");

const progressBar =
    document.getElementById("progressBar");

const percentage =
    document.getElementById("percentage");

const statusMessage =
    document.getElementById("statusMessage");

const enterButton =
    document.getElementById("enterButton");

const particlesContainer =
    document.getElementById("particles");


/* =====================================================
   SAFETY CHECK
===================================================== */

/*
   Prevent JavaScript errors if an element
   is missing from the HTML.
*/

if (!intro) {
    console.error("Intro container not found.");
}


/* =====================================================
   PARTICLE GENERATOR
===================================================== */

function createParticles() {

    if (!particlesContainer) {
        return;
    }

    const particleCount = 45;

    for (
        let i = 0;
        i < particleCount;
        i++
    ) {

        const particle =
            document.createElement("span");


        particle.classList.add(
            "particle"
        );


        /* Random horizontal position */

        particle.style.left =
            Math.random() * 100 + "%";


        /* Random vertical position */

        particle.style.top =
            Math.random() * 100 + "%";


        /* Random animation duration */

        particle.style.setProperty(
            "--duration",
            (4 + Math.random() * 7) + "s"
        );


        /* Random animation delay */

        particle.style.animationDelay =
            Math.random() * 5 + "s";


        /* Random particle size */

        const size =
            1 + Math.random() * 3;

        particle.style.width =
            size + "px";

        particle.style.height =
            size + "px";


        particlesContainer.appendChild(
            particle
        );
    }
}


/* =====================================================
   START PARTICLES
===================================================== */

createParticles();


/* =====================================================
   LOADING SEQUENCE
===================================================== */

/*
   The loading messages now match the
   slower visual introduction.

   Total visual sequence:
   
   0.0s  Student
   1.5s  Company
   3.0s  University
   4.5s  Internship
   9.5s  All cards finished
   12s   Redirect
*/

const loadingSteps = [

    {
        percent: 10,
        message: "Initializing platform..."
    },

    {
        percent: 20,
        message: "Connecting student ecosystem..."
    },

    {
        percent: 35,
        message: "Connecting companies..."
    },

    {
        percent: 50,
        message: "Synchronizing universities..."
    },

    {
        percent: 65,
        message: "Mapping internship opportunities..."
    },

    {
        percent: 80,
        message: "Preparing digital logbook..."
    },

    {
        percent: 92,
        message: "Finalizing internship ecosystem..."
    },

    {
        percent: 100,
        message: "Platform ready."
    }

];


let currentStep = 0;


/* =====================================================
   UPDATE PROGRESS
===================================================== */

function updateProgress() {

    if (
        currentStep >=
        loadingSteps.length
    ) {

        return;
    }


    const step =
        loadingSteps[currentStep];


    if (progressBar) {

        progressBar.style.width =
            step.percent + "%";
    }


    if (percentage) {

        percentage.textContent =
            step.percent + "%";
    }


    if (statusMessage) {

        statusMessage.textContent =
            step.message;
    }


    currentStep++;


    /*
       Slower timing.

       This prevents the progress bar from
       reaching 100% while the cards are
       still falling.
    */

    const delay =
        850;


    setTimeout(
        updateProgress,
        delay
    );
}


/* =====================================================
   START PROGRESS
===================================================== */

setTimeout(
    updateProgress,
    700
);


/* =====================================================
   REDIRECT CONTROL
===================================================== */

let hasRedirected = false;


/* =====================================================
   ENTER PLATFORM
===================================================== */

function enterPlatform() {

    /*
       Prevent multiple redirects.

       This is important because the user
       can click the button while the
       automatic redirect timer is active.
    */

    if (hasRedirected) {

        return;
    }


    hasRedirected = true;


    /*
       Disable the button after activation.
    */

    if (enterButton) {

        enterButton.disabled =
            true;

        enterButton.style.pointerEvents =
            "none";
    }


    /*
       Change the status message.
    */

    if (statusMessage) {

        statusMessage.textContent =
            "Launching platform...";
    }


    if (percentage) {

        percentage.textContent =
            "100%";
    }


    if (progressBar) {

        progressBar.style.width =
            "100%";
    }


    /*
       Start page exit animation.
    */

    if (intro) {

        intro.classList.add(
            "is-exiting"
        );
    }


    /*
       Give the exit animation time
       to complete before redirecting.
    */

    setTimeout(
        function () {

       

            if (
                typeof loginUrl !==
                "undefined"
            ) {

                window.location.href =
                    loginUrl;

            } else {

                /*
                   Fallback in case the
                   Django variable is missing.
                */

                window.location.href =
                    "/home/";
            }

        },
        800
    );
}


/* =====================================================
   AUTOMATIC LAUNCH
===================================================== */

/*
   IMPORTANT:

   The slowest card starts at:

       4.5 seconds

   Its animation lasts:

       5 seconds

   Therefore:

       4.5 + 5 = 9.5 seconds

   We wait until approximately 12 seconds
   before redirecting.

   This gives the audience time to see
   the completed introduction.
*/

const automaticLaunchTime =
    20000;


setTimeout(
    enterPlatform,
    automaticLaunchTime
);


/* =====================================================
   ENTER BUTTON
===================================================== */

if (enterButton) {

    enterButton.addEventListener(
        "click",
        enterPlatform
    );
}


/* =====================================================
   KEYBOARD SUPPORT
===================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        /*
           ENTER or SPACE launches
           the platform.
        */

        if (
            event.key === "Enter" ||
            event.key === " "
        ) {

            event.preventDefault();

            enterPlatform();
        }
    }
);


/* =====================================================
   VISIBILITY HANDLING
===================================================== */

/*
   If the browser tab becomes inactive,
   we don't stop the animation.

   This keeps the experience predictable
   when the user returns to the page.
*/

document.addEventListener(
    "visibilitychange",
    function () {

        if (
            document.visibilityState ===
            "visible"
        ) {

            document.body.classList.add(
                "page-visible"
            );
        }
    }
);

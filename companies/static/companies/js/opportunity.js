document.addEventListener("DOMContentLoaded", () => {
    const section = document.querySelector("#latest-opportunities");

    if (!section) return;

    const viewport = section.querySelector(".opportunities-marquee");
    const track = section.querySelector(".opportunities-track");
    const pauseButton = section.querySelector("[data-opportunities-pause]");
    const controls = section.querySelectorAll("[data-opportunities-direction]");

    if (!viewport || !track) return;

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    const originalCards = Array.from(track.children).filter(
        card => !card.hasAttribute("aria-hidden")
    );

    // No carousel animation is needed for an empty state.
    if (originalCards.length === 0) {
        controls.forEach(button => {
            button.disabled = true;
        });

        if (pauseButton) pauseButton.disabled = true;
        return;
    }

    let paused = reduceMotion.matches;
    let dragging = false;
    let startX = 0;
    let startScrollLeft = 0;
    let pointerId = null;
    let animationFrame = null;
    let previousTime = 0;
    let dragDistance = 0;
    let suppressClick = false;

    const SPEED = 28; // Pixels per second

    // Measure the distance occupied by one complete set of cards.
    function getLoopDistance() {
        const firstDuplicate = track.querySelector(
            '.opportunity-card[aria-hidden="true"]'
        );

        if (!firstDuplicate || originalCards.length === 0) {
            return 0;
        }

        return firstDuplicate.offsetLeft - originalCards[0].offsetLeft;
    }
    function updateLoopState() {
    const loopDistance = getLoopDistance();

    const needsLoop =
        loopDistance > viewport.clientWidth + 20;

    viewport.classList.toggle("has-no-loop", !needsLoop);

    controls.forEach(button => {
        button.disabled = !needsLoop;
    });

    if (!needsLoop) {
        stopAnimation();
        viewport.scrollLeft = 0;
    } else if (!paused && !dragging) {
        startAnimation();
    }
}

    function getStepSize() {
        const firstCard = originalCards[0];

        if (!firstCard) return 300;

        const styles = window.getComputedStyle(track);
        const gap = parseFloat(styles.columnGap) || 0;

        return firstCard.getBoundingClientRect().width + gap;
    }

    function normalizePosition() {
        const loopDistance = getLoopDistance();

        if (loopDistance <= 0) return;

        // Keep the scroll position inside the duplicated track.
        while (viewport.scrollLeft >= loopDistance) {
            viewport.scrollLeft -= loopDistance;
        }

        while (viewport.scrollLeft < 0) {
            viewport.scrollLeft += loopDistance;
        }
    }

    function updatePauseButton() {
        if (!pauseButton) return;

        pauseButton.setAttribute("aria-pressed", String(paused));

        const icon = pauseButton.querySelector("[data-lucide]");

        if (icon) {
            icon.setAttribute(
                "data-lucide",
                paused ? "play" : "pause"
            );
        }

        pauseButton.setAttribute(
            "aria-label",
            paused
                ? "Resume automatic scrolling"
                : "Pause automatic scrolling"
        );

        // Refresh Lucide icons if its library is loaded.
        if (window.lucide?.createIcons) {
            window.lucide.createIcons();
        }
    }

    function stopAnimation() {
        if (animationFrame !== null) {
            cancelAnimationFrame(animationFrame);
            animationFrame = null;
        }

        previousTime = 0;
    }

    function animate(time) {
        if (paused || dragging || document.hidden) {
            animationFrame = null;
            previousTime = 0;
            return;
        }

        if (previousTime !== 0) {
            const delta = Math.min(time - previousTime, 50);

            viewport.scrollLeft += (SPEED * delta) / 1000;

            normalizePosition();
        }

        previousTime = time;
        animationFrame = requestAnimationFrame(animate);
    }

    function startAnimation() {
        stopAnimation();

        if (paused || dragging || document.hidden || reduceMotion.matches) {
            return;
        }

        animationFrame = requestAnimationFrame(animate);
    }

    function setPaused(value) {
        paused = value;

        if (paused) {
            stopAnimation();
        } else {
            startAnimation();
        }

        updatePauseButton();
    }

    // Previous and next buttons.
    controls.forEach(button => {
        button.addEventListener("click", () => {
            const direction = button.dataset.opportunitiesDirection;
            const distance = getStepSize();

            setPaused(true);

            viewport.scrollBy({
                left: direction === "right" ? distance : -distance,
                behavior: reduceMotion.matches ? "auto" : "smooth"
            });

            // Resume automatically after manual navigation.
     
    if (!reduceMotion.matches) {
        window.setTimeout(() => {
            normalizePosition();

            if (!paused) {
                startAnimation();
            }
        }, 550);
    }
        });
    });

    // Pause and resume button.
    if (pauseButton) {
        pauseButton.addEventListener("click", () => {
            if (reduceMotion.matches) return;
            setPaused(!paused);
        });
    }

    // Pause when the pointer enters the carousel.
    viewport.addEventListener("mouseenter", () => {
        if (!dragging) stopAnimation();
    });

    viewport.addEventListener("mouseleave", () => {
        if (!dragging) startAnimation();
    });

    // Pause when the page is hidden; resume when it becomes visible.
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            stopAnimation();
        } else {
            startAnimation();
        }
    });

    // Mouse dragging and touch-friendly pointer handling.
    viewport.addEventListener("pointerdown", event => {
        if (event.pointerType === "mouse" && event.button !== 0) {
            return;
        }

        dragging = true;
        startX = event.clientX;
        startScrollLeft = viewport.scrollLeft;
        dragDistance = 0;
        pointerId = event.pointerId;

        stopAnimation();
        viewport.classList.add("is-dragging");
    });

    viewport.addEventListener("pointermove", event => {
        if (!dragging || event.pointerId !== pointerId) return;

        const distance = event.clientX - startX;

        dragDistance = Math.max(dragDistance, Math.abs(distance));

        if (dragDistance > 5) {
            viewport.scrollLeft = startScrollLeft - distance;
            normalizePosition();
        }
    });

    function endDrag(event) {
        if (!dragging) return;

        if (
            event &&
            pointerId !== null &&
            event.pointerId !== undefined &&
            event.pointerId !== pointerId
        ) {
            return;
        }

        dragging = false;
        pointerId = null;
        viewport.classList.remove("is-dragging");

        if (dragDistance > 5) {
            suppressClick = true;

            window.setTimeout(() => {
                suppressClick = false;
            }, 100);
        }

        startAnimation();
    }

    viewport.addEventListener("pointerup", endDrag);
    viewport.addEventListener("pointercancel", endDrag);
    window.addEventListener("pointerup", endDrag);

    // Prevent accidental navigation after dragging a card.
    viewport.addEventListener("click", event => {
        if (suppressClick) {
            event.preventDefault();
            event.stopPropagation();
        }
    }, true);

    // Keyboard navigation when the carousel viewport has focus.
    viewport.addEventListener("keydown", event => {
        if (event.key === "ArrowRight") {
            event.preventDefault();
            viewport.scrollBy({
                left: getStepSize(),
                behavior: reduceMotion.matches ? "auto" : "smooth"
            });
        }

        if (event.key === "ArrowLeft") {
            event.preventDefault();
            viewport.scrollBy({
                left: -getStepSize(),
                behavior: reduceMotion.matches ? "auto" : "smooth"
            });
        }
    });

    // Respect changes to the operating system's motion preference.
    reduceMotion.addEventListener("change", event => {
        if (event.matches) {
            setPaused(true);
        }
    });

    updatePauseButton();
    startAnimation();

    // Keep the carousel measurements accurate after resizing.
    window.addEventListener("resize", normalizePosition);
});
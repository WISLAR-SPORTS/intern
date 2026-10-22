(() => { "use strict";

const exam = document.getElementById("exam");
const form = document.getElementById("exam-form");

if (!exam || !form) return;

const timer = document.getElementById("timer");
const timerPanel = timer?.closest(".timer-panel");
const submitButton = document.getElementById("submit-exam");
const overallStatus = document.getElementById("overall-status");

if (!timer || !timerPanel || !submitButton || !overallStatus) {
    console.error("Assessment page is missing required elements.");
    return;
}

const deadline = Number(exam.dataset.deadline);
const saveUrl = exam.dataset.saveUrl;
const submitUrl = exam.dataset.submitUrl;
const resultUrl = exam.dataset.resultUrl;

if (
    !Number.isFinite(deadline) ||
    deadline <= 0 ||
    !saveUrl ||
    !submitUrl ||
    !resultUrl
) {
    overallStatus.textContent =
        "Assessment configuration is invalid. Please reload the page.";
    submitButton.disabled = true;
    return;
}

let submitting = false;
let expired = false;
let timerInterval = null;
let submissionPromise = null;

// Each question has at most one active save.
// New selections replace the pending value.
const questionStates = new Map();

function csrfToken() {
    return form.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    )?.value || "";
}

async function post(url, data = {}) {
    const token = csrfToken();

    if (!token) {
        throw new Error("CSRF token is missing. Reload the page.");
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
        const response = await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            signal: controller.signal,
            headers: {
                "X-CSRFToken": token,
                "Content-Type":
                    "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "application/json",
            },
            body: new URLSearchParams(data),
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                result.error ||
                result.detail ||
                `Request failed (${response.status}).`
            );
        }

        return result;
    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error(
                "The request timed out. Please retry submission."
            );
        }

        throw error;
    } finally {
        clearTimeout(timeoutId);
    }
}

function setOverallStatus(message) {
    overallStatus.textContent = message;
}

function setSaveStatus(state, isActive, message) {
    const status = state.card?.querySelector(".save-status");

    if (!status) return;

    status.classList.remove("saving", "saved", "error");

    if (state.error) {
        status.classList.add("error");
    } else if (state.saving) {
        status.classList.add("saving");
    } else if (state.saved) {
        status.classList.add("saved");
    }

    status.textContent = message || "";
}

function getQuestionState(input) {
    const questionId = input.dataset.questionId;
    let state = questionStates.get(questionId);

    if (!state) {
        state = {
            questionId,
            card: input.closest(".question-card"),
            selectedOption: null,
            savedOption: null,
            saving: false,
            saved: false,
            error: false,
            version: 0,
            worker: null,
        };

        const selected = state.card?.querySelector(
            'input[type="radio"]:checked'
        );

        if (selected) {
            state.selectedOption = selected.value;
            state.savedOption = selected.value;

            // The template marks this answer as previously saved.
            state.saved = true;
        }

        questionStates.set(questionId, state);
    }

    return state;
}

// Initialize all questions, including previously answered ones.
form.querySelectorAll(".question-card").forEach(card => {
    const input = card.querySelector(
        'input[type="radio"][data-question-id]'
    );

    if (!input) return;

    const state = getQuestionState(input);

    if (state.selectedOption !== null) {
        setSaveStatus(state, true, "Previously saved");
    } else {
        setSaveStatus(state, false, "Not answered");
    }
});

function hasPendingSaves() {
    for (const state of questionStates.values()) {
        if (
            state.saving ||
            state.worker ||
            state.selectedOption !== state.savedOption
        ) {
            return true;
        }
    }

    return false;
}

function hasFailedSaves() {
    for (const state of questionStates.values()) {
        if (state.error) return true;
    }

    return false;
}

async function processSaveQueue(state) {
    if (state.worker) return state.worker;

    state.worker = (async () => {
        state.saving = true;

        try {
            while (state.selectedOption !== state.savedOption) {
                if (expired || submitting) break;

                const optionToSave = state.selectedOption;
                const versionToSave = state.version;

                state.error = false;
                state.saved = false;

                setSaveStatus(state, true, "Saving...");
                setOverallStatus("Saving your answers...");

                try {
                    await post(saveUrl, {
                        question_id: state.questionId,
                        option_id: optionToSave,
                    });

                    state.savedOption = optionToSave;

                    // Do not show an outdated success message if
                    // the student selected another option meanwhile.
                    if (state.version === versionToSave) {
                        state.error = false;
                        state.saved = true;

                        setSaveStatus(state, true, "Answer saved");
                    }
                } catch (error) {
                    state.error = true;
                    state.saved = false;

                    setSaveStatus(
                        state,
                        false,
                        "Save failed. Select your answer again to retry."
                    );

                    setOverallStatus(
                        `${error.message} Your latest answer may not be saved.`
                    );

                    break;
                }
            }
        } finally {
            state.saving = false;
            state.worker = null;

            // A new selection may have arrived as the worker ended.
            if (
                !expired &&
                !submitting &&
                state.selectedOption !== state.savedOption &&
                !state.error
            ) {
                void processSaveQueue(state);
            }
        }
    })();

    return state.worker;
}

function saveAnswer(input) {
    const state = getQuestionState(input);

    state.selectedOption = input.value;
    state.version += 1;
    state.error = false;
    state.saved = false;

    setSaveStatus(state, true, "Saving...");

    return processSaveQueue(state);
}

form.addEventListener("change", event => {
    const input = event.target;

    if (!input.matches('input[type="radio"][data-question-id]')) {
        return;
    }

    if (submitting || expired || Date.now() >= deadline) {
        input.checked = false;

        setOverallStatus(
            "The assessment deadline has passed or submission has started."
        );

        return;
    }

    const state = getQuestionState(input);

    // Update the latest desired answer immediately.
    state.selectedOption = input.value;
    state.version += 1;
    state.error = false;
    state.saved = false;

    setSaveStatus(state, true, "Saving...");

    void processSaveQueue(state);
});

function updateTimer() {
    if (expired || submitting) return;

    const remaining = Math.max(
        0,
        Math.ceil((deadline - Date.now()) / 1000)
    );

    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;

    timer.textContent =
        `${String(minutes).padStart(2, "0")}:` +
        `${String(seconds).padStart(2, "0")}`;

    if (remaining <= 60) {
        timerPanel.classList.add("timer-warning");
    }

    if (remaining === 0) {
        expired = true;

        clearInterval(timerInterval);
        timerInterval = null;

        timer.textContent = "00:00";

        form.querySelectorAll('input[type="radio"]').forEach(input => {
            input.disabled = true;
        });

        submitButton.disabled = true;

        setOverallStatus(
            "Time is up! Your assessment is being submitted..."
        );

        void submitExam(true);
    }
}

async function flushPendingSaves() {
    // Wait for all currently running save queues to settle.
    while (true) {
        const workers = [];

        for (const state of questionStates.values()) {
            if (
                state.selectedOption !== state.savedOption &&
                !state.worker &&
                !state.error
            ) {
                void processSaveQueue(state);
            }

            if (state.worker) {
                workers.push(state.worker);
            }
        }

        if (workers.length > 0) {
            await Promise.allSettled(workers);
            continue;
        }

        if (!hasPendingSaves()) return;

        // A failed save must not silently pass as successful.
        if (hasFailedSaves()) {
            throw new Error(
                "Some answers could not be saved. Retry the failed answers before submitting."
            );
        }

        // Allow any just-finished queue to settle.
        await new Promise(resolve => setTimeout(resolve, 50));
    }
}

async function submitExam(timeExpired = false) {
    if (submissionPromise) return submissionPromise;
    if (submitting) return;

    if (!timeExpired && Date.now() >= deadline) {
        timeExpired = true;
    }

    submitting = true;

    if (timeExpired) {
        expired = true;

        clearInterval(timerInterval);
        timerInterval = null;

        timer.textContent = "00:00";

        form.querySelectorAll('input[type="radio"]').forEach(input => {
            input.disabled = true;
        });
    }

    submitButton.disabled = true;

    setOverallStatus(
        timeExpired
            ? "Time is up! Submitting your saved answers..."
            : "Checking saved answers before submission..."
    );

    submissionPromise = (async () => {
        try {
            // Only normal submissions wait for pending answer saves.
            // An expired assessment must not wait indefinitely.
            if (!timeExpired) {
                await flushPendingSaves();
            }

            setOverallStatus("Submitting your assessment...");

            const result = await post(submitUrl);

            setOverallStatus("Submission successful. Opening results...");

            window.location.replace(
                result.redirect_url || resultUrl
            );
        } catch (error) {
            console.error("Assessment submission failed:", error);

            submitting = false;
            submissionPromise = null;

            if (expired || timeExpired) {
                // Keep answers locked, but allow submission to be retried.
                submitButton.disabled = false;
                submitButton.textContent = "Retry submission";

                setOverallStatus(
                    "Your time has expired, but submission could not be " +
                    "confirmed. Check your connection and click " +
                    "'Retry submission'. Your answers remain locked."
                );
            } else {
                submitButton.disabled = false;

                setOverallStatus(
                    `${error.message} Please resolve the issue and retry.`
                );
            }
        }
    })();

    return submissionPromise;
}
form.addEventListener("submit", event => {
    event.preventDefault();

    if (submitting) return;

    if (expired || Date.now() >= deadline) {
        void submitExam(true);
        return;
    }

    if (
        window.confirm(
            "Are you sure you want to submit your assessment? " +
            "You may not be able to change your answers afterward."
        )
    ) {
        void submitExam(false);
    }
});

// Retry failed answers when the student selects an option again.
// Do not treat a failed save as successful.

// Optional browser-side deterrents. These are not security boundaries.
exam.addEventListener("contextmenu", event => {
    event.preventDefault();
});

exam.addEventListener("copy", event => {
    event.preventDefault();
});

exam.addEventListener("cut", event => {
    event.preventDefault();
});

exam.addEventListener("paste", event => {
    if (event.target.matches("input[type='radio']")) {
        event.preventDefault();
    }
});

exam.addEventListener("keydown", event => {
    const key = event.key.toLowerCase();
    const modified = event.ctrlKey || event.metaKey;

    if (
        modified &&
        ["c", "x", "v", "u", "s", "p"].includes(key)
    ) {
        event.preventDefault();
    }

    if (key === "f12") {
        event.preventDefault();
    }
});

// Disable accidental repeated clicks and enforce the visual deadline.
updateTimer();
timerInterval = setInterval(updateTimer, 1000);

window.addEventListener("pagehide", () => {
    clearInterval(timerInterval);
});


})();
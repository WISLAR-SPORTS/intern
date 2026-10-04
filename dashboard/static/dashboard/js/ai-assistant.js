/* =========================================================
   INTERNSHIP CONNECT
   AI ASSISTANT
   dashboard/static/dashboard/js/ai-assistant.js
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("AI Assistant JS loaded");


    /* =====================================================
       ELEMENTS
    ===================================================== */

    const aiInput =
        document.getElementById("ai-input");

    const aiSend =
        document.getElementById("ai-send");

    const aiConversation =
        document.getElementById("ai-conversation");

    const aiAssistant =
        document.getElementById("ai-assistant");

    const aiToggle =
        document.getElementById("ai-toggle");

    const closeAi =
        document.getElementById("close-ai");


    /* =====================================================
       CHECK REQUIRED ELEMENTS
    ===================================================== */

    if (!aiToggle) {
        console.error("AI ERROR: #ai-toggle was not found.");
        return;
    }

    if (!aiAssistant) {
        console.error("AI ERROR: #ai-assistant was not found.");
        return;
    }

    if (!closeAi) {
        console.error("AI ERROR: #close-ai was not found.");
        return;
    }

    if (!aiInput) {
        console.error("AI ERROR: #ai-input was not found.");
        return;
    }

    if (!aiSend) {
        console.error("AI ERROR: #ai-send was not found.");
        return;
    }

    if (!aiConversation) {
        console.error(
            "AI ERROR: #ai-conversation was not found."
        );
        return;
    }


    /* =====================================================
       LUCIDE ICONS
    ===================================================== */

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }


    /* =====================================================
       CSRF TOKEN
    ===================================================== */

    function getCSRFToken() {

        const cookie = document.cookie
            .split("; ")
            .find(
                row => row.startsWith("csrftoken=")
            );

        if (!cookie) {
            return null;
        }

        return decodeURIComponent(
            cookie.split("=")[1]
        );
    }


    /* =====================================================
       OPEN AI ASSISTANT
    ===================================================== */

    function openAI() {

        console.log("Opening AI Assistant");

        aiAssistant.classList.add("active");

        document.body.classList.add("ai-open");

        setTimeout(function () {

            aiInput.focus();

        }, 100);

        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }
    }


    /* =====================================================
       CLOSE AI ASSISTANT
    ===================================================== */

    function closeAI() {

        console.log("Closing AI Assistant");

        aiAssistant.classList.remove("active");

        document.body.classList.remove("ai-open");
    }


    /* =====================================================
       TOGGLE BUTTON
    ===================================================== */

    aiToggle.addEventListener(
        "click",
        function (event) {

            event.preventDefault();
            event.stopPropagation();

            console.log("AI button clicked");

            if (
                aiAssistant.classList.contains("active")
            ) {

                closeAI();

            } else {

                openAI();

            }

        }
    );


    /* =====================================================
       CLOSE BUTTON
    ===================================================== */

    closeAi.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            closeAI();

        }
    );


    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                aiAssistant.classList.contains("active")
            ) {

                closeAI();

            }

        }
    );


    /* =====================================================
       ADD MESSAGE
    ===================================================== */

    function addMessage(
        message,
        role,
        learningUrl = null
    ) {

        const messageElement =
            document.createElement("div");

        messageElement.classList.add(
            "ai-message",
            role
        );


        const textElement =
            document.createElement("div");

        textElement.textContent =
            message || "";

        messageElement.appendChild(
            textElement
        );


        /* =============================================
           LEARNING RESOURCE
        ============================================= */

        if (
            learningUrl &&
            role === "assistant"
        ) {

            try {

                const url =
                    new URL(learningUrl);


                const allowedHost =
                    url.hostname === "youtube.com" ||
                    url.hostname === "www.youtube.com" ||
                    url.hostname === "m.youtube.com";


                if (
                    url.protocol === "https:" &&
                    allowedHost
                ) {

                    const resourceCard =
                        document.createElement("div");

                    resourceCard.classList.add(
                        "ai-learning-resource"
                    );


                    const icon =
                        document.createElement("div");

                    icon.className =
                        "learning-resource-icon";

                    icon.textContent =
                        "▶";


                    const content =
                        document.createElement("div");

                    content.className =
                        "learning-resource-content";


                    const title =
                        document.createElement("strong");

                    title.textContent =
                        "Learning Resource";


                    const description =
                        document.createElement("span");

                    description.textContent =
                        "Watch tutorials and lessons on YouTube";


                    content.appendChild(title);
                    content.appendChild(description);


                    const link =
                        document.createElement("a");

                    link.href =
                        url.href;

                    link.target =
                        "_blank";

                    link.rel =
                        "noopener noreferrer";

                    link.className =
                        "learning-resource-button";

                    link.textContent =
                        "Watch Tutorials ↗";


                    resourceCard.appendChild(icon);
                    resourceCard.appendChild(content);
                    resourceCard.appendChild(link);


                    messageElement.appendChild(
                        resourceCard
                    );
                }

            } catch (error) {

                console.error(
                    "Invalid learning URL:",
                    error
                );

            }

        }


        aiConversation.appendChild(
            messageElement
        );


        scrollConversation();
    }


    /* =====================================================
       SCROLL
    ===================================================== */

    function scrollConversation() {

        const messages =
            document.getElementById("ai-messages");

        if (!messages) {
            return;
        }

        messages.scrollTop =
            messages.scrollHeight;
    }


    /* =====================================================
       LOADING
    ===================================================== */

    function setLoading(loading) {

        aiSend.disabled =
            loading;

        aiInput.disabled =
            loading;


        if (loading) {

            aiSend.innerHTML =
                "⏳";

        } else {

            aiSend.innerHTML =
                '<i data-lucide="send"></i>';

            if (typeof lucide !== "undefined") {
                lucide.createIcons();
            }

        }
    }


    /* =====================================================
       SEND MESSAGE
    ===================================================== */

    async function sendMessage(message) {

        if (
            !message ||
            !message.trim()
        ) {

            return;
        }


        message =
            message.trim();


        /* User message */

        addMessage(
            message,
            "user"
        );


        aiInput.value = "";


        setLoading(true);


        try {

            console.log(
                "Sending AI request..."
            );


            const csrfToken =
                getCSRFToken();


            if (!csrfToken) {

                throw new Error(
                    "CSRF token not found."
                );

            }


            const response =
                await fetch(
                    "/ai/chat/",
                    {
                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json",

                            "X-CSRFToken":
                                csrfToken,

                            "X-Requested-With":
                                "XMLHttpRequest"

                        },

                        body:
                            JSON.stringify({
                                message: message
                            })
                    }
                );


            console.log(
                "AI HTTP status:",
                response.status
            );


            const contentType =
                response.headers.get(
                    "content-type"
                ) || "";


            if (
                !contentType.includes(
                    "application/json"
                )
            ) {

                throw new Error(
                    "Server returned a non-JSON response."
                );

            }


            const data =
                await response.json();


            console.log(
                "AI DATA:",
                data
            );


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "AI request failed."
                );

            }


            addMessage(
                data.message ||
                "I received your message, but no response was returned.",
                "assistant",
                data.learning_url ||
                null
            );


        } catch (error) {

            console.error(
                "AI Assistant Error:",
                error
            );


            addMessage(
                "Sorry, I couldn't process your request. Please try again.",
                "assistant"
            );


        } finally {

            setLoading(false);

            aiInput.focus();

        }

    }


    /* =====================================================
       QUICK ACTIONS
    ===================================================== */

    window.sendQuickMessage =
        function (message) {

            openAI();

            sendMessage(message);

        };


    /* =====================================================
       SEND BUTTON
    ===================================================== */

    aiSend.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            sendMessage(
                aiInput.value
            );

        }
    );


    /* =====================================================
       ENTER KEY
    ===================================================== */

    aiInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage(
                    aiInput.value
                );

            }

        }
    );


    /* =====================================================
       INITIALIZE
    ===================================================== */

    console.log(
        "AI Assistant initialized successfully"
    );

});

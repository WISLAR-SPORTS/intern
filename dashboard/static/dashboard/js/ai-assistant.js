document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("ai-form");
    const input = document.getElementById("ai-input");
    const conversation = document.getElementById("ai-conversation");
    const sendButton = document.getElementById("ai-send");
    const config = document.getElementById("ai-chat-config");

    if (!form || !input || !conversation || !sendButton || !config) {
        console.error("AI chat elements are missing from the page.");
        return;
    }

    const chatUrl = config.dataset.chatUrl;

    function getCsrfToken() {
        return document.querySelector(
            '[name="csrfmiddlewaretoken"]'
        )?.value || "";
    }

    function addMessage(text, sender = "assistant") {
        const wrapper = document.createElement("div");

        wrapper.className = sender === "user"
            ? "assistant-message user-message"
            : "assistant-message assistant-reply";

        const avatar = document.createElement("div");
        avatar.className = "message-avatar";

        const icon = document.createElement("i");
        icon.setAttribute(
            "data-lucide",
            sender === "user" ? "user-round" : "bot"
        );
        avatar.appendChild(icon);

        const content = document.createElement("div");
        content.className = "message-content";

        const heading = document.createElement("strong");
        heading.textContent = sender === "user" ? "You" : "AI Assistant";

        const paragraph = document.createElement("p");
        paragraph.textContent = text;

        content.append(heading, paragraph);
        wrapper.append(avatar, content);
        conversation.appendChild(wrapper);

        if (window.lucide) {
            window.lucide.createIcons({ root: wrapper });
        }

        conversation.scrollTop = conversation.scrollHeight;

        return wrapper;
    }

    async function sendMessage(message) {
        const cleanMessage = message.trim();

        if (!cleanMessage || sendButton.disabled) return;

        addMessage(cleanMessage, "user");
        input.value = "";
        input.disabled = true;
        sendButton.disabled = true;

        const pending = addMessage("Thinking...");

        try {
            const response = await fetch(chatUrl, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({
                    message: cleanMessage,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to get an AI response."
                );
            }

            pending.querySelector("p").textContent =
                data.message || "The assistant returned an empty response.";

            // Show a learning resource link when supplied.
            if (data.learning_url) {
                const link = document.createElement("a");
                link.href = data.learning_url;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                link.textContent = "Open learning resources";
                link.className = "assistant-resource-link";

                pending.querySelector(".message-content").appendChild(link);
            }
        } catch (error) {
            pending.querySelector("p").textContent = error.message;
        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
            conversation.scrollTop = conversation.scrollHeight;
        }
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        sendMessage(input.value);
    });

    document.querySelectorAll(".assistant-prompt").forEach((button) => {
        button.addEventListener("click", () => {
            sendMessage(button.dataset.aiMessage || "");
        });
    });
});
/**
 * FitCoach AI - Chatbot Client Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");
    const clearChatBtn = document.getElementById("clear-chat-btn");
    const ttsToggle = document.getElementById("tts-toggle");

    let isSpeechEnabled = false;

    // Configure marked options
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    // Scroll chat to bottom
    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Format markdown text to safe HTML
    function formatMarkdown(text) {
        if (window.marked) {
            return marked.parse(text);
        }
        return text.replace(/\n/g, "<br>");
    }

    // Speak text using Web Speech API
    function speakText(text) {
        if (!isSpeechEnabled || !('speechSynthesis' in window)) return;
        
        window.speechSynthesis.cancel(); // Stop current speech
        // Strip markdown symbols for clean audio
        const cleanText = text.replace(/[*#_`|>-]/g, ' ').replace(/\[.*?\]\(.*?\)/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.05;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }

    // Append Message to UI
    function appendMessage(role, content) {
        const isUser = role === "user";
        const messageDiv = document.createElement("div");
        messageDiv.className = `message-bubble ${isUser ? 'user' : 'assistant'}`;

        const avatarDiv = document.createElement("div");
        avatarDiv.className = "bubble-avatar";
        avatarDiv.innerHTML = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const contentDiv = document.createElement("div");
        contentDiv.className = "bubble-content";
        contentDiv.innerHTML = isUser ? content.replace(/\n/g, '<br>') : formatMarkdown(content);

        // Add copy button for assistant replies
        if (!isUser) {
            const actionsDiv = document.createElement("div");
            actionsDiv.className = "mt-2 pt-2 d-flex gap-2 border-top border-secondary border-opacity-25";
            actionsDiv.innerHTML = `
                <button class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size: 0.75rem;" onclick="navigator.clipboard.writeText(\`${content.replace(/`/g, '\\`').replace(/\\/g, '\\\\')}\`); showToast('Copied to clipboard!', 'success');">
                    <i class="fa-regular fa-copy me-1"></i> Copy
                </button>
            `;
            contentDiv.appendChild(actionsDiv);
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();

        if (!isUser) {
            speakText(content);
        }
    }

    // Show typing placeholder
    function showTyping() {
        const typingDiv = document.createElement("div");
        typingDiv.className = "message-bubble assistant";
        typingDiv.id = "typing-indicator";
        typingDiv.innerHTML = `
            <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="bubble-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    function hideTyping() {
        const typingDiv = document.getElementById("typing-indicator");
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    // Send message to backend API
    async function sendMessage(text) {
        const message = text || userInput.value.trim();
        if (!message) return;

        if (userInput) userInput.value = "";
        appendMessage("user", message);
        showTyping();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            hideTyping();

            if (data.success && data.reply) {
                appendMessage("assistant", data.reply);
            } else {
                appendMessage("assistant", "⚠️ " + (data.error || "Sorry, I could not process that request."));
            }
        } catch (error) {
            hideTyping();
            console.error("Chat error:", error);
            appendMessage("assistant", "⚠️ Connection error. Please ensure the server is running.");
        }
    }

    // Handle Form Submit
    if (chatForm) {
        chatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            sendMessage();
        });
    }

    // Handle Quick Prompt Chips
    document.querySelectorAll(".prompt-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt") || chip.innerText.trim();
            sendMessage(prompt);
        });
    });

    // Clear Chat History
    if (clearChatBtn) {
        clearChatBtn.addEventListener("click", async () => {
            if (!confirm("Are you sure you want to clear your conversation history?")) return;
            try {
                const response = await fetch("/api/chat/clear", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                if (data.success) {
                    if (chatMessages) chatMessages.innerHTML = "";
                    appendMessage("assistant", "👋 Conversation cleared! How can I help you crush your fitness goals today?");
                    if (window.showToast) showToast("Chat history cleared", "info");
                }
            } catch (err) {
                console.error("Clear chat error:", err);
            }
        });
    }

    // Audio Voice Toggle
    if (ttsToggle) {
        ttsToggle.addEventListener("click", () => {
            isSpeechEnabled = !isSpeechEnabled;
            ttsToggle.classList.toggle("active", isSpeechEnabled);
            ttsToggle.innerHTML = isSpeechEnabled ? 
                '<i class="fa-solid fa-volume-high text-success"></i> Audio On' : 
                '<i class="fa-solid fa-volume-xmark"></i> Audio Off';
            if (!isSpeechEnabled && window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        });
    }

    // Scroll to bottom on initial load
    scrollToBottom();
});

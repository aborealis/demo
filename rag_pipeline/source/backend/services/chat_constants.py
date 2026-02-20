

MAIN_CHAT_PIPELINE_NAME = "main_pipeline"
MAIN_CHAT_PIPELINE_VERSION = "1.0"

DEFAULT_CHAT_ERROR_MESSAGE = "Sorry, something went wrong."
DEFAULT_CHAT_NO_ANSWER_MESSAGE = "No relevant answer was found in the indexed documents."
DEFAULT_CHAT_SEND_AGAIN = "Please try rephrasing your request."
DEFAUL_CIRCUIT_BREAKER_MSG = "The chat is temporary unavailable."


SYSTEM_PROMPT_CHAT_INIT = "You are a helpful assistant. Answer briefly. Keep conversation in the user's language."


GREETING_PROMPT = """Language detected: {{ lang }}.
Send one short, polite greeting in the detected language.
Do not add extra explanations.

Greeting:
"""


SUMMARY_PROMPT = """You are maintaining a running summary of a conversation.

Your task:
- Update the existing summary using the new messages.
- Preserve important facts, user goals, decisions, constraints, preferences, and unresolved questions.
- Remove irrelevant details, chit-chat, and repetitions.
- Do NOT invent new information.
- Do NOT change facts.
- Keep the summary concise but complete.

If there is no existing summary, create one from scratch. Use the user's language.

Return ONLY the updated summary text.
"""


TEST_CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
</head>
<body>
<h1>WebSocket Chat</h1>

<form id="chat-form">
    <input type="text" id="messageText" autocomplete="off"/>
    <button type="submit">Send</button>
</form>

<ul id="messages"></ul>

<script>
let ws = null;
const PASSPORT_KEY = "chat_passport_id";

async function initChat() {
    let passportId = localStorage.getItem(PASSPORT_KEY);

    const response = await fetch("/chat/init", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id: passportId,
            source: "web",
        })
    });

    const data = await response.json();

    passportId = data.chat_passport_id;
    localStorage.setItem(PASSPORT_KEY, passportId);

    connectWebSocket(data.ws_url);
}

function connectWebSocket(wsUrl) {
    ws = new WebSocket(`ws://${location.host}${wsUrl}`);

    ws.onopen = () => {
        console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
        addMessageToList(event.data, false);
    };

    ws.onclose = () => {
        console.log("WebSocket closed");
    };

    ws.onerror = (err) => {
        console.error("WebSocket error", err);
    };
}

function addMessageToList(message, isUserMessage) {
    const li = document.createElement("li");
    
    if (isUserMessage) {
        li.textContent = `user: ${message}`;
        li.style.color = "blue";
    } else {
        li.textContent = message;
        li.style.color = "black";
    }
    
    document.getElementById("messages").appendChild(li);
}

document.getElementById("chat-form").addEventListener("submit", (event) => {
    event.preventDefault();

    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn("WebSocket not connected");
        return;
    }

    const input = document.getElementById("messageText");
    const message = input.value.trim();
    
    if (message) {
        // show local echo for user message
        addMessageToList(message, true);
        
        // then send to websocket
        ws.send(message);
        
        input.value = "";
    }
});

// initialize chat session on load
initChat();
</script>
</body>
</html>
"""

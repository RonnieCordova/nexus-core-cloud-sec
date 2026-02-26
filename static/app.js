const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let historialChat = [];

marked.setOptions({ breaks: true, gfm: true });

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'system-message');
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    if (sender === 'system') {
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.textContent = text;
    }
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    console.log("Enviando mensaje a Nexus..."); // LOG DE PRUEBA
    appendMessage(text, 'user');
    userInput.value = '';
    userInput.style.height = 'auto'; // Resetea altura del textarea

    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'bubble system-message';
    loadingDiv.style.fontStyle = 'italic';
    loadingDiv.textContent = 'Nexus analizando...';
    chatBox.appendChild(loadingDiv);

    try {
        const response = await fetch('/api/consultar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                pregunta: text,
                historial: historialChat.slice(-6) 
            })
        });

        console.log("Respuesta recibida, status:", response.status); // LOG DE PRUEBA
        const data = await response.json();
        if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();

        if (response.ok) {
            appendMessage(data.respuesta, 'system');
            historialChat.push({ role: "user", content: text });
            historialChat.push({ role: "assistant", content: data.respuesta });
        } else {
            const errorMsg = response.status === 429 ? "Límite excedido. Espera 60s." : (data.detail || "Error fatal.");
            appendMessage("⚠️ " + errorMsg, 'system');
        }
    } catch (error) {
        console.error("Error en Fetch:", error); // LOG DE ERROR
        if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();
        appendMessage("Error: No se pudo contactar al servidor.", 'system');
    }
}

// Eventos
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Enter envía, Shift+Enter hace salto de línea
        e.preventDefault();
        sendMessage();
    }
});

// Auto-expandir el textarea segun el contenido
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});
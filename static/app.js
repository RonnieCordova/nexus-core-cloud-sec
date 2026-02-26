// capturo los elementos principales del html
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// array para guardar la memoria de la sesion actual
let historialChat = [];

// configuro la libreria marked para que respete los saltos de linea normales de la IA
marked.setOptions({
    breaks: true,
    gfm: true
});

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'system-message');
    
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    
    // si el mensaje es de la IA, lo renderizo con markdown. si es mio, lo dejo como texto plano por seguridad
    if (sender === 'system') {
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.textContent = text;
    }
    
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    
    // scrolleo hacia abajo automaticamente para ver el nuevo mensaje
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    // si el input esta vacio, no hago nada para no gastar peticiones a la api
    if (!text) return;

    // pinto mi mensaje en la pantalla
    appendMessage(text, 'user');
    userInput.value = '';

    // pongo un indicador visual de que la peticion esta en proceso
    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Nexus está procesando...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // envio la pregunta actual y todo el historial de mi sesion
        const response = await fetch('/api/consultar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                pregunta: text,
                historial: historialChat
            })
        });

        const data = await response.json();
        
        // quito el texto de "cargando"
        document.getElementById(loadingId).remove();

        // manejo las posibles respuestas del servidor
        if (response.ok) {
            // si todo salio bien, pinto la respuesta
            appendMessage(data.respuesta, 'system');
            
            // actualizo mi memoria local para la proxima peticion
            historialChat.push({ role: "user", content: text });
            historialChat.push({ role: "assistant", content: data.respuesta });
            
        } else if (response.status === 429) {
            // atrapo el error especifico de rate limit (slowapi) para proteger mi plataforma
            appendMessage("Has superado el límite de consultas permitidas. Por favor, espera un minuto por seguridad.", 'system');
        } else {
            // cualquier otro error del servidor (ej. un 500)
            appendMessage("Error: " + (data.detail || "Error desconocido"), 'system');
        }

    } catch (error) {
        // si el servidor esta caido y ni siquiera responde
        document.getElementById(loadingId).remove();
        appendMessage("Error de conexión con el servidor local.", 'system');
    }
}

// escucho el click en el boton de enviar
sendBtn.addEventListener('click', sendMessage);

// escucho cuando presiono la tecla enter en el teclado
userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let historialChat = [];
marked.setOptions({ breaks: true, gfm: true });

function appendMessage(text, sender) {
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'flex flex-col gap-2 max-w-3xl mx-auto w-full';
    
    // diseño para la IA vs el Usuario
    if (sender === 'system') {
        wrapperDiv.innerHTML = `
            <div class="flex items-center gap-2 mb-1">
                <div class="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center text-[10px] text-emerald-500 border border-emerald-500/30">N</div>
                <span class="text-xs text-zinc-400 font-medium">Nexus System</span>
            </div>
            <div class="bg-zinc-900/50 border border-zinc-800 text-sm text-zinc-300 p-4 rounded-2xl rounded-tl-sm shadow-sm inline-block prose prose-invert max-w-none">
                ${marked.parse(text)}
            </div>
        `;
    } else {
        wrapperDiv.className += ' items-end';
        wrapperDiv.innerHTML = `
            <div class="bg-zinc-100 text-sm text-zinc-900 p-4 rounded-2xl rounded-tr-sm shadow-sm inline-block max-w-[85%] whitespace-pre-wrap">
                ${text}
            </div>
        `;
    }
    
    chatBox.appendChild(wrapperDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';

    const loadingId = 'loading-' + Date.now();
    const loadingHtml = `
        <div id="${loadingId}" class="flex flex-col gap-2 max-w-3xl mx-auto w-full">
            <div class="flex items-center gap-2 mb-1">
                <div class="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center text-[10px] text-emerald-500 border border-emerald-500/30">N</div>
                <span class="text-xs text-zinc-400 font-medium">Nexus System</span>
            </div>
            <div class="bg-zinc-900/50 border border-zinc-800 text-sm text-zinc-500 italic p-4 rounded-2xl rounded-tl-sm w-fit flex items-center gap-3">
                <span class="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce"></span>
                <span class="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                <span class="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
            </div>
        </div>
    `;
    chatBox.insertAdjacentHTML('beforeend', loadingHtml);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/api/consultar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pregunta: text, historial: historialChat.slice(-6) })
        });

        const data = await response.json();
        document.getElementById(loadingId).remove();

        if (response.ok) {
            appendMessage(data.respuesta, 'system');
            historialChat.push({ role: "user", content: text });
            historialChat.push({ role: "assistant", content: data.respuesta });
        } else {
            appendMessage("⚠️ Error: " + (data.detail || "Fallo en el servidor."), 'system');
        }
    } catch (error) {
        document.getElementById(loadingId).remove();
        appendMessage("⚠️ Error de conexión con el servidor local.", 'system');
    }
}

sendBtn.onclick = sendMessage;
userInput.onkeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
};
userInput.oninput = function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
};
/**
 * Fontanero Virtual PRO v1.0
 * Chatbot con 133 respuestas + presupuestos estimativos
 * Eduardo Quiroz - Fontanero en Torrevieja
 */

// Variables globales
let chatData = {};
let isLoaded = false;

// Cargar JSON de respuestas al iniciar
async function loadChatData() {
    try {
        const response = await fetch('json/responses.json');
        if (!response.ok) throw new Error('HTTP ' + response.status);
        chatData = await response.json();
        isLoaded = true;
        console.log('✅ Chat data loaded:', Object.keys(chatData).length, 'entries');
    } catch (error) {
        console.error('❌ Error loading chat data:', error);
        addMessage('bot', '⚠️ Error al cargar respuestas. Recarga la página o contacta por WhatsApp 📸');
    }
}

// Normalizar texto (igual que en Python)
function normalizeText(text) {
    return text.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Quitar tildes
        .replace(/[^\w\s]/g, '') // Quitar caracteres especiales
        .trim();
}

// Buscar respuesta en el JSON
function findResponse(message) {
    if (!isLoaded || Object.keys(chatData).length === 0) {
        return null;
    }
    
    const normalizedMsg = normalizeText(message);
    
    // 1. Búsqueda directa por clave
    if (chatData[normalizedMsg]) {
        return chatData[normalizedMsg];
    }
    
    // 2. Búsqueda por clave original (con espacios/guiones)
    for (const [key, value] of Object.entries(chatData)) {
        const normalizedKey = normalizeText(key);
        if (normalizedKey === normalizedMsg) {
            return value;
        }
        // Contención parcial
        if (normalizedMsg.includes(normalizedKey) || normalizedKey.includes(normalizedMsg)) {
            if (normalizedKey.length > 3) { // Evitar matches muy cortos
                return value;
            }
        }
    }
    
    // 3. Búsqueda por aliases
    for (const [key, value] of Object.entries(chatData)) {
        const aliases = value.alias || value.aliases || [];
        for (const alias of aliases) {
            if (normalizeText(alias) === normalizedMsg || normalizedMsg.includes(normalizeText(alias))) {
                return value;
            }
        }
    }
    
    // 4. Búsqueda por palabras clave
    const words = normalizedMsg.split(/\s+/).filter(w => w.length > 3);
    for (const word of words) {
        for (const [key, value] of Object.entries(chatData)) {
            const normalizedKey = normalizeText(key);
            if (normalizedKey.includes(word) || word.includes(normalizedKey)) {
                return value;
            }
        }
    }
    
    return null;
}

// Generar respuesta con presupuesto
function generateResponse(data, question) {
    if (!data) {
        return {
            text: 'Lo siento, no tengo información específica sobre eso. Para una valoración exacta, envíame una foto por WhatsApp 📸',
            hasBudget: false
        };
    }
    
    const pasos = data.pasos || data.steps || [];
    let responseText = pasos.join(' | ');
    
    // Detectar si hay presupuesto en los pasos
    const hasBudget = pasos.some(p => 
        p.toLowerCase().includes('presupuest') || 
        p.toLowerCase().includes('€') ||
        p.toLowerCase().includes('estimad')
    );
    
    // Añadir nota de WhatsApp si no hay presupuesto
    if (!hasBudget) {
        responseText += ' | Para valoración exacta, envíame una foto por WhatsApp 📸';
    }
    
    return {
        text: responseText,
        hasBudget: hasBudget
    };
}

// Añadir mensaje al chat
function addMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) {
        console.error('❌ Chat box not found');
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message message-' + sender;
    
    const label = sender === 'bot' ? '<strong>Fontanero Virtual 👷‍♂️</strong><br>' : '<strong>Tú 👤</strong><br>';
    messageDiv.innerHTML = label + escapeHtml(text);
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Escapar HTML para seguridad
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Función principal de envío
function sendMessage() {
    const input = document.getElementById('user-input');
    if (!input) {
        console.error('❌ User input not found');
        return;
    }
    
    const message = input.value.trim();
    if (!message) {
        console.log('⚠️ Empty message');
        return;
    }
    
    console.log('📤 Sending:', message);
    
    // Añadir mensaje del usuario
    addMessage('user', message);
    input.value = '';
    
    // Buscar y mostrar respuesta
    setTimeout(() => {
        const responseData = findResponse(message);
        const response = generateResponse(responseData, message);
        console.log('📥 Response:', response.text.substring(0, 50) + '...');
        addMessage('bot', response.text);
    }, 300); // Pequeño delay para simular pensamiento
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Fontanero Virtual initializing...');
    loadChatData();
    
    // Configurar evento Enter en el input
    const input = document.getElementById('user-input');
    if (input) {
        input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
            }
        });
        console.log('✅ Enter key listener attached');
    }
    
    // Mensaje de bienvenida si el chat está vacío
    setTimeout(() => {
        const chatBox = document.getElementById('chat-box');
        if (chatBox && chatBox.children.length <= 1) {
            console.log('✅ Chat ready');
        }
    }, 1000);
});

// Hacer sendMessage disponible globalmente para el onclick
window.sendMessage = sendMessage;

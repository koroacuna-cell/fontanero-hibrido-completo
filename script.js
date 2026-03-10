/**
 * Fontanero Virtual PRO v2.0 - Chat Inteligente con Preguntas de Seguimiento
 * Detección de intención, seguimiento conversacional y soporte bilingüe
 */

let chatData = {};
let isLoaded = false;
let currentLanguage = 'es';
let lastTopic = null;

// ===== CARGAR JSON =====
async function loadChatData() {
    try {
        const response = await fetch('json/responses.json');
        if (!response.ok) throw new Error('HTTP ' + response.status);
        chatData = await response.json();
        isLoaded = true;
        console.log('✅ Chat data loaded:', Object.keys(chatData).length, 'entries');
        updateLanguageUI();
    } catch (error) {
        console.error('❌ Error loading ', error);
        addMessage('bot', currentLanguage === 'es' ? 
            '⚠️ Error al cargar. Recarga la página o contacta por WhatsApp 📸' :
            '⚠️ Error loading. Refresh or contact WhatsApp 📸');
    }
}

// ===== CAMBIAR IDIOMA =====
function toggleLanguage() {
    currentLanguage = currentLanguage === 'es' ? 'en' : 'es';
    updateLanguageUI();
    addMessage('bot', currentLanguage === 'es' ?
        '🇪🇸 Idioma cambiado a ESPAÑOL' :
        '🇬🇧 Language changed to ENGLISH');
}

function updateLanguageUI() {
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) {
        langBtn.textContent = currentLanguage === 'es' ? '🇬🇧 EN' : '🇪🇸 ES';
    }
    const placeholder = document.getElementById('user-input');
    if (placeholder) {
        placeholder.placeholder = currentLanguage === 'es' ?
            'Ej: grifo gotea, quiero termo, urgencia...' :
            'Ex: dripping tap, want water heater, emergency...';
    }
}

// ===== NORMALIZAR TEXTO =====
function normalizeText(text) {
    return text.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[^\w\s]/g, '')
        .replace(/\s+/g, '_')
        .trim();
}

// ===== DETECTAR INTENCIÓN =====
function detectIntent(message) {
    const msg = message.toLowerCase();
    
    const productKeywords = ['comprar', 'nuevo', 'precio', 'cuánto cuesta', 'quiero un', 'catálogo', 
        'modelos', 'tienda', 'webador', 'disponibles', '50 litros', '80 litros', 'digital', 'híbrido'];
    
    const repairKeywords = ['reparar', 'arreglar', 'roto', 'averiado', 'no funciona', 'no calienta',
        'gotea', 'pierde', 'fuga', 'atasco', 'no cierra', 'no para', 'urgente', 'olor', 'huele'];
    
    const hasProduct = productKeywords.some(k => msg.includes(k));
    const hasRepair = repairKeywords.some(k => msg.includes(k));
    
    if (hasProduct && !hasRepair) return 'product';
    if (hasRepair && !hasProduct) return 'repair';
    if (hasProduct && hasRepair) {
        if (msg.includes('termo') && (msg.includes('nuevo') || msg.includes('comprar'))) return 'product';
        return 'repair';
    }
    
    return null;
}

// ===== FUZZY MATCHING =====
function similarity(s1, s2) {
    const longer = s1.length > s2.length ? s1 : s2;
    const shorter = s1.length > s2.length ? s2 : s1;
    if (longer.length === 0) return 1.0;
    const edits = levenshteinDistance(longer, shorter);
    return (longer.length - edits) / longer.length;
}

function levenshteinDistance(s1, s2) {
    const matrix = [];
    for (let i = 0; i <= s2.length; i++) matrix[i] = [i];
    for (let j = 0; j <= s1.length; j++) matrix[0][j] = j;
    for (let i = 1; i <= s2.length; i++) {
        for (let j = 1; j <= s1.length; j++) {
            if (s2.charAt(i-1) === s1.charAt(j-1)) {
                matrix[i][j] = matrix[i-1][j-1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i-1][j-1] + 1,
                    matrix[i][j-1] + 1,
                    matrix[i-1][j] + 1
                );
            }
        }
    }
    return matrix[s2.length][s1.length];
}

// ===== BUSCAR RESPUESTA CON CONTEXTO =====
function findResponse(message) {
    if (!isLoaded || Object.keys(chatData).length === 0) return null;
    
    const intent = detectIntent(message);
    const normalizedMsg = normalizeText(message);
    
    // 1. Búsqueda por intención + palabra clave
    if (intent) {
        const keywords = ['termo', 'grifo', 'cisterna', 'fuga', 'atasco', 'caldera', 'radiador', 
            'multicapa', 'pvc', 'sifon', 'latiguillo', 'mampara', 'ducha', 'lavadora', 'lavavajillas'];
        const foundKeyword = keywords.find(k => normalizedMsg.includes(k));
        
        if (foundKeyword) {
            const targetKey = `${foundKeyword}_${intent === 'product' ? 'producto' : 'reparacion'}`;
            if (chatData[targetKey]) {
                lastTopic = foundKeyword;
                console.log(`🎯 Match por intención: ${targetKey}`);
                return chatData[targetKey];
            }
        }
    }
    
    // 2. Búsqueda por aliases
    for (const [key, value] of Object.entries(chatData)) {
        const aliases = value.alias || value.aliases || [];
        for (const alias of aliases) {
            if (normalizeText(alias) === normalizedMsg) {
                console.log(`🎯 Match por alias: ${key}`);
                return value;
            }
        }
    }
    
    // 3. Fuzzy matching
    let bestMatch = null;
    let bestScore = 0.55;
    
    for (const [key, value] of Object.entries(chatData)) {
        const normalizedKey = normalizeText(key);
        const score = similarity(normalizedMsg, normalizedKey);
        
        if (score > bestScore) {
            bestScore = score;
            bestMatch = value;
        }
    }
    
    if (bestMatch) {
        console.log(`🎯 Fuzzy match: ${bestScore.toFixed(2)}`);
        return bestMatch;
    }
    
    // 4. Búsqueda por palabra clave simple
    for (const key of Object.keys(chatData)) {
        if (normalizedMsg.includes(normalizeText(key)) || 
            normalizeText(key).includes(normalizedMsg.split('_')[0])) {
            return chatData[key];
        }
    }
    
    return null;
}

// ===== GENERAR PREGUNTA DE SEGUIMIENTO =====
function generateFollowUp(data, question) {
    const msg = question.toLowerCase();
    
    // Si es sobre termo, preguntar capacidad
    if (msg.includes('termo') && !msg.includes('litro')) {
        return '💡 ¿De qué capacidad necesitas el termo? (50L, 80L, 100L)';
    }
    
    // Si es fuga, preguntar ubicación
    if (msg.includes('fuga') && !msg.includes('cocina') && !msg.includes('baño')) {
        return '💡 ¿Dónde está la fuga? (cocina, baño, terraza, pared)';
    }
    
    // Si es atasco, preguntar qué no desagua
    if (msg.includes('atasco') || msg.includes('desagüe')) {
        return '💡 ¿Qué no desagua? (fregadero, lavabo, ducha, bañera)';
    }
    
    return null;
}

// ===== GENERAR RESPUESTA =====
function generateResponse(data, question) {
    if (!data) {
        return {
            text: currentLanguage === 'es' ?
                'Lo siento, no tengo información específica. Para valoración exacta, envíame una foto por WhatsApp 📸' :
                'Sorry, no specific info. For exact quote, send photo via WhatsApp 📸',
            hasBudget: false,
            followUp: null
        };
    }
    
    const pasos = data.pasos || data.steps || [];
    let responseText = pasos.join(' | ');
    
    // Detectar presupuesto
    const hasBudget = pasos.some(p => 
        p.toLowerCase().includes('presupuest') || 
        p.toLowerCase().includes('€') ||
        p.toLowerCase().includes('estimad')
    );
    
    // Añadir pregunta de seguimiento
    const followUp = generateFollowUp(data, question);
    if (followUp) {
        responseText += ' | ' + followUp;
    }
    
    if (!hasBudget) {
        responseText += currentLanguage === 'es' ?
            ' | Para valoración exacta, envíame foto por WhatsApp 📸' :
            ' | For exact quote, send photo via WhatsApp 📸';
    }
    
    return { text: responseText, hasBudget, followUp };
}

// ===== AÑADIR MENSAJE AL CHAT =====
function addMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message message-' + sender;
    
    const label = sender === 'bot' ? 
        (currentLanguage === 'es' ? '<strong>Fontanero Virtual 👷‍♂️</strong><br>' : '<strong>Virtual Plumber 👷‍♂️</strong><br>') :
        (currentLanguage === 'es' ? '<strong>Tú 👤</strong><br>' : '<strong>You 👤</strong><br>');
    
    let escaped = escapeHtml(text);
    // Hacer enlaces clickeables y que se ajusten a pantalla
    escaped = escaped.replace(
        /https?:\/\/[^\s<"]+/g, 
        '<a href="$&" target="_blank" style="color:#0ea5e9;text-decoration:none;font-weight:500;word-break:break-all;display:inline-block;max-width:100%">$&</a>'
    );
    
    messageDiv.innerHTML = label + escaped;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== ENVIAR MENSAJE =====
function sendMessage() {
    const input = document.getElementById('user-input');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    console.log('📤 Sending:', message);
    console.log('🎯 Intent:', detectIntent(message));
    
    addMessage('user', message);
    input.value = '';
    
    setTimeout(() => {
        const responseData = findResponse(message);
        const response = generateResponse(responseData, message);
        console.log('📥 Response:', response.text.substring(0, 70) + '...');
        addMessage('bot', response.text);
    }, 400);
}

// ===== INICIALIZAR =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Fontanero Virtual PRO v2.0 initializing...');
    loadChatData();
    
    // Botón de idioma
    const header = document.querySelector('header .header-content');
    if (header) {
        const langBtn = document.createElement('button');
        langBtn.id = 'lang-toggle';
        langBtn.textContent = '🇬🇧 EN';
        langBtn.style.cssText = 'background:var(--accent);border:none;border-radius:6px;padding:0.4rem 0.75rem;cursor:pointer;font-weight:600;font-size:0.875rem';
        langBtn.onclick = toggleLanguage;
        header.appendChild(langBtn);
    }
    
    const input = document.getElementById('user-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
        });
        console.log('✅ Enter key listener attached');
    }
});

window.sendMessage = sendMessage;

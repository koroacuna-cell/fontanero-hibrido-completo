/**
 * Fontanero Virtual PRO v3.2 - Matching Semántico Mejorado
 * Entiende intención, contexto y lenguaje natural
 */

let chatData = {};
let isLoaded = false;
let userLanguage = null;
let conversationContext = { topic: null, lastAnswer: null, timestamp: null };

// ===== DETECTAR IDIOMA =====
function detectLanguage(text) {
    if (!text) return 'es';
    const enWords = ['water', 'heater', 'boiler', 'dripping', 'leak', 'fix', 'repair', 'urgent', 'price', 'cost', 'want', 'need', 'new', 'kitchen', 'bathroom', 'tap', 'faucet', 'pipe', 'drain'];
    const esWords = ['agua', 'termo', 'caldera', 'gotea', 'pierde', 'fuga', 'reparar', 'arreglar', 'urgente', 'precio', 'quiero', 'necesito', 'nuevo', 'cocina', 'baño', 'grifo', 'tuberia', 'desagüe'];
    const lower = text.toLowerCase();
    const enCount = enWords.filter(w => lower.includes(w)).length;
    const esCount = esWords.filter(w => lower.includes(w)).length;
    if (enCount > esCount) return 'en';
    if (esCount > enCount) return 'es';
    return userLanguage || 'es';
}

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
        addMessage('bot', getLangText('error_load'));
    }
}

// ===== TEXTOS POR IDIOMA =====
function getLangText(key) {
    const texts = {
        'es': {
            welcome: 'Hola, soy tu Fontanero Virtual. Pregúntame sobre grifos, termos, cisternas, fugas... y te ayudaré con solución + presupuesto estimado.',
            no_info: 'No tengo info específica. Para valoración exacta, envíame foto por WhatsApp 📸',
            followup_capacity: '💡 ¿De qué capacidad? (50L / 80L / 100L)',
            followup_location: '💡 ¿Dónde está? (cocina / baño / terraza / pared)',
            followup_kitchen_bath: '💡 ¿De cocina o baño?',
            lang_changed: '🇪🇸 Idioma cambiado a ESPAÑOL',
            placeholder: 'Ej: grifo gotea, quiero termo, urgencia...'
        },
        'en': {
            welcome: 'Hi, I\'m your Virtual Plumber. Ask me about taps, water heaters, leaks... and I\'ll help with solution + estimated quote.',
            no_info: 'Sorry, no specific info. For exact quote, send photo via WhatsApp 📸',
            followup_capacity: '💡 What capacity? (50L / 80L / 100L)',
            followup_location: '💡 Where is it? (kitchen / bathroom / terrace / wall)',
            followup_kitchen_bath: '💡 Kitchen or bathroom?',
            lang_changed: '🇬🇧 Language changed to ENGLISH',
            placeholder: 'Ex: dripping tap, want water heater, emergency...'
        }
    };
    const lang = userLanguage || detectLanguage('');
    return texts[lang]?.[key] || texts['es'][key];
}

function toggleLanguage() {
    userLanguage = userLanguage === 'es' ? 'en' : (userLanguage === 'en' ? null : 'es');
    updateLanguageUI();
    addMessage('bot', getLangText('lang_changed'));
}

function updateLanguageUI() {
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) langBtn.textContent = userLanguage === 'en' ? '🇪🇸 ES' : (userLanguage === 'es' ? '🇬🇧 EN' : '🌐 AUTO');
    const input = document.getElementById('user-input');
    if (input) input.placeholder = getLangText('placeholder');
}

// ===== NORMALIZACIÓN AVANZADA =====
function normalizeText(text) {
    if (!text) return '';
    return text.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .replace(/ç/g, 'c').replace(/ñ/g, 'n')
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, '_')
        .replace(/^_+|_+$/g, '')
        .trim();
}

// ===== EXTRAER PALABRAS CLAVE DE LA PREGUNTA =====
function extractKeywords(message) {
    const normalized = normalizeText(message);
    const words = normalized.split('_').filter(w => w.length > 2);
    
    // Palabras clave principales de fontanería
    const mainKeywords = ['termo', 'grifo', 'cisterna', 'fuga', 'atasco', 'caldera', 'radiador', 'llave', 'paso', 'desague', 'sifon', 'mampara', 'ducha', 'lavadora', 'lavavajillas', 'multicapa', 'pvc', 'latiguillo'];
    
    // Palabras de intención
    const productWords = ['comprar', 'nuevo', 'precio', 'cuanto', 'quiero', 'necesito', 'catalogo', 'webador', 'coste', 'valor', 'modelos'];
    const repairWords = ['reparar', 'arreglar', 'roto', 'averiado', 'gotea', 'pierde', 'no_funciona', 'no_calienta', 'fuga', 'urgente', 'error', 'codigo'];
    
    return {
        main: words.filter(w => mainKeywords.includes(w)),
        intent_product: words.some(w => productWords.includes(w)),
        intent_repair: words.some(w => repairWords.includes(w)),
        all: words
    };
}

// ===== DETECTAR INTENCIÓN MEJORADA =====
function detectIntent(message) {
    const kw = extractKeywords(message);
    
    // Si tiene palabras de producto y no de reparación → producto
    if (kw.intent_product && !kw.intent_repair) return 'product';
    // Si tiene palabras de reparación y no de producto → reparación
    if (kw.intent_repair && !kw.intent_product) return 'repair';
    
    // Si tiene ambas o ninguna, usar heurísticas
    const msg = message.toLowerCase();
    
    // Heurísticas para termo
    if (kw.main.includes('termo')) {
        if (msg.includes('comprar') || msg.includes('nuevo') || msg.includes('precio') || msg.includes('cuanto cuesta') || msg.includes('quiero un') || msg.includes('necesito un')) return 'product';
        return 'repair'; // por defecto para termo es reparación
    }
    
    // Heurísticas para grifo
    if (kw.main.includes('grifo') || kw.main.includes('llave')) {
        if (msg.includes('comprar') || msg.includes('nuevo') || msg.includes('precio') || msg.includes('cuanto vale') || msg.includes('quiero un')) return 'product';
        return 'repair';
    }
    
    // Por defecto: si no está claro, asumir reparación (más común)
    return 'repair';
}

// ===== FUZZY MATCHING =====
function similarity(s1, s2) {
    s1 = normalizeText(s1);
    s2 = normalizeText(s2);
    if (s1 === s2) return 1.0;
    if (!s1 || !s2) return 0;
    const longer = s1.length > s2.length ? s1 : s2;
    const shorter = s1.length > s2.length ? s2 : s1;
    if (longer.length === 0) return 1.0;
    
    // Levenshtein distance simplificada
    let edits = 0;
    let i = 0, j = 0;
    while (i < shorter.length && j < longer.length) {
        if (shorter[i] === longer[j]) { i++; j++; }
        else { edits++; j++; }
    }
    edits += longer.length - j;
    
    let score = (longer.length - edits) / longer.length;
    
    // Bonus por palabras comunes
    const s1Words = s1.split('_').filter(w => w.length > 2);
    const s2Words = s2.split('_').filter(w => w.length > 2);
    const common = s1Words.filter(w => s2Words.includes(w)).length;
    if (common >= 2) score = Math.min(1.0, score + 0.2);
    else if (common === 1) score = Math.min(1.0, score + 0.1);
    
    return score;
}

// ===== BUSCAR RESPUESTA INTELIGENTE =====
function findResponse(message) {
    if (!isLoaded || Object.keys(chatData).length === 0) return null;
    
    const kw = extractKeywords(message);
    const intent = detectIntent(message);
    const normalizedMsg = normalizeText(message);
    
    console.log(`🔍 Buscando: "${message}" | Keywords: [${kw.main.join(', ')}] | Intent: ${intent}`);
    
    // 1. Búsqueda directa por clave normalizada
    if (chatData[normalizedMsg]) {
        console.log(`✅ Match directo: ${normalizedMsg}`);
        return chatData[normalizedMsg];
    }
    
    // 2. Búsqueda por aliases (incluyendo variantes naturales)
    for (const [key, value] of Object.entries(chatData)) {
        const aliases = value.alias || value.aliases || [];
        for (const alias of aliases) {
            if (normalizeText(alias) === normalizedMsg) {
                console.log(`✅ Match alias: ${key}`);
                return value;
            }
            // Matching parcial: si la pregunta contiene el alias o viceversa
            if (normalizedMsg.includes(normalizeText(alias)) || normalizeText(alias).includes(normalizedMsg)) {
                if (normalizeText(alias).length > 3) { // evitar matches muy cortos
                    console.log(`✅ Match parcial alias: "${alias}" → ${key}`);
                    return value;
                }
            }
        }
    }
    
    // 3. Búsqueda por intención + palabra clave principal
    if (kw.main.length > 0 && intent) {
        for (const mainKw of kw.main) {
            const targetKey = `${mainKw}_${intent === 'product' ? 'producto' : 'reparacion'}`;
            if (chatData[targetKey]) {
                console.log(`✅ Match intención+keyword: ${targetKey}`);
                return chatData[targetKey];
            }
            // También probar variantes con guiones/espacios
            for (const [key, value] of Object.entries(chatData)) {
                if (key.includes(mainKw) && key.includes(intent === 'product' ? 'producto' : 'reparacion')) {
                    console.log(`✅ Match variante: ${key}`);
                    return value;
                }
            }
        }
    }
    
    // 4. Fuzzy matching con umbral flexible
    let bestMatch = null;
    let bestScore = 0.5; // Umbral más bajo para ser más permisivo
    
    for (const [key, value] of Object.entries(chatData)) {
        const normalizedKey = normalizeText(key);
        const score = similarity(normalizedMsg, normalizedKey);
        
        if (score > bestScore) {
            bestScore = score;
            bestMatch = value;
        }
        
        // También comparar con aliases usando fuzzy
        const aliases = value.alias || value.aliases || [];
        for (const alias of aliases) {
            const aliasScore = similarity(normalizedMsg, normalizeText(alias));
            if (aliasScore > bestScore) {
                bestScore = aliasScore;
                bestMatch = value;
            }
        }
    }
    
    if (bestMatch && bestScore >= 0.5) {
        console.log(`✅ Fuzzy match: ${bestScore.toFixed(2)}`);
        return bestMatch;
    }
    
    // 5. Búsqueda por contención de palabras clave simples
    for (const [key, value] of Object.entries(chatData)) {
        const keyWords = normalizeText(key).split('_').filter(w => w.length > 2);
        const common = kw.all.filter(w => keyWords.includes(w));
        if (common.length >= 2) {
            console.log(`✅ Match por palabras comunes: [${common.join(', ')}]`);
            return value;
        }
    }
    
    // 6. Fallback: buscar por palabra clave única si es muy específica
    if (kw.main.length === 1) {
        const singleKw = kw.main[0];
        for (const [key, value] of Object.entries(chatData)) {
            if (key.includes(singleKw) && !key.includes('_producto') && !key.includes('_reparacion')) {
                console.log(`✅ Match fallback: ${key}`);
                return value;
            }
        }
    }
    
    console.log('❌ No se encontró match');
    return null;
}

// ===== PREGUNTA DE SEGUIMIENTO =====
function generateFollowUp(data, question) {
    const kw = extractKeywords(question);
    
    if (kw.main.includes('termo') && !question.toLowerCase().match(/(50|80|100).*litro|litro.*(50|80|100)/)) {
        return getLangText('followup_capacity');
    }
    if ((kw.main.includes('fuga') || kw.main.includes('pierde') || kw.main.includes('gotea')) && !question.toLowerCase().includes('cocina') && !question.toLowerCase().includes('bano') && !question.toLowerCase().includes('baño')) {
        return getLangText('followup_location');
    }
    if (kw.main.includes('grifo') && !question.toLowerCase().includes('cocina') && !question.toLowerCase().includes('bano') && !question.toLowerCase().includes('baño') && !question.toLowerCase().includes('lavabo')) {
        return getLangText('followup_kitchen_bath');
    }
    return null;
}

// ===== GENERAR RESPUESTA CON PRECIO POR DEFECTO =====
function generateResponse(data, question) {
    if (!data) {
        // Fallback inteligente: sugerir temas relacionados
        const kw = extractKeywords(question);
        let suggestion = '';
        if (kw.main.includes('grifo')) suggestion = ' | Prueba preguntar: "grifo gotea" o "quiero grifo nuevo"';
        else if (kw.main.includes('termo')) suggestion = ' | Prueba: "termo no calienta" o "precio termo 80L"';
        else if (kw.main.includes('llave') || kw.main.includes('paso')) suggestion = ' | Prueba: "llave de paso gotea" o "cambiar llave general"';
        
        return {
            text: getLangText('no_info') + suggestion + ' | 📱 WhatsApp directo: https://wa.me/34603398960',
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
        p.toLowerCase().includes('estimad') ||
        p.match(/\d+\s*[-–]\s*\d+\s*€/i)
    );
    
    // Precio por defecto si no hay
    if (!hasBudget) {
        const kw = extractKeywords(question);
        let defaultPrice = 'desde 35€';
        if (kw.main.includes('termo')) defaultPrice = '60-120€ (reparación) | 195-1000€+ (producto)';
        else if (kw.main.includes('grifo') || kw.main.includes('llave')) defaultPrice = '40-70€';
        else if (kw.main.includes('cisterna')) defaultPrice = '60-140€';
        else if (kw.main.includes('fuga')) defaultPrice = '70-160€';
        
        const priceText = (userLanguage || detectLanguage(question)) === 'en' ? 
            `💰 Estimated: ${defaultPrice}. WhatsApp 📸` :
            `💰 Presupuesto: ${defaultPrice}. WhatsApp 📸`;
        responseText += ' | ' + priceText;
    }
    
    // Follow-up
    const followUp = generateFollowUp(data, question);
    if (followUp) responseText += ' | ' + followUp;
    
    return { text: responseText, hasBudget: true, followUp };
}

// ===== AÑADIR MENSAJE AL CHAT =====
function addMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message message-' + sender;
    
    const label = sender === 'bot' ? 
        ((userLanguage || detectLanguage('')) === 'en' ? '<strong>Virtual Plumber 👷‍♂️</strong><br>' : '<strong>Fontanero Virtual 👷‍♂️</strong><br>') :
        ((userLanguage || detectLanguage('')) === 'en' ? '<strong>You 👤</strong><br>' : '<strong>Tú 👤</strong><br>');
    
    let escaped = escapeHtml(text);
    escaped = escaped.replace(
        /https?:\/\/[^\s<"]+/g, 
        '<a href="$&" target="_blank" style="color:#0ea5e9;text-decoration:none;font-weight:500;word-break:break-all;display:inline;max-width:100%;overflow-wrap:break-word">$&</a>'
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
    
    if (!userLanguage) {
        userLanguage = detectLanguage(message);
        updateLanguageUI();
    }
    
    console.log('📤 Sending:', message, '| Lang:', userLanguage);
    addMessage('user', message);
    input.value = '';
    
    setTimeout(() => {
        const responseData = findResponse(message);
        const response = generateResponse(responseData, message);
        console.log('📥 Response:', response.text.substring(0, 80) + '...');
        addMessage('bot', response.text);
    }, 400);
}

// ===== INICIALIZAR =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Fontanero Virtual PRO v3.2 initializing...');
    loadChatData();
    
    const header = document.querySelector('header .header-content');
    if (header) {
        const langBtn = document.createElement('button');
        langBtn.id = 'lang-toggle';
        langBtn.textContent = '🌐 AUTO';
        langBtn.style.cssText = 'background:var(--accent);border:none;border-radius:6px;padding:0.4rem 0.75rem;cursor:pointer;font-weight:600;font-size:0.875rem;margin-left:0.5rem';
        langBtn.onclick = toggleLanguage;
        header.appendChild(langBtn);
    }
    
    const input = document.getElementById('user-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
        })


// 🔤 Normaliza texto para matching tolerante (typos, mayúsculas, acentos)
function normalizarTexto(texto) {
    return texto.toLowerCase()
        .normalize("NFD").replace(/[̀-ͯ]/g, "") // quitar acentos
        .replace(/[^\w\s]/g, " ") // quitar puntuación
        .replace(/\s+/g, " ").trim(); // espacios múltiples
}

// 🔍 Matching tolerante: busca coincidencias parciales y con typos leves
function buscarCoincidenciaTolerante(consulta, data) {
    const consultaNorm = normalizarTexto(consulta);
    const palabras = consultaNorm.split(' ').filter(p => p.length > 2);
    
    // 1. Búsqueda directa por clave
    if (data[consultaNorm]) return data[consultaNorm];
    
    // 2. Búsqueda por aliases con coincidencia parcial
    for (const [clave, entrada] of Object.entries(data)) {
        const aliases = Array.isArray(entrada.alias) ? entrada.alias : 
                       Array.isArray(entrada.aliases) ? entrada.aliases : [];
        for (const alias of aliases) {
            const aliasNorm = normalizarTexto(alias);
            // Coincidencia exacta, contenida o que contiene
            if (consultaNorm === aliasNorm || 
                consultaNorm.includes(aliasNorm) || 
                aliasNorm.includes(consultaNorm)) {
                return entrada;
            }
            // Coincidencia por palabras clave (2+ palabras en común)
            const aliasPalabras = aliasNorm.split(' ');
            const comunes = palabras.filter(p => aliasPalabras.includes(p));
            if (comunes.length >= 2 && palabras.length >= 2) {
                return entrada;
            }
        }
    }
    
    // 3. Fallback por categoría si la consulta menciona "termo" o "water heater"
    if (consultaNorm.includes('termo') || consultaNorm.includes('water') && consultaNorm.includes('heater')) {
        if (consultaNorm.includes('precio') || consultaNorm.includes('cuanto') || consultaNorm.includes('cost')) {
            return data['termo_pregunta_precio'] || data['termo_catalogo'];
        }
        if (consultaNorm.includes('mejor') || consultaNorm.includes('recomienda') || consultaNorm.includes('best')) {
            return data['termo_recomendacion'] || data['termo_catalogo'];
        }
        return data['termo_catalogo'];
    }
    
    // 4. Fallback genérico
    return data['ayuda'] || data['problemaGeneral'] || null;
}
;
    }
});

window.sendMessage = sendMessage;

/**
 * Fontanero Virtual PRO v2.1 - Tolerancia Avanzada a Errores
 * Soporta dictado por voz, typos, mayúsculas, palabras similares
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
            '⚠️ Error al cargar. Recarga o WhatsApp 📸' :
            '⚠️ Error loading. Refresh or WhatsApp 📸');
    }
}

// ===== IDIOMA =====
function toggleLanguage() {
    currentLanguage = currentLanguage === 'es' ? 'en' : 'es';
    updateLanguageUI();
    addMessage('bot', currentLanguage === 'es' ? '🇪🇸 ESPAÑOL' : '🇬🇧 ENGLISH');
}

function updateLanguageUI() {
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) langBtn.textContent = currentLanguage === 'es' ? '🇬🇧 EN' : '🇪🇸 ES';
    const input = document.getElementById('user-input');
    if (input) {
        input.placeholder = currentLanguage === 'es' ?
            'Ej: grifo gotea, quiero termo, urgencia...' :
            'Ex: dripping tap, want water heater, emergency...';
    }
}

// ===== NORMALIZACIÓN AVANZADA (tolera errores) =====
function normalizeText(text) {
    if (!text) return '';
    
    return text.toLowerCase()
        // Quitar tildes y caracteres especiales
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        // Reemplazar caracteres confusos por voz
        .replace(/ç/g, 'c').replace(/ñ/g, 'n')
        // Quitar puntuación excepto espacios
        .replace(/[^\w\s]/g, '')
        // Unificar espacios múltiples
        .replace(/\s+/g, '_')
        // Quitar espacios al inicio/final
        .trim();
}

// ===== GENERAR VARIANTES DE TYPOS COMUNES =====
function generateTypos(text) {
    const variants = [text];
    
    // Typos comunes por dictado por voz
    const voiceTypos = {
        'pierde': ['poerde', 'pierde', 'pierd', 'pierdeagua', 'pierde_agua'],
        'gotea': ['gotea', 'gote', 'goteaagua', 'gotea_agua'],
        'agua': ['agua', 'agu', 'aguas'],
        'termo': ['termo', 'term', 'termos', 'calentador'],
        'grifo': ['grifo', 'grif', 'grifos', 'canilla'],
        'cisterna': ['cisterna', 'cisterna', 'inodoro', 'wcter'],
        'fuga': ['fuga', 'fug', 'fugas', 'perdiendo'],
        'cocina': ['cocina', 'cosina', 'kocina'],
        'baño': ['bano', 'bano', 'baño', 'bath'],
        'urgente': ['urgente', 'urgencia', 'urjente', 'rapido', 'ya'],
    };
    
    for (const [correct, typos] of Object.entries(voiceTypos)) {
        if (text.includes(correct)) {
            for (const typo of typos) {
                variants.push(text.replace(new RegExp(correct, 'g'), typo));
            }
        }
    }
    
    // Variante sin guiones bajos
    if (text.includes('_')) {
        variants.push(text.replace(/_/g, ''));
    }
    
    // Variante con guiones bajos añadidos
    variants.push(text.replace(/\s/g, '_'));
    
    return [...new Set(variants)]; // Eliminar duplicados
}

// ===== FUZZY MATCHING MEJORADO (más permisivo) =====
function similarity(s1, s2) {
    // Normalizar primero
    s1 = normalizeText(s1);
    s2 = normalizeText(s2);
    
    if (s1 === s2) return 1.0;
    if (!s1 || !s2) return 0;
    
    const longer = s1.length > s2.length ? s1 : s2;
    const shorter = s1.length > s2.length ? s2 : s1;
    
    if (longer.length === 0) return 1.0;
    
    // Levenshtein distance
    const edits = levenshteinDistance(longer, shorter);
    const score = (longer.length - edits) / longer.length;
    
    // Bonus por contención de palabras clave
    const s1Words = s1.split('_').filter(w => w.length > 2);
    const s2Words = s2.split('_').filter(w => w.length > 2);
    const commonWords = s1Words.filter(w => s2Words.includes(w)).length;
    
    if (commonWords >= 2) return Math.min(1.0, score + 0.15);
    if (commonWords === 1) return Math.min(1.0, score + 0.08);
    
    return score;
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

// ===== DETECTAR INTENCIÓN (más flexible) =====
function detectIntent(message) {
    const msg = normalizeText(message);
    
    const productKeywords = ['comprar', 'nuevo', 'precio', 'cuanto_cuesta', 'quiero_un', 'catalogo', 
        'modelos', 'tienda', 'webador', 'disponibles', '50_litros', '80_litros', 'digital', 'hibrido',
        'cuantos_euros', 'valor', 'coste', 'tarifa'];
    
    const repairKeywords = ['reparar', 'arreglar', 'roto', 'averiado', 'no_funciona', 'no_calienta',
        'gotea', 'pierde', 'fuga', 'atasco', 'no_cierra', 'no_para', 'urgente', 'olor', 'huele',
        'gote', 'poerde', 'fug', 'atasc', 'urjente'];
    
    const hasProduct = productKeywords.some(k => msg.includes(k));
    const hasRepair = repairKeywords.some(k => msg.includes(k));
    
    if (hasProduct && !hasRepair) return 'product';
    if (hasRepair && !hasProduct) return 'repair';
    if (hasProduct && hasRepair) {
        if (msg.includes('termo') && (msg.includes('nuevo') || msg.includes('comprar') || msg.includes('quiero'))) return 'product';
        return 'repair';
    }
    
    return null;
}

// ===== BUSCAR RESPUESTA CON TOLERANCIA EXTREMA =====
function findResponse(message) {
    if (!isLoaded || Object.keys(chatData).length === 0) return null;
    
    const intent = detectIntent(message);
    const normalizedMsg = normalizeText(message);
    const variants = generateTypos(normalizedMsg);
    
    console.log(`🔍 Buscando: "${message}" → variants: [${variants.slice(0,3).join(', ')}...]`);
    
    // 1. Búsqueda directa por variantes
    for (const variant of variants) {
        if (chatData[variant]) {
            console.log(`✅ Match directo variante: ${variant}`);
            return chatData[variant];
        }
    }
    
    // 2. Búsqueda por intención + palabra clave con variantes
    if (intent) {
        const keywords = ['termo', 'grifo', 'cisterna', 'fuga', 'atasco', 'caldera', 'radiador', 
            'multicapa', 'pvc', 'sifon', 'latiguillo', 'mampara', 'ducha', 'lavadora', 'lavavajillas',
            'term', 'grif', 'cistern', 'fug', 'atasc'];
        
        for (const kw of keywords) {
            if (normalizedMsg.includes(kw) || variants.some(v => v.includes(kw))) {
                const baseKey = kw.replace(/[^a-z]/g, '');
                const targetKey = `${baseKey}_${intent === 'product' ? 'producto' : 'reparacion'}`;
                
                // Buscar con fuzzy en las claves
                for (const [key, value] of Object.entries(chatData)) {
                    if (key.includes(baseKey) && key.includes(intent === 'product' ? 'producto' : 'reparacion')) {
                        console.log(`✅ Match intención+keyword: ${key}`);
                        lastTopic = baseKey;
                        return value;
                    }
                }
            }
        }
    }
    
    // 3. Búsqueda por aliases con variantes
    for (const [key, value] of Object.entries(chatData)) {
        const aliases = value.alias || value.aliases || [];
        for (const alias of aliases) {
            const normalizedAlias = normalizeText(alias);
            const aliasVariants = generateTypos(normalizedAlias);
            
            if (variants.some(v => aliasVariants.includes(v)) || aliasVariants.some(v => variants.includes(v))) {
                console.log(`✅ Match alias con typo: ${key}`);
                return value;
            }
        }
    }
    
    // 4. Fuzzy matching con umbral más bajo (0.45)
    let bestMatch = null;
    let bestScore = 0.45; // Más permisivo que antes (0.55)
    
    for (const [key, value] of Object.entries(chatData)) {
        const normalizedKey = normalizeText(key);
        
        // Probar con todas las variantes del mensaje
        for (const variant of variants) {
            const score = similarity(variant, normalizedKey);
            if (score > bestScore) {
                bestScore = score;
                bestMatch = value;
                console.log(`🎯 Fuzzy: "${variant}" → "${key}" = ${score.toFixed(2)}`);
            }
        }
    }
    
    if (bestMatch) {
        console.log(`✅ Mejor fuzzy match: ${bestScore.toFixed(2)}`);
        return bestMatch;
    }
    
    // 5. Búsqueda por contención de palabras clave simples
    const msgWords = normalizedMsg.split('_').filter(w => w.length > 3);
    for (const [key, value] of Object.entries(chatData)) {
        const keyWords = normalizeText(key).split('_').filter(w => w.length > 3);
        const common = msgWords.filter(w => keyWords.includes(w));
        if (common.length >= 2) {
            console.log(`✅ Match por palabras comunes: ${common.join(', ')}`);
            return value;
        }
    }
    
    console.log('❌ No se encontró match');
    return null;
}

// ===== PREGUNTA DE SEGUIMIENTO =====
function generateFollowUp(data, question) {
    const msg = normalizeText(question);
    
    if (msg.includes('termo') && !msg.includes('litro') && !msg.includes('50') && !msg.includes('80') && !msg.includes('100')) {
        return '💡 ¿De qué capacidad? (50L / 80L / 100L)';
    }
    if ((msg.includes('fuga') || msg.includes('pierde')) && !msg.includes('cocina') && !msg.includes('bano') && !msg.includes('terr')) {
        return '💡 ¿Dónde está? (cocina / baño / terraza / pared)';
    }
    if (msg.includes('atasco') || msg.includes('desag') || msg.includes('no_desagua')) {
        return '💡 ¿Qué no desagua? (fregadero / lavabo / ducha / bañera)';
    }
    if (msg.includes('grifo') && !msg.includes('cocina') && !msg.includes('bano')) {
        return '💡 ¿De cocina o baño?';
    }
    
    return null;
}

// ===== GENERAR RESPUESTA CON PRECIO POR DEFECTO =====
function generateResponse(data, question) {
    if (!data) {
        return {
            text: currentLanguage === 'es' ?
                'No tengo info específica. Para valoración exacta, envíame foto por WhatsApp 📸' :
                'No specific info. For exact quote, send photo via WhatsApp 📸',
            hasBudget: false,
            followUp: null
        };
    }
    
    const pasos = data.pasos || data.steps || [];
    let responseText = pasos.join(' | ');
    
    // Detectar si ya tiene precio
    const hasBudget = pasos.some(p => 
        p.toLowerCase().includes('presupuest') || 
        p.toLowerCase().includes('€') ||
        p.toLowerCase().includes('estimad') ||
        p.match(/\d+\s*[-–]\s*\d+\s*€/i)
    );
    
    // Si NO tiene precio, añadir uno por defecto según contexto
    if (!hasBudget) {
        const msg = normalizeText(question);
        let defaultPrice = null;
        
        if (msg.includes('termo')) defaultPrice = '60-120€';
        else if (msg.includes('grifo')) defaultPrice = '40-70€';
        else if (msg.includes('cisterna')) defaultPrice = '60-140€';
        else if (msg.includes('fuga') || msg.includes('pierde')) defaultPrice = '70-160€';
        else if (msg.includes('atasco') || msg.includes('desag')) defaultPrice = '50-100€';
        else if (msg.includes('lavadora') || msg.includes('lavavajillas')) defaultPrice = '35-70€';
        else if (msg.includes('caldera') || msg.includes('radiador')) defaultPrice = '70-130€';
        else defaultPrice = 'desde 35€';
        
        responseText += ` | 💰 Presupuesto orientativo: ${defaultPrice}. Para exacto, WhatsApp 📸`;
    }
    
    // Añadir pregunta de seguimiento
    const followUp = generateFollowUp(data, question);
    if (followUp) {
        responseText += ' | ' + followUp;
    }
    
    return { text: responseText, hasBudget: true, followUp };
}

// ===== AÑADIR MENSAJE (con enlaces que no rompen layout) =====
function addMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message message-' + sender;
    
    const label = sender === 'bot' ? 
        (currentLanguage === 'es' ? '<strong>Fontanero Virtual 👷‍♂️</strong><br>' : '<strong>Virtual Plumber 👷‍♂️</strong><br>') :
        (currentLanguage === 'es' ? '<strong>Tú 👤</strong><br>' : '<strong>You 👤</strong><br>');
    
    let escaped = escapeHtml(text);
    // Enlaces que se ajustan a pantalla
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
    
    console.log('📤 Sending:', message);
    console.log('🎯 Intent:', detectIntent(message));
    
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
    console.log('🚀 Fontanero Virtual PRO v2.1 initializing...');
    loadChatData();
    
    // Botón idioma
    const header = document.querySelector('header .header-content');
    if (header) {
        const langBtn = document.createElement('button');
        langBtn.id = 'lang-toggle';
        langBtn.textContent = '🇬🇧 EN';
        langBtn.style.cssText = 'background:var(--accent);border:none;border-radius:6px;padding:0.4rem 0.75rem;cursor:pointer;font-weight:600;font-size:0.875rem;margin-left:0.5rem';
        langBtn.onclick = toggleLanguage;
        header.appendChild(langBtn);
    }
    
    const input = document.getElementById('user-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
        });
    }
});

window.sendMessage = sendMessage;

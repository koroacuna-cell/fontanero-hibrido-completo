/**
 * Fontanero Virtual PRO v2.2 - Idioma Consistente + Contexto Conversacional
 * Responde en el idioma del usuario, recuerda contexto, tolera typos EN/ES
 */

let chatData = {};
let isLoaded = false;
let userLanguage = null; // 'es', 'en', o null (auto-detect)
let conversationContext = { topic: null, lastAnswer: null, timestamp: null };

// ===== DETECTAR IDIOMA DEL MENSAJE =====
function detectLanguage(text) {
    if (!text) return 'es';
    
    const enWords = ['water', 'heater', 'boiler', 'dripping', 'leak', 'fix', 'repair', 
        'urgent', 'emergency', 'price', 'cost', 'want', 'need', 'new', 'liters', 'litres',
        'kitchen', 'bathroom', 'tap', 'faucet', 'pipe', 'drain', 'clogged', 'broken'];
    
    const esWords = ['agua', 'termo', 'caldera', 'gotea', 'pierde', 'fuga', 'reparar', 
        'arreglar', 'urgente', 'emergencia', 'precio', 'coste', 'quiero', 'necesito', 'nuevo',
        'litros', 'cocina', 'baño', 'grifo', 'tuberia', 'desagüe', 'atasco', 'roto'];
    
    const lower = text.toLowerCase();
    const enCount = enWords.filter(w => lower.includes(w)).length;
    const esCount = esWords.filter(w => lower.includes(w)).length;
    
    if (enCount > esCount) return 'en';
    if (esCount > enCount) return 'es';
    
    // Si hay empate, usar último idioma usado o español por defecto
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
            welcome: 'Hola, soy tu Fontanero Virtual. Pregúntame sobre grifos, termos, cisternas, fugas, desagües, mamparas, reformas... y te ayudaré con solución + presupuesto estimado.',
            no_info: 'Lo siento, no tengo información específica. Para valoración exacta, envíame una foto por WhatsApp 📸',
            followup_capacity: '💡 ¿De qué capacidad? (50L / 80L / 100L)',
            followup_location: '💡 ¿Dónde está? (cocina / baño / terraza / pared)',
            followup_drain: '💡 ¿Qué no desagua? (fregadero / lavabo / ducha / bañera)',
            followup_kitchen_bath: '💡 ¿De cocina o baño?',
            lang_changed: '🇪🇸 Idioma cambiado a ESPAÑOL',
            placeholder: 'Ej: grifo gotea, quiero termo, urgencia...'
        },
        'en': {
            welcome: 'Hi, I\'m your Virtual Plumber. Ask me about taps, water heaters, cisterns, leaks, drains, showers, bathroom renovations... and I\'ll help with solution + estimated quote.',
            no_info: 'Sorry, no specific info. For exact quote, send photo via WhatsApp 📸',
            followup_capacity: '💡 What capacity? (50L / 80L / 100L)',
            followup_location: '💡 Where is it? (kitchen / bathroom / terrace / wall)',
            followup_drain: '💡 What won\'t drain? (sink / washbasin / shower / bathtub)',
            followup_kitchen_bath: '💡 Kitchen or bathroom?',
            lang_changed: '🇬🇧 Language changed to ENGLISH',
            placeholder: 'Ex: dripping tap, want water heater, emergency...'
        }
    };
    const lang = userLanguage || detectLanguage('');
    return texts[lang]?.[key] || texts['es'][key];
}

// ===== CAMBIAR IDIOMA MANUAL =====
function toggleLanguage() {
    userLanguage = userLanguage === 'es' ? 'en' : (userLanguage === 'en' ? null : 'en');
    updateLanguageUI();
    addMessage('bot', getLangText('lang_changed'));
}

function updateLanguageUI() {
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) {
        if (userLanguage === 'en') langBtn.textContent = '🇪🇸 ES';
        else if (userLanguage === 'es') langBtn.textContent = '🇬🇧 EN';
        else langBtn.textContent = '🌐 AUTO';
    }
    const input = document.getElementById('user-input');
    if (input) {
        input.placeholder = getLangText('placeholder');
    }
}

// ===== NORMALIZACIÓN AVANZADA (EN + ES) =====
function normalizeText(text) {
    if (!text) return '';
    
    return text.toLowerCase()
        // Quitar tildes
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        // Reemplazar caracteres confusos
        .replace(/ç/g, 'c').replace(/ñ/g, 'n').replace(/ß/g, 'ss')
        // Correcciones comunes de dictado/typos EN
        .replace(/\bwater\s*heter\b/g, 'water_heater')
        .replace(/\bwater\s*heater\b/g, 'termo')
        .replace(/\bboiler\b/g, 'caldera')
        .replace(/\bdripping\b/g, 'gotea')
        .replace(/\bleak\b/g, 'fuga')
        .replace(/\bfix\b|\brepair\b/g, 'reparar')
        .replace(/\burgent\b|\bemergency\b/g, 'urgente')
        .replace(/\bprice\b|\bcost\b/g, 'precio')
        .replace(/\bliters?\b|\blitres?\b/g, 'litros')
        .replace(/\bfifty\b/g, '50').replace(/\beighty\b/g, '80').replace(/\bone\s*hundred\b/g, '100')
        .replace(/\bkitchen\b/g, 'cocina').replace(/\bbathroom\b/g, 'bano')
        .replace(/\btap\b|\bfaucet\b/g, 'grifo')
        .replace(/\bpipe\b/g, 'tuberia').replace(/\bdrain\b/g, 'desague')
        .replace(/\bclogged\b|\bblocked\b/g, 'atasco')
        .replace(/\bbroken\b/g, 'roto')
        // Correcciones comunes ES
        .replace(/\bpoerde\b/g, 'pierde')
        .replace(/\bgote\b/g, 'gotea')
        .replace(/\bfug\b/g, 'fuga')
        .replace(/\batasc\b/g, 'atasco')
        .replace(/\burjente\b/g, 'urgente')
        .replace(/\bcosina\b|\bkocina\b/g, 'cocina')
        .replace(/\bbano\b/g, 'bano')
        // Quitar puntuación
        .replace(/[^\w\s]/g, '')
        // Unificar espacios
        .replace(/\s+/g, '_')
        .trim();
}

// ===== GENERAR VARIANTES DE TYPOS =====
function generateTypos(text) {
    const variants = [text];
    
    // Typos comunes EN/ES
    const typos = {
        'termo': ['termo', 'term', 'termos', 'calentador', 'water_heater', 'boiler'],
        'grifo': ['grifo', 'grif', 'grifos', 'canilla', 'tap', 'faucet'],
        'cisterna': ['cisterna', 'cistern', 'inodoro', 'wc', 'toilet'],
        'fuga': ['fuga', 'fug', 'fugas', 'leak', 'pierde', 'poerde'],
        'gotea': ['gotea', 'gote', 'goteando', 'dripping', 'drip'],
        'cocina': ['cocina', 'cosina', 'kitchen'],
        'bano': ['bano', 'bano', 'bathroom', 'bath'],
        'urgente': ['urgente', 'urgencia', 'urjente', 'urgent', 'emergency', 'rapido', 'ya'],
        'litros': ['litros', 'litro', 'liters', 'litres', 'l', '50l', '80l', '100l'],
    };
    
    for (const [correct, variants_list] of Object.entries(typos)) {
        if (text.includes(correct)) {
            for (const typo of variants_list) {
                variants.push(text.replace(new RegExp(correct, 'g'), typo));
            }
        }
    }
    
    // Variantes con/sin guiones
    if (text.includes('_')) variants.push(text.replace(/_/g, ''));
    variants.push(text.replace(/\s/g, '_'));
    
    return [...new Set(variants)];
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
    
    const edits = levenshteinDistance(longer, shorter);
    let score = (longer.length - edits) / longer.length;
    
    // Bonus por palabras comunes
    const s1Words = s1.split('_').filter(w => w.length > 2);
    const s2Words = s2.split('_').filter(w => w.length > 2);
    const common = s1Words.filter(w => s2Words.includes(w)).length;
    
    if (common >= 2) score = Math.min(1.0, score + 0.15);
    else if (common === 1) score = Math.min(1.0, score + 0.08);
    
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

// ===== DETECTAR INTENCIÓN =====
function detectIntent(message) {
    const msg = normalizeText(message);
    
    const product = ['comprar', 'nuevo', 'precio', 'cuanto_cuesta', 'quiero_un', 'catalogo', 
        'modelos', 'tienda', 'webador', 'disponibles', 'digital', 'hibrido', 'coste', 'tarifa',
        'want', 'need', 'new', 'price', 'cost', 'buy', 'catalog'];
    
    const repair = ['reparar', 'arreglar', 'roto', 'averiado', 'no_funciona', 'no_calienta',
        'gotea', 'pierde', 'fuga', 'atasco', 'no_cierra', 'no_para', 'urgente', 'olor', 'huele',
        'fix', 'repair', 'broken', 'leak', 'dripping', 'clogged', 'urgent', 'emergency'];
    
    const hasProduct = product.some(k => msg.includes(k));
    const hasRepair = repair.some(k => msg.includes(k));
    
    if (hasProduct && !hasRepair) return 'product';
    if (hasRepair && !hasProduct) return 'repair';
    if (hasProduct && hasRepair) {
        if (msg.includes('termo') || msg.includes('water_heater') || msg.includes('boiler')) {
            if (msg.includes('nuevo') || msg.includes('comprar') || msg.includes('quiero') || msg.includes('want') || msg.includes('need')) return 'product';
        }
        return 'repair';
    }
    return null;
}

// ===== ACTUALIZAR CONTEXTO CONVERSACIONAL =====
function updateContext(topic, answer) {
    conversationContext = {
        topic: topic,
        lastAnswer: answer,
        timestamp: Date.now()
    };
}

function getContextResponse(message) {
    const now = Date.now();
    const msg = normalizeText(message);
    
    // Si es hace menos de 30 segundos y hay contexto
    if (conversationContext.topic && (now - conversationContext.timestamp) < 30000) {
        // Respuesta sobre capacidad de termo
        if (conversationContext.topic === 'termo' && (msg.includes('50') || msg.includes('80') || msg.includes('100') || msg.includes('litro'))) {
            const capacity = msg.match(/(50|80|100)/)?.[0] || '50';
            return {
                text: `✅ Termo de ${capacity}L disponible. 🛒 Precios: ${capacity === '50' ? 'desde 195€' : capacity === '80' ? 'desde 350€' : 'desde 500€'} (básico) hasta 700€+ (digital) y 1000€+ (híbrido). | 🔗 Ver modelos: https://fontaneriaeduardoquiroz.webador.es | 💰 Instalación + producto desde 250€. WhatsApp 📸`,
                hasBudget: true
            };
        }
        // Respuesta sobre ubicación de fuga
        if (conversationContext.topic === 'fuga' && (msg.includes('cocina') || msg.includes('bano') || msg.includes('terr'))) {
            return {
                text: `✅ Fuga en ${msg.includes('cocina') ? 'cocina' : msg.includes('bano') ? 'baño' : 'terraza'}. 💰 Reparación estimada: 70-160€ según acceso. Cierra llave de paso si es grave. Envía foto por WhatsApp 📸`,
                hasBudget: true
            };
        }
    }
    return null;
}

// ===== BUSCAR RESPUESTA =====
function findResponse(message) {
    if (!isLoaded || Object.keys(chatData).length === 0) return null;
    
    // 1. Verificar contexto conversacional primero
    const contextResp = getContextResponse(message);
    if (contextResp) {
        console.log('🎯 Match por contexto:', contextResp.text.substring(0, 50));
        return { pasos: [contextResp.text], hasBudget: contextResp.hasBudget };
    }
    
    const intent = detectIntent(message);
    const normalizedMsg = normalizeText(message);
    const variants = generateTypos(normalizedMsg);
    const lang = detectLanguage(message);
    
    console.log(`🔍 Buscando: "${message}" (lang: ${lang}) → variants: [${variants.slice(0,3).join(', ')}...]`);
    
    // 2. Búsqueda directa por variantes
    for (const variant of variants) {
        if (chatData[variant]) {
            console.log(`✅ Match directo variante: ${variant}`);
            updateContext(variant.split('_')[0], chatData[variant]);
            return chatData[variant];
        }
    }
    
    // 3. Búsqueda por intención + keyword
    if (intent) {
        const keywords = ['termo', 'grifo', 'cisterna', 'fuga', 'atasco', 'caldera', 'radiador', 
            'multicapa', 'pvc', 'sifon', 'latiguillo', 'mampara', 'ducha', 'lavadora', 'lavavajillas',
            'llave_paso', 'humedades', 'plato_ducha'];
        
        for (const kw of keywords) {
            if (normalizedMsg.includes(kw) || variants.some(v => v.includes(kw))) {
                const targetKey = `${kw}_${intent === 'product' ? 'producto' : 'reparacion'}`;
                if (chatData[targetKey]) {
                    console.log(`✅ Match intención+keyword: ${targetKey}`);
                    updateContext(kw, chatData[targetKey]);
                    return chatData[targetKey];
                }
            }
        }
    }
    
    // 4. Búsqueda por aliases
    for (const [key, value] of Object.entries(chatData)) {
        const aliases = value.alias || value.aliases || [];
        for (const alias of aliases) {
            const normalizedAlias = normalizeText(alias);
            const aliasVariants = generateTypos(normalizedAlias);
            if (variants.some(v => aliasVariants.includes(v)) || aliasVariants.some(v => variants.includes(v))) {
                console.log(`✅ Match alias con typo: ${key}`);
                updateContext(key.split('_')[0], value);
                return value;
            }
        }
    }
    
    // 5. Fuzzy matching (umbral 0.45)
    let bestMatch = null;
    let bestScore = 0.45;
    
    for (const [key, value] of Object.entries(chatData)) {
        const normalizedKey = normalizeText(key);
        for (const variant of variants) {
            const score = similarity(variant, normalizedKey);
            if (score > bestScore) {
                bestScore = score;
                bestMatch = value;
            }
        }
    }
    
    if (bestMatch) {
        console.log(`✅ Mejor fuzzy: ${bestScore.toFixed(2)}`);
        updateContext(Object.keys(chatData).find(k => chatData[k] === bestMatch)?.split('_')[0], bestMatch);
        return bestMatch;
    }
    
    // 6. Búsqueda por palabras clave simples
    const msgWords = normalizedMsg.split('_').filter(w => w.length > 3);
    for (const [key, value] of Object.entries(chatData)) {
        const keyWords = normalizeText(key).split('_').filter(w => w.length > 3);
        const common = msgWords.filter(w => keyWords.includes(w));
        if (common.length >= 2) {
            console.log(`✅ Match palabras comunes: ${common.join(', ')}`);
            updateContext(key.split('_')[0], value);
            return value;
        }
    }
    
    console.log('❌ No match');
    return null;
}

// ===== PREGUNTA DE SEGUIMIENTO =====
function generateFollowUp(data, question) {
    const msg = normalizeText(question);
    
    if (msg.includes('termo') && !msg.match(/(50|80|100).*litro|litro.*(50|80|100)/)) {
        return getLangText('followup_capacity');
    }
    if ((msg.includes('fuga') || msg.includes('pierde') || msg.includes('leak')) && !msg.includes('cocina') && !msg.includes('bano')) {
        return getLangText('followup_location');
    }
    if (msg.includes('atasco') || msg.includes('desag') || msg.includes('clogged')) {
        return getLangText('followup_drain');
    }
    if (msg.includes('grifo') && !msg.includes('cocina') && !msg.includes('bano')) {
        return getLangText('followup_kitchen_bath');
    }
    return null;
}

// ===== GENERAR RESPUESTA CON PRECIO POR DEFECTO =====
function generateResponse(data, question) {
    if (!data) {
        return {
            text: getLangText('no_info'),
            hasBudget: false,
            followUp: null
        };
    }
    
    const pasos = data.pasos || data.steps || [];
    let responseText = pasos.join(' | ');
    
    // Detectar precio
    const hasBudget = pasos.some(p => 
        p.toLowerCase().includes('presupuest') || 
        p.toLowerCase().includes('€') ||
        p.toLowerCase().includes('estimad') ||
        p.match(/\d+\s*[-–]\s*\d+\s*€/i)
    );
    
    // Precio por defecto si no hay
    if (!hasBudget) {
        const msg = normalizeText(question);
        let defaultPrice = 'desde 35€';
        
        if (msg.includes('termo') || msg.includes('water_heater') || msg.includes('boiler')) defaultPrice = '60-120€ (reparación) | 195-1000€+ (producto)';
        else if (msg.includes('grifo') || msg.includes('tap') || msg.includes('faucet')) defaultPrice = '40-70€';
        else if (msg.includes('cisterna') || msg.includes('toilet')) defaultPrice = '60-140€';
        else if (msg.includes('fuga') || msg.includes('pierde') || msg.includes('leak')) defaultPrice = '70-160€';
        else if (msg.includes('atasco') || msg.includes('desag') || msg.includes('clogged')) defaultPrice = '50-100€';
        else if (msg.includes('lavadora') || msg.includes('lavavajillas')) defaultPrice = '35-70€';
        else if (msg.includes('caldera') || msg.includes('boiler')) defaultPrice = '70-130€';
        else if (msg.includes('llave_paso') || msg.includes('llave general')) defaultPrice = '50-90€';
        
        const priceText = userLanguage === 'en' ? 
            `💰 Estimated quote: ${defaultPrice}. For exact, WhatsApp 📸` :
            `💰 Presupuesto orientativo: ${defaultPrice}. Para exacto, WhatsApp 📸`;
        
        responseText += ' | ' + priceText;
    }
    
    // Follow-up
    const followUp = generateFollowUp(data, question);
    if (followUp) responseText += ' | ' + followUp;
    
    return { text: responseText, hasBudget: true, followUp };
}

// ===== AÑADIR MENSAJE =====
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
    
    // Auto-detectar idioma si no está forzado
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
    console.log('🚀 Fontanero Virtual PRO v2.2 initializing...');
    loadChatData();
    
    // Botón idioma
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
        });
    }
});

window.sendMessage = sendMessage;

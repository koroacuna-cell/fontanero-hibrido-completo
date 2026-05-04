from flask import Flask, request, jsonify, send_from_directory
import json, os, re, datetime

app = Flask(__name__, static_folder='.', static_url_path='')

RESPONSES_FILE = 'json/Fontanero_Virtual_J_JSON_2.json'
AUDIT_FILE = 'logs/audit.json'
VISITS_FILE = 'data/visits.json'

os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# ──────────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────────
def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ──────────────────────────────────────────────────────────────
# CONTADOR DE VISITAS
# ──────────────────────────────────────────────────────────────
def track_visit(client_ip):
    real_ip = request.headers.get('X-Forwarded-For', client_ip).split(',')[0].strip()
    visits = load_json(VISITS_FILE, {"total": 0, "by_date": {}, "by_ip": {}})
    today = datetime.date.today().isoformat()
    visits["total"] += 1
    visits["by_date"][today] = visits["by_date"].get(today, 0) + 1
    visits["by_ip"][real_ip] = visits["by_ip"].get(real_ip, 0) + 1
    if len(visits["by_ip"]) > 1000:
        visits["by_ip"] = dict(list(visits["by_ip"].items())[-500:])
    save_json(VISITS_FILE, visits)
    return visits["total"]

@app.before_request
def before_req():
    track_visit(request.remote_addr)

# ──────────────────────────────────────────────────────────────
# MOTOR DE MATCHING SEMÁNTICO (compatible con tu JSON actual)
# ──────────────────────────────────────────────────────────────
STOP_WORDS = {"el", "la", "los", "las", "un", "una", "de", "del", "al", "con", "por", "para", "y", "o", "que", "en", "mi", "tu", "se", "es", "no", "si", "como", "cuando", "donde", "su", "sus", "este", "esta", "a", "o"}
CONNECTORS = {"de", "del", "la", "el", "que", "en", "un", "una", "para", "con"}

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)
    return re.sub(r'\s+', ' ', text)

def score_match(query, category_key, pasos_text):
    q_norm = normalize(query)
    q_words = set(q_norm.split()) - STOP_WORDS
    
    # Palabras objetivo: nombre de categoría + palabras clave de los pasos
    t_words = set(normalize(category_key).split() + normalize(pasos_text).split()) - STOP_WORDS
    
    if not q_words or not t_words: return 0.0
    
    # Coincidencia exacta de categoría → puntuación máxima
    if category_key in q_norm or q_norm in category_key: return 1.0
    
    # Jaccard + bonus por conectores presentes
    union = q_words | t_words
    if not union: return 0.0
    intersection = q_words & t_words
    score = len(intersection) / len(union)
    conn_bonus = sum(0.05 for c in CONNECTORS if c in q_norm and c in t_words)
    return min(score + conn_bonus, 1.0)

def find_best_response(query, knowledge):
    candidates = []
    for key, data in knowledge.items():
        pasos_list = data.get("pasos", [])
        pasos_text = " ".join(pasos_list) if isinstance(pasos_list, list) else str(pasos_list)
        score = score_match(query, key, pasos_text)
        if score >= 0.35:  # Umbral bajo para captar coincidencias parciales
            response = "\n".join(pasos_list) if isinstance(pasos_list, list) else str(pasos_list)
            candidates.append((key, score, response))
            
    if not candidates: return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0]

# ──────────────────────────────────────────────────────────────
# AUDITORÍA
# ──────────────────────────────────────────────────────────────
def log_audit(query, alias, score, ip):
    audit = load_json(AUDIT_FILE, [])
    audit.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "matched_alias": alias,
        "score": round(score, 3),
        "ip": request.headers.get('X-Forwarded-For', ip).split(',')[0].strip()
    })
    if len(audit) > 2000:
        audit = audit[-2000:]
    save_json(AUDIT_FILE, audit)

# ──────────────────────────────────────────────────────────────
# RUTAS
# ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        query = data.get('message', '').strip()
        if not query:
            return jsonify({"response": "Describe tu consulta de fontanería."})
            
        knowledge = load_json(RESPONSES_FILE, {})
        result = find_best_response(query, knowledge)
        
        if result:
            key, score, response = result
            log_audit(query, key, score, request.remote_addr)
            return jsonify({"response": response, "matched_alias": key, "confidence": round(score, 2)})
        else:
            log_audit(query, None, 0.0, request.remote_addr)
            return jsonify({
                "response": "No encontré respuesta exacta. Prueba con: grifo, fuga, termo, ducha, cisterna o precio.",
                "matched_alias": None,
                "confidence": 0.0
            })
    except Exception as e:
        return jsonify({"response": "Error interno. Intenta de nuevo."}), 500

@app.route('/audit')
def get_audit():
    limit = request.args.get('limit', 20, type=int)
    audit = load_json(AUDIT_FILE, [])
    return jsonify({"total_entries": len(audit), "recent": audit[-limit:][::-1]})

@app.route('/stats')
def get_stats():
    visits = load_json(VISITS_FILE, {"total": 0, "by_date": {}, "by_ip": {}})
    audit = load_json(AUDIT_FILE, [])
    total_q = len(audit)
    matched = sum(1 for a in audit if a.get('matched_alias'))
    return jsonify({
        "visits": visits["total"],
        "queries": total_q,
        "matched": matched,
        "unmatched": total_q - matched,
        "match_rate": round((matched/total_q)*100, 1) if total_q > 0 else 0,
        "today_visits": visits["by_date"].get(datetime.date.today().isoformat(), 0)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

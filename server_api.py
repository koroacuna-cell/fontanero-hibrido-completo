from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Cargar maestro_local.json
with open('maestro_local.json', 'r', encoding='utf-8') as f:
    maestro = json.load(f)

@app.route('/api/responder', methods=['POST'])
def responder():
    data = request.json
    pregunta = data.get('pregunta', '').lower()
    
    # Búsqueda simple (puedes mejorar con difflib como el motor v4)
    for clave, valor in maestro.items():
        if clave in pregunta or any(alias in pregunta for alias in valor.get('alias', [])):
            return jsonify({
                'respuesta': ' | '.join(valor.get('pasos', [])),
                'clave': clave
            })
    
    return jsonify({
        'respuesta': 'Lo siento, no entiendo la pregunta. Envía una foto por WhatsApp 📸',
        'clave': None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

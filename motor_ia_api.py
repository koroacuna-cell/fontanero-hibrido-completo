
from flask import Flask, request, jsonify
from motor_ia import MotorIA

app = Flask(__name__)
motor = MotorIA()

@app.route("/evaluar", methods=["POST"])
def evaluar_texto():
    data = request.get_json()

    if not data or "texto" not in data:
        return jsonify({"error": "Falta el campo 'texto'"}), 400

    resultado = motor.evaluar(data["texto"])
    return jsonify(resultado)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "mensaje": "Motor IA Fontanero funcionando",
        "endpoint": "/evaluar (POST, JSON)"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)

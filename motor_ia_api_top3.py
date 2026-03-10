from flask import Flask, request, jsonify
from motor_ia import MotorIA

app = Flask(__name__)
motor = MotorIA()

# Configuración: Top N resultados a devolver
TOP_N = 3

@app.route("/evaluar", methods=["POST"])
def evaluar_texto():
    try:
        data = request.get_json()
        texto = data.get("texto", "")
        resultados = motor.evaluar(texto)
        
        # Devolver solo los Top N
        top_n_resultados = resultados[:TOP_N]
        return jsonify(top_n_resultados)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)

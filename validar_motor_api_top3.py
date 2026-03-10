import json
import requests

# Configura tu endpoint
URL = "http://127.0.0.1:5005/evaluar"
TOP_N = 3

# Cargar tests
with open("tests_motor.json", "r", encoding="utf-8") as f:
    tests = json.load(f)

for test in tests:
    texto = test["texto"]
    esperado = test["esperado"]

    # POST al servidor Flask
    try:
        r = requests.post(URL, json={"texto": texto})
        r.raise_for_status()
        resultados = r.json()
    except Exception as e:
        print(f"❌ Error al consultar '{texto}': {e}")
        continue

    # Mostrar resultados Top-N
    etiquetas_top = [res["etiqueta"] for res in resultados]
    correcto = "✅" if esperado in etiquetas_top else "❌"

    print(f"\n{correcto} Consulta: {texto}")
    print(f"   Esperado: {esperado}")
    for i, res in enumerate(resultados, start=1):
        print(f"   Top {i}: {res['etiqueta']} ({res['porcentaje']}%)")
        for c in res["coincidencias"]:
            print(f"      - {c[0]}: {c[1]}")

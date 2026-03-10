import json
from motor_ia import MotorIA

# Cargar motor
motor = MotorIA()

# Cargar tests
with open("tests_motor.json", "r", encoding="utf-8") as f:
    tests = json.load(f)

# Ejecutar tests mostrando las top 3 coincidencias
for test in tests:
    texto = test["texto"]
    esperado = test["esperado"]
    resultados = [motor.evaluar(texto)]  # lista de resultados para compatibilidad

    print(f"\n🧪 Consulta: {texto}")

    for i, res in enumerate(resultados[:3], start=1):  # top 3
        etiqueta_obtenida = res["etiqueta"]
        porcentaje = res["porcentaje"]
        coincidencias = res["coincidencias"]

        correcto = "✅" if etiqueta_obtenida == esperado else "❌"
        print(f"Top {i}: {correcto} Etiqueta: {etiqueta_obtenida}, Porcentaje: {porcentaje}%")
        for c in coincidencias:
            print(f"   - {c[0]}: {c[1]}")

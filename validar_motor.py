import json
from motor_ia import MotorIA

# Cargar motor
motor = MotorIA()

# Cargar tests
with open("tests_motor.json", "r", encoding="utf-8") as f:
    tests = json.load(f)

# Ejecutar tests
for test in tests:
    texto = test["texto"]
    esperado = test["esperado"]
    resultado = motor.evaluar(texto)[0]  # <-- tomar el primer elemento de la lista
    etiqueta_obtenida = resultado["etiqueta"]
    porcentaje = resultado["porcentaje"]

    correcto = "✅" if etiqueta_obtenida == esperado else "❌"

    print(f"{correcto} Consulta: {texto}")
    print(f"   Esperado: {esperado}")
    print(f"   Obtenido: {etiqueta_obtenida} ({porcentaje}%)")
    print(f"   Coincidencias: {resultado['coincidencias']}\n")

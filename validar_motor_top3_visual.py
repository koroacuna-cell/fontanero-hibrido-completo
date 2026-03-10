import json
from motor_ia import MotorIA

# Colores ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Cargar motor
motor = MotorIA()

# Cargar tests
with open("tests_motor.json", "r", encoding="utf-8") as f:
    tests = json.load(f)

TOP_N = 3  # Número de resultados a mostrar

# Ejecutar tests
for test in tests:
    texto = test["texto"]
    esperado = test["esperado"]
    resultados = motor.evaluar_top_n(texto, top_n=TOP_N)

    # Comprobar si la etiqueta esperada está en Top-N
    top_etiquetas = [r["etiqueta"] for r in resultados]
    correcto = GREEN + "✅" + RESET if esperado in top_etiquetas else RED + "❌" + RESET

    print(f"{correcto} Consulta: {YELLOW}{texto}{RESET}")
    print(f"   Esperado: {esperado}\n")

    for i, res in enumerate(resultados, start=1):
        etiqueta = res["etiqueta"]
        porcentaje = res["porcentaje"]
        coincidencias = res["coincidencias"]
        print(f"   Top {i}: {etiqueta} ({porcentaje}%)")
        for c in coincidencias:
            frase, score = c
            print(f"      - {frase}: {score}")
    print("\n" + "-"*50 + "\n")

import json
from motor_ia import MotorIA

# Configuración
TOP_N = 3
motor = MotorIA()
TESTS_FILE = "tests_motor.json"

# Cargar tests
with open(TESTS_FILE, "r", encoding="utf-8") as f:
    tests = json.load(f)

# Contadores
top1_correct = 0
top2_correct = 0
top3_correct = 0
total = len(tests)

# Evaluación
for test in tests:
    texto = test["texto"]
    esperado = test["esperado"]
    resultados = motor.evaluar_top_n(texto, top_n=TOP_N)

    etiquetas_top = [r["etiqueta"] for r in resultados]

    if esperado == etiquetas_top[0]:
        top1_correct += 1
    if esperado in etiquetas_top[:2]:
        top2_correct += 1
    if esperado in etiquetas_top[:3]:
        top3_correct += 1

# Informe
print("===== Informe de Evaluación Top-N =====")
print(f"Total de consultas: {total}")
print(f"Top 1 correcto: {top1_correct} ({top1_correct/total*100:.2f}%)")
print(f"Top 2 correcto: {top2_correct} ({top2_correct/total*100:.2f}%)")
print(f"Top 3 correcto: {top3_correct} ({top3_correct/total*100:.2f}%)")
print("=======================================")

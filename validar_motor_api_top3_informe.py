import json
import requests

API_URL = "http://127.0.0.1:5005/evaluar"
TESTS_FILE = "tests_motor.json"

def main():
    with open(TESTS_FILE, "r", encoding="utf-8") as f:
        tests = json.load(f)

    total = len(tests)
    aciertos_top1 = 0
    aciertos_top2 = 0
    aciertos_top3 = 0

    print("===== Informe de Evaluación Top-N =====")
    for test in tests:
        texto = test["texto"]
        esperado = test["esperado"]

        resp = requests.post(API_URL, json={"texto": texto})
        resultados = resp.json()

        top_etiquas = [r["etiqueta"] for r in resultados]

        correcto1 = esperado == top_etiquas[0]
        correcto2 = esperado in top_etiquas[:2]
        correcto3 = esperado in top_etiquas[:3]

        aciertos_top1 += correcto1
        aciertos_top2 += correcto2
        aciertos_top3 += correcto3

        print(f"\nConsulta: {texto}")
        print(f"   Esperado: {esperado}")
        for i, r in enumerate(resultados, start=1):
            print(f"   Top {i}: {r['etiqueta']} ({r['porcentaje']}%)")
            for c in r['coincidencias']:
                print(f"      - {c[0]}: {c[1]}")
        print(f"   ✅ Top 1 correcto: {correcto1}")
        print(f"   ✅ Top 2 correcto: {correcto2}")
        print(f"   ✅ Top 3 correcto: {correcto3}")
        print("-" * 50)

    print("\n===== Resumen =====")
    print(f"Total consultas: {total}")
    print(f"Top 1 correcto: {aciertos_top1} ({aciertos_top1/total*100:.2f}%)")
    print(f"Top 2 correcto: {aciertos_top2} ({aciertos_top2/total*100:.2f}%)")
    print(f"Top 3 correcto: {aciertos_top3} ({aciertos_top3/total*100:.2f}%)")
    print("=====================================")

if __name__ == "__main__":
    main()

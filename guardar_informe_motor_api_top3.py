# guardar_informe_motor_api_top3.py

import json
import requests

# Configuración
API_URL = "http://127.0.0.1:5005/evaluar"
INFORME_FILE = "informe_motor_api_top3.txt"

# Consultas de prueba
consultas = [
    {"texto": "mi ducha pierde agua", "esperado": "ducha_pierde_agua"},
    {"texto": "la cisterna está goteando", "esperado": "cisterna_pierde"},
    {"texto": "no enciende la caldera", "esperado": "caldera_no_enciende"},
    {"texto": "la lavadora no arranca", "esperado": "lavadora_no_enciende"},
    {"texto": "hay agua fría en la ducha", "esperado": "ducha_fria"},
    {"texto": "gotea el grifo del baño", "esperado": "grifo_goteando"}
]

informe = []
top1_correcto = 0
top2_correcto = 0
top3_correcto = 0

for c in consultas:
    response = requests.post(API_URL, json={"texto": c["texto"]})
    if response.status_code != 200:
        raise Exception(f"Error al consultar API: {response.status_code}")
    resultados = response.json()

    top1 = resultados[0]["etiqueta"]
    top2 = resultados[1]["etiqueta"]
    top3 = resultados[2]["etiqueta"]

    top1_ok = top1 == c["esperado"]
    top2_ok = top2 == c["esperado"]
    top3_ok = top3 == c["esperado"]

    top1_correcto += top1_ok
    top2_correcto += top2_ok
    top3_correcto += top3_ok

    informe.append({
        "consulta": c["texto"],
        "esperado": c["esperado"],
        "top": [
            {"pos": 1, "etiqueta": top1, "correcto": top1_ok, "coincidencias": resultados[0]["coincidencias"]},
            {"pos": 2, "etiqueta": top2, "correcto": top2_ok, "coincidencias": resultados[1]["coincidencias"]},
            {"pos": 3, "etiqueta": top3, "correcto": top3_ok, "coincidencias": resultados[2]["coincidencias"]},
        ]
    })

# Generar resumen
resumen = (
    f"===== Informe de Evaluación Top-N =====\n"
    f"Total consultas: {len(consultas)}\n"
    f"Top 1 correcto: {top1_correcto} ({top1_correcto/len(consultas)*100:.2f}%)\n"
    f"Top 2 correcto: {top2_correcto} ({top2_correcto/len(consultas)*100:.2f}%)\n"
    f"Top 3 correcto: {top3_correcto} ({top3_correcto/len(consultas)*100:.2f}%)\n"
    f"=====================================\n"
)

# Guardar informe en archivo
with open(INFORME_FILE, "w", encoding="utf-8") as f:
    f.write(resumen)
    for item in informe:
        f.write(f"\nConsulta: {item['consulta']}\n")
        f.write(f"   Esperado: {item['esperado']}\n")
        for t in item["top"]:
            f.write(f"   Top {t['pos']}: {t['etiqueta']} | Correcto: {t['correcto']}\n")
            for frase, score in t["coincidencias"]:
                f.write(f"      - {frase}: {score}\n")
        f.write("--------------------------------------------------\n")

# También imprimir resumen en pantalla
print(resumen)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from inteligencia_local import buscar_respuesta

# Carga los archivos maestro
with open("maestro_local.json", "r", encoding="utf-8") as f:
    maestro_local = json.load(f)

with open("maestro.json", "r", encoding="utf-8") as f:
    maestro_global = json.load(f)

print("=== EJECUTANDO PRUEBAS INDIVIDUALES ===")

while True:
    problema = input("💬 Describe tu problema (o 'salir' para terminar): ").strip()
    if problema.lower() == "salir" or problema == "":
        break

    try:
        # Ignoramos valores extra que pueda devolver la función
        etiqueta, respuestas, *_ = buscar_respuesta(problema, maestro_global, maestro_local)
    except Exception as e:
        print(f"❌ No se pudo procesar el problema: {e}")
        continue

    if respuestas:
        print(f"\n🔧 Resultado para: {etiqueta}")
        for r in respuestas:
            print(f"- {r}")
    else:
        print("❌ No he encontrado una solución para eso. Envía foto por WhatsApp 📸 y te ayudaré.")

    print("-" * 50)

print("=== FIN DE PRUEBAS INDIVIDUALES ===")

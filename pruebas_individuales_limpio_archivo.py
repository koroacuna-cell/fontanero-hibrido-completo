#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from inteligencia_local import buscar_respuesta
import json
import sys

# Carga los archivos maestro
with open("maestro_local.json", "r", encoding="utf-8") as f:
    maestro_local = json.load(f)

with open("maestro.json", "r", encoding="utf-8") as f:
    maestro_global = json.load(f)

print("=== EJECUTANDO PRUEBAS DESDE ARCHIVO ===")

# Leer problemas desde archivo si se pasa como argumento
if len(sys.argv) > 1:
    problemas_archivo = sys.argv[1]
    with open(problemas_archivo, "r", encoding="utf-8") as f:
        problemas = [line.strip() for line in f if line.strip()]
else:
    # Entrada interactiva
    problemas = []
    while True:
        problema = input("💬 Describe tu problema (o 'salir' para terminar): ").strip()
        if problema.lower() == "salir" or problema == "":
            break
        problemas.append(problema)

# Procesar problemas
for problema in problemas:
    etiqueta, respuestas, *_ = buscar_respuesta(problema, maestro_global, maestro_local)
    if respuestas:
        print(f"\n🔧 Resultado para: {etiqueta}")
        for r in respuestas:
            print(f"- {r}")
    else:
        print(f"\n❌ No he encontrado una solución para: {problema}. Envía foto por WhatsApp 📸 y te ayudaré.")
    print("-" * 50)

print("=== FIN DE PRUEBAS DESDE ARCHIVO ===")

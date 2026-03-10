#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from inteligencia_local import buscar_respuesta
from sinonimos_problemas import SINONIMOS_PROBLEMAS

# Carga los archivos maestro
with open("maestro_local.json", "r", encoding="utf-8") as f:
    maestro_local = json.load(f)

with open("maestro.json", "r", encoding="utf-8") as f:
    maestro_global = json.load(f)

print("=== EJECUTANDO PRUEBAS INDIVIDUALES LIMPIO ===")

# Si se pasa un archivo por argumento, leer problemas desde ahí
if len(sys.argv) > 1:
    archivo_problemas = sys.argv[1]
    with open(archivo_problemas, "r", encoding="utf-8") as f:
        problemas = [line.strip() for line in f if line.strip()]
else:
    problemas = []

# Función para procesar un problema
def procesar_problema(problema):
    problema_normalizado = SINONIMOS_PROBLEMAS.get(problema.lower(), problema.lower())
    try:
        etiqueta, respuestas, *_ = buscar_respuesta(problema_normalizado, maestro_global, maestro_local)
    except ValueError:
        print(f"❌ No se pudo procesar el problema: {problema}")
        return

    if respuestas:
        print(f"\n🔧 Resultado para: {etiqueta}")
        for r in respuestas:
            print(f"- {r}")
    else:
        print("❌ No he encontrado una solución para eso. Envía foto por WhatsApp 📸 y te ayudaré.")
    print("-" * 50)

# Procesar problemas del archivo
for problema in problemas:
    procesar_problema(problema)

# Interactivo si no se pasó archivo o quedan problemas por leer
while True:
    problema = input("💬 Describe tu problema (o 'salir' para terminar): ").strip()
    if problema.lower() == "salir" or problema == "":
        break
    procesar_problema(problema)

print("=== FIN DE PRUEBAS INDIVIDUALES LIMPIO ===")

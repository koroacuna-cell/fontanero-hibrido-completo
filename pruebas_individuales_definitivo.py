#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# Función de búsqueda con soporte de sinónimos
def buscar_respuesta(problema, maestro_global, maestro_local, sinonimos=None):
    if sinonimos and problema in sinonimos:
        problema = sinonimos[problema]

    # Buscar en maestro_local
    for item in maestro_local:
        if problema.lower() == item["etiqueta"].lower():
            return item["etiqueta"], item["respuesta"]

    # Buscar en maestro_global
    for item in maestro_global:
        if problema.lower() == item["etiqueta"].lower():
            return item["etiqueta"], item["respuesta"]

    return None, []

# Carga maestros
with open("maestro_local.json", "r", encoding="utf-8") as f:
    maestro_local = json.load(f)

with open("maestro.json", "r", encoding="utf-8") as f:
    maestro_global = json.load(f)

# Diccionario de sinónimos
SINONIMOS = {
    "grifo de lavabo gotea": "grifo_goteando",
    "ducha fría": "ducha_fria",
    "tubería rota": "tuberia_rota",
    "cisterna pierde agua": "cisterna_pierde"
}

# Función principal
def ejecutar_problemas(lista_problemas):
    procesados = set()
    for problema in lista_problemas:
        problema = problema.strip()
        if not problema or problema.lower() == "salir":
            continue
        etiqueta, respuestas = buscar_respuesta(problema, maestro_global, maestro_local, SINONIMOS)
        if etiqueta and etiqueta not in procesados:
            print(f"\n🔧 Resultado para: {etiqueta}")
            for r in respuestas:
                print(f"- {r}")
            print("-" * 50)
            procesados.add(etiqueta)
        elif etiqueta is None:
            print(f"\n❌ No he encontrado una solución para: {problema}. Envía foto por WhatsApp 📸 y te ayudaré.")
            print("-" * 50)

# Entrada interactiva o desde archivo
import sys
if len(sys.argv) > 1:
    # Leer problemas desde archivo
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        lista = f.readlines()
    print("=== EJECUTANDO PRUEBAS DESDE ARCHIVO ===")
    ejecutar_problemas(lista)
    print("=== FIN DE PRUEBAS DESDE ARCHIVO ===")
else:
    # Entrada interactiva
    print("=== EJECUTANDO PRUEBAS INDIVIDUALES DEFINITIVO ===")
    while True:
        try:
            problema = input("💬 Describe tu problema (o 'salir' para terminar): ")
        except EOFError:
            break
        if problema.lower() == "salir" or problema.strip() == "":
            break
        ejecutar_problemas([problema])
    print("=== FIN DE PRUEBAS INDIVIDUALES DEFINITIVO ===")

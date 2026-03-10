#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def cargar_maestro(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def encontrar_etiqueta(problema, maestro):
    problema_lower = problema.lower()
    for entry in maestro:
        etiqueta = entry.get("etiqueta")
        sinonimos = entry.get("sinonimos", [])
        # Comparamos con etiqueta y todos los sinónimos
        if problema_lower == etiqueta.lower() or problema_lower in [s.lower() for s in sinonimos]:
            return etiqueta, entry.get("respuesta", [])
    return None, []

def ejecutar_pruebas_desde_archivo(nombre_archivo_problemas, maestro_global, maestro_local):
    print("=== EJECUTANDO PRUEBAS INDIVIDUALES SYNONYMOUS ===")
    with open(nombre_archivo_problemas, "r", encoding="utf-8") as f:
        for linea in f:
            problema = linea.strip()
            if not problema:
                continue
            # Primero buscamos en maestro_local
            etiqueta, respuestas = encontrar_etiqueta(problema, maestro_local)
            # Si no está, buscamos en maestro_global
            if not etiqueta:
                etiqueta, respuestas = encontrar_etiqueta(problema, maestro_global)

            if respuestas:
                print(f"\n🔧 Resultado para: {etiqueta}")
                for r in respuestas:
                    print(f"- {r}")
            else:
                print(f"\n❌ No he encontrado una solución para: {problema}. Envía foto por WhatsApp 📸 y te ayudaré.")
            print("-" * 50)
    print("=== FIN DE PRUEBAS INDIVIDUALES SYNONYMOUS ===")

if __name__ == "__main__":
    maestro_local = cargar_maestro("maestro_local.json")
    maestro_global = cargar_maestro("maestro.json")
    nombre_archivo_problemas = "problemas.txt"  # Cambia si quieres otro archivo
    ejecutar_pruebas_desde_archivo(nombre_archivo_problemas, maestro_global, maestro_local)

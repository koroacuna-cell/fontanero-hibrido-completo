#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def cargar_archivo(ruta):
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_archivo(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def buscar_respuesta(texto, maestro_global, maestro_local):
    texto = texto.lower()

    for entrada in maestro_local:
        if entrada.get("etiqueta") == texto.replace(" ", "_"):
            return entrada

    for entrada in maestro_global:
        if entrada.get("etiqueta") == texto.replace(" ", "_"):
            return entrada

    for entrada in maestro_local:
        if any(pal in texto for pal in entrada.get("palabras", [])):
            return entrada

    for entrada in maestro_global:
        if any(pal in texto for pal in entrada.get("palabras", [])):
            return entrada

    return None

def main():
    print("=== FONTANERO VIRTUAL HÍBRIDO — V6 ===")
    print("Escribe 'salir' para terminar.\n")

    maestro_global = cargar_archivo("maestro.json")
    maestro_local = cargar_archivo("maestro_local.json")

    print(f"[OK] Cargado: maestro.json ({len(maestro_global)} entradas)")
    print(f"[OK] Cargado: maestro_local.json ({len(maestro_local)} entradas)")

    while True:
        try:
            descripcion = input("Describe tu problema: ").strip().lower()
        except EOFError:
            print("\n👋 Cerrando por EOF (CTRL+D).")
            break

        if descripcion in ["salir", "exit", "quit"]:
            print("👋 Saliendo del Fontanero Virtual...")
            break

        resultado = buscar_respuesta(descripcion, maestro_global, maestro_local)

        if resultado:
            print(f"\n🔧 Resultado para: **{resultado['etiqueta']}**\n")
            print(resultado["respuesta"])
            print("---------------------------")
            continue

        # Si no hay coincidencia, se añade automáticamente
        nueva_entrada = {
            "etiqueta": descripcion.replace(" ", "_"),
            "palabras": descripcion.split(),
            "respuesta": "Pendiente de definir respuesta"
        }
        maestro_local.append(nueva_entrada)
        guardar_archivo("maestro_local.json", maestro_local)

        print(f"✅ Entrada agregada automáticamente al conocimiento local: {nueva_entrada['etiqueta']}\n")

if __name__ == "__main__":
    main()

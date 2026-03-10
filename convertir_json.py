#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import shutil

archivos = ["maestro.json", "maestro_local.json"]

for ruta in archivos:
    # Hacemos copia de seguridad
    shutil.copyfile(ruta, ruta + ".bak")
    print(f"✅ Copia de seguridad creada: {ruta}.bak")

    # Cargamos el JSON original
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Si es dict, lo convertimos a lista
    if isinstance(data, dict):
        data = list(data.values())

    nueva_data = []
    for entrada in data:
        # Detectamos estructura actual
        alias = entrada.get("alias", [])
        pasos = entrada.get("pasos", [])
        if not alias:
            continue  # Si no hay alias, ignoramos
        nueva_entrada = {
            "etiqueta": alias[0].replace(" ", "_"),
            "palabras": alias,
            "respuesta": pasos
        }
        nueva_data.append(nueva_entrada)

    # Guardamos el archivo transformado
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(nueva_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Archivo {ruta} transformado y listo para Fontanero V6, entradas: {len(nueva_data)}")

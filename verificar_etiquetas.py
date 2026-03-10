#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def cargar_maestro(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def listar_etiquetas(maestro, nombre):
    print(f"=== Etiquetas en {nombre} ===")
    for entry in maestro:
        etiqueta = entry.get("etiqueta", "SIN_ETIQUETA")
        print(f"- {etiqueta}")
        sinonimos = entry.get("sinonimos", [])
        if sinonimos:
            print(f"  sinónimos: {', '.join(sinonimos)}")
    print("-" * 50)

if __name__ == "__main__":
    maestro_local = cargar_maestro("maestro_local.json")
    maestro_global = cargar_maestro("maestro.json")

    listar_etiquetas(maestro_local, "maestro_local.json")
    listar_etiquetas(maestro_global, "maestro.json")

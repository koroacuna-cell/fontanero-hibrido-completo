#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def cargar_maestro(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def listar_etiquetas(maestro):
    print(f"=== Etiquetas en maestro_test.json ===")
    for entry in maestro:
        etiqueta = entry.get("etiqueta", "SIN_ETIQUETA")
        print(f"- {etiqueta}")
        sinonimos = entry.get("sinonimos", [])
        if sinonimos:
            print(f"  sinónimos: {', '.join(sinonimos)}")
    print("-" * 50)

if __name__ == "__main__":
    maestro = cargar_maestro("maestro_test.json")
    listar_etiquetas(maestro)

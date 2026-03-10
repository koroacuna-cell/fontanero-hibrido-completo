#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# Carga de datos de ejemplo (puedes comentarlo si se cargan desde fuera)
# with open("maestro_local.json", "r", encoding="utf-8") as f:
#     maestro_local = json.load(f)
# with open("maestro.json", "r", encoding="utf-8") as f:
#     maestro_global = json.load(f)

def buscar_respuesta(problema, maestro_global, maestro_local):
    """
    Busca la etiqueta y respuestas para un problema dado en los archivos maestro.
    Devuelve: etiqueta, lista de respuestas
    """
    problema_lower = problema.lower().strip()

    # Primero buscamos en maestro_local
    for contenido in maestro_local:  # ✅ iteramos sobre la lista
        etiqueta = contenido.get("etiqueta")
        respuestas = contenido.get("respuesta", [])
        palabras = contenido.get("palabras", [])
        for palabra in palabras:
            if palabra.lower() in problema_lower:
                return etiqueta, respuestas

    # Luego buscamos en maestro_global
    for contenido in maestro_global:  # ✅ iteramos sobre la lista
        etiqueta = contenido.get("etiqueta")
        respuestas = contenido.get("respuesta", [])
        palabras = contenido.get("palabras", [])
        for palabra in palabras:
            if palabra.lower() in problema_lower:
                return etiqueta, respuestas

    # Si no se encuentra nada
    return None, []

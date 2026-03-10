# Contenido completo de tu script json.diff.lit convertido a Python si hace falta
# por ejemplo funciones para comparar JSON, detectar cambios, etc.

import json

def cargar_json(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def comparar_json(json1, json2):
    """Devuelve diferencias entre dos diccionarios JSON"""
    diffs = {}
    for k in json1:
        if k not in json2:
            diffs[k] = {"status": "faltante en json2", "valor_json1": json1[k]}
        elif json1[k] != json2[k]:
            diffs[k] = {"status": "diferente", "valor_json1": json1[k], "valor_json2": json2[k]}
    for k in json2:
        if k not in json1:
            diffs[k] = {"status": "faltante en json1", "valor_json2": json2[k]}
    return diffs


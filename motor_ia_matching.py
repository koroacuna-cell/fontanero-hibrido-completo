#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
motor_ia_matching.py
Motor de matching progresivo (exacto -> fuzzy -> token-overlap)
Usar: python3 motor_ia_matching.py problemas.txt
o ejecutar sin argumentos para modo interactivo.
"""

import json
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

# --- Utilities ---
def norm(text: str) -> str:
    """Normaliza: minusculas, trim, elimina acentos"""
    if not isinstance(text, str):
        return ""
    t = text.strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return t

def jaccard(a_tokens, b_tokens):
    if not a_tokens or not b_tokens:
        return 0.0
    A = set(a_tokens)
    B = set(b_tokens)
    inter = A.intersection(B)
    union = A.union(B)
    return len(inter) / len(union)

def fuzzy_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

# --- Carga maestro ---
MAESTRO_FILE = "maestro_local_limpio.json"

def cargar_maestro(path=MAESTRO_FILE):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe el maestro: {path}")
    with p.open(encoding="utf-8") as f:
        return json.load(f)

# --- Preparar índice (mapa de sinónimos + etiquetas) ---
def construir_indice(maestro):
    """
    Devuelve lista de entries con campos:
    - etiqueta
    - sinonimos (lista)
    - respuesta (lista)
    - norm_keys: lista de claves normalizadas (etiqueta + sinonimos)
    """
    indice = []
    for entry in maestro:
        etiqueta = entry.get("etiqueta", "")
        sinonimos = entry.get("sinonimos", []) or []
        respuestas = entry.get("respuesta", []) or []
        claves = [etiqueta] + list(sinonimos)
        norm_keys = [norm(k) for k in claves if k]
        indice.append({
            "etiqueta": etiqueta,
            "sinonimos": sinonimos,
            "respuesta": respuestas,
            "norm_keys": norm_keys
        })
    return indice

# --- Lógica de matching ---
def match_problema(texto, indice,
                   fuzzy_threshold=0.82,
                   jaccard_threshold=0.40):

    t_norm = norm(texto)
    t_tokens = [tok for tok in t_norm.split() if tok]

    candidatos = []

    for entry in indice:
        best_score = 0.0
        best_reason = None

        for clave in entry["norm_keys"]:
            # evitar que una palabra corta (<=5 letras) contamine
            if len(clave) <= 5:
                continue

            # coincidencia exacta o frase clave muy cercana
            if clave == t_norm:
                best_score = 1.0
                best_reason = f"exact '{clave}'"
                break

            # fuzzy matching fuerte
            r = fuzzy_ratio(clave, t_norm)
            if r >= fuzzy_threshold and r > best_score:
                best_score = r
                best_reason = f"fuzzy {r:.2f} '{clave}'"

            # similitud por tokens
            j = jaccard(clave.split(), t_tokens)
            if j >= jaccard_threshold and j > best_score:
                best_score = j
                best_reason = f"jaccard {j:.2f} '{clave}'"

        if best_score >= fuzzy_threshold or best_score >= 0.99:
            candidatos.append((best_score, best_reason, entry))

    candidatos.sort(key=lambda x: x[0], reverse=True)

    etiquetas_vistas = set()
    resultados = []
    for score, reason, entry in candidatos:
        if entry["etiqueta"] not in etiquetas_vistas:
            etiquetas_vistas.add(entry["etiqueta"])
            resultados.append({"score": score, "reason": reason, "entry": entry})

    return resultadosdef ejecutar_problemas(archivo_problemas=None):
    maestro = cargar_maestro()
    indice = construir_indice(maestro)

    if archivo_problemas:
        p = Path(archivo_problemas)
        if not p.exists():
            print(f"No existe el archivo de problemas: {archivo_problemas}")
            return
        with p.open(encoding="utf-8") as f:
            problemas = [line.strip() for line in f if line.strip()]
    else:
        # modo interactivo
        print("🤖 Modo interactivo. Escribe tu problema y pulsa Enter (vacío para salir).")
        problemas = []
        while True:
            try:
                s = input("💬 Describe tu problema: ").strip()
            except EOFError:
                break
            if not s:
                break
            problemas.append(s)

    resumen = {entry.get("etiqueta", ""): [] for entry in maestro}

    print("\n=== EJECUCIÓN ===\n")
    for p in problemas:
        resultados = match_problema(p, indice)
        if not resultados:
            print(f"❌ No he encontrado una solución para: {p}")
            print("-" * 50)
            continue

        # imprimir los mejores (hasta 3)
        for r in resultados[:3]:
            score = r["score"]
            reason = r["reason"]
            entry = r["entry"]
            etiqueta = entry["etiqueta"]
            print(f"🔧 Resultado para: {etiqueta}  (score={score:.2f})  — {reason}")
            for resp in entry.get("respuesta", []):
                print(f"- {resp}")
            print("-" * 50)
            # añadir al resumen (guardamos el texto original que coincidió)
            resumen[etiqueta].append(p)

    # imprimir resumen
    print("\n=== RESUMEN DE COINCIDENCIAS POR ETIQUETA ===\n")
    for etiqueta, lista in resumen.items():
        print(f"🔧 {etiqueta}")
        for item in lista:
            print(f" - {item}")
        print("-" * 50)

    # guardar resumen en archivo
    out = "resumen_motor_ia.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("=== RESUMEN DE COINCIDENCIAS POR ETIQUETA ===\n\n")
        for etiqueta, lista in resumen.items():
            f.write(f"🔧 {etiqueta}\n")
            for item in lista:
                f.write(f" - {item}\n")
            f.write("-" * 50 + "\n")
    print(f"\n✅ Resumen guardado en '{out}'")

# --- CLI ---
if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else None
    ejecutar_problemas(archivo)

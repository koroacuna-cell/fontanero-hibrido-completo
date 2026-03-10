#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fontanero Virtual — Híbrido PRO+LOCAL (v4)
Cargar maestro_local.json (rápido) y maestro.json (completo).
Búsqueda por claves y aliases (difflib) y respuesta interactiva en consola.
Diseñado para Termux / móvil (sin dependencias externas).
"""

import json
import difflib
import os
import sys
from datetime import datetime

# Config
LOCAL_FILE = "maestro_local.json"   # archivo ligero, respuestas rápidas
MASTER_FILE = "maestro.json"        # archivo maestro grande
MATCH_CUTOFF = 0.55                 # similitud mínima para difflib
MAX_SUGGESTIONS = 5                 # nº máximas sugerencias mostradas

def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}")

def cargar_json(path):
    """Cargar JSON desde path, devuelve diccionario o {} si falla."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log(f"✅ Cargado: {path} ({len(data)} entradas)")
        return data
    except FileNotFoundError:
        log(f"⚠️  No encontrado: {path}")
        return {}
    except json.JSONDecodeError as e:
        log(f"❌ Error JSON en {path}: {e}")
        return {}
    except Exception as e:
        log(f"❌ Error al cargar {path}: {e}")
        return {}

def construir_indice(*dicts):
    """
    Construye índice unificado: { alias_or_key_lower: canonical_key }
    Recibe uno o varios diccionarios de datos (local primero por prioridad en orden).
    """
    indice = {}
    canonical_source = {}  # para saber de qué fichero proviene (info opcional)
    for source_idx, data in enumerate(dicts):
        for clave, contenido in (data or {}).items():
            if not isinstance(clave, str):
                continue
            can = clave.strip()
            if not can:
                continue
            # si clave ya existe no la sobreescribimos (prioridad del primer dict pasado)
            low_can = can.lower()
            if low_can not in indice:
                indice[low_can] = can
                canonical_source[low_can] = source_idx
            # aliases
            aliases = contenido.get("alias") or contenido.get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            for a in aliases:
                if not isinstance(a, str):
                    continue
                la = a.strip().lower()
                if la and la not in indice:
                    indice[la] = can
                    canonical_source[la] = source_idx
    return indice, canonical_source

def buscar_coincidencia(texto, indice_keys, cutoff=MATCH_CUTOFF):
    """Devuelve la mejor clave canon (None si no hay coincidencia)."""
    texto = texto.strip().lower()
    if not texto:
        return None
    # Búsqueda directa exacta
    if texto in indice_keys:
        return indice_keys[texto]
    # Búsqueda por get_close_matches
    posibles = list(indice_keys.keys())
    matches = difflib.get_close_matches(texto, posibles, n=1, cutoff=cutoff)
    if matches:
        return indice_keys[matches[0]]
    return None

def sugerir_alternativas(texto, indice_keys, n=MAX_SUGGESTIONS):
    texto = texto.strip().lower()
    if not texto:
        return []
    posibles = list(indice_keys.keys())
    similars = difflib.get_close_matches(texto, posibles, n=n, cutoff=0.4)
    # devolver las claves canon (sin duplicados) respetando el orden
    seen = set()
    resultado = []
    for s in similars:
        canon = indice_keys.get(s)
        if canon and canon not in seen:
            resultado.append(canon)
            seen.add(canon)
    return resultado

def mostrar_pasos(entrada_key, data_local, data_master):
    """Muestra pasos. da prioridad a local si existe la clave en local."""
    # preferencia: local -> master
    if entrada_key in data_local:
        pasos = data_local[entrada_key].get("pasos") or data_local[entrada_key].get("steps") or []
    elif entrada_key in data_master:
        pasos = data_master[entrada_key].get("pasos") or data_master[entrada_key].get("steps") or []
    else:
        pasos = []
    if not pasos:
        print("\n🔧 Resultado encontrado pero no hay 'pasos' definidos.\n")
        return
    print(f"\n🔧 Resultado para: **{entrada_key}**\n")
    for i, p in enumerate(pasos, 1):
        print(f"{i}. {p}")
    print("---------------------------\n")

def main_loop(data_local, data_master, indice, source_map):
    print("=== FONTANERO VIRTUAL HÍBRIDO — V4 ===")
    print("Escribe 'salir' para terminar.\n")
    while True:
        try:
            texto = input("Describe tu problema: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSalida. ¡Hasta luego!")
            break
        if not texto:
            continue
        if texto.lower() in ("salir", "exit", "quit"):
            print("Cerrando. ¡Hasta luego!")
            break

        # 1) buscar en índice (local tiene prioridad por cómo se construyó)
        clave_canon = buscar_coincidencia(texto, indice)

        if clave_canon:
            # decidir si la clave está en local o en master (preferir local si existe)
            if clave_canon in data_local:
                mostrar_pasos(clave_canon, data_local, data_master)
            elif clave_canon in data_master:
                mostrar_pasos(clave_canon, data_local, data_master)
            else:
                # aunque improbable, si la clave no está en ninguno, sugerimos alternativas
                print("❌ Error interno: clave detectada no encontrada en datos.")
        else:
            # No coincidencia; probar búsqueda en texto por palabras (token search simple)
            words = [w.lower() for w in texto.split() if len(w) > 2]
            found = None
            for w in words:
                c = buscar_coincidencia(w, indice, cutoff=0.75)
                if c:
                    found = c
                    break
            if found:
                print(f"🔎 He detectado posible término relacionado: {found}")
                mostrar_pasos(found, data_local, data_master)
                continue

            # sugerir alternativas
            suger = sugerir_alternativas(texto, indice, n=MAX_SUGGESTIONS)
            if suger:
                print("❌ No encontré coincidencia exacta. ¿Quizás quisiste decir alguna de estas?")
                for s in suger:
                    print(f" - {s}")
                print("Prueba con uno de estos términos o envía una foto por WhatsApp 📸 para valoración.")
            else:
                print("❌ No encontré coincidencias. Intenta describirlo de otra forma o envía una foto por WhatsApp 📸.")
        # loop continúa

def ensure_files_present():
    """Comprobaciones básicas y mensajes al usuario sobre los archivos."""
    missing = []
    if not os.path.exists(LOCAL_FILE):
        missing.append(LOCAL_FILE)
    if not os.path.exists(MASTER_FILE):
        missing.append(MASTER_FILE)
    if missing:
        print("⚠️ Aviso: faltan algunos archivos necesarios para respuesta completa:")
        for m in missing:
            print(f" - {m}")
        print("El sistema seguirá intentando con los archivos disponibles.\n")

if __name__ == "__main__":
    ensure_files_present()
    data_local = cargar_json(LOCAL_FILE)
    data_master = cargar_json(MASTER_FILE)

    # construir índice con prioridad local primero
    indice_map, source_map = construir_indice(data_local, data_master)
    # indice_map: { alias_lower: canonical_key }
    # Para buscar por clave directa: podemos mapear canonical_lower -> canonical_key
    # ya está bien así.

    if not indice_map:
        print("❌ Índice vacío. Asegúrate de que maestro_local.json o maestro.json contengan datos válidos.")
        sys.exit(1)

    try:
        main_loop(data_local, data_master, indice_map, source_map)
    except Exception as e:
        log(f"❌ Error inesperado en ejecución: {e}")
        raise

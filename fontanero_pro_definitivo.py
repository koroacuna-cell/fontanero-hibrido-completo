#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fontanero Virtual PRO DEFINITIVO — Eduardo Quiroz, Torrevieja
✅ Semántica con difflib | ✅ 130 respuestas | ✅ Presupuestos estimativos
✅ Aliases flexibles | ✅ Irrompible | ✅ WhatsApp integrado
"""

import json
import difflib
import os
import sys
from datetime import datetime

# Importar módulo de presupuestos
try:
    from presupuestos import generar_respuesta_con_presupuesto, calcular_presupuesto
except ImportError:
    # Fallback si no está disponible
    def generar_respuesta_con_presupuesto(problema, pasos, **kwargs):
        return " | ".join(pasos) + " | 💰 Presupuesto: envía foto por WhatsApp 📸"

# Config
LOCAL_FILE = "maestro_local.json"
MASTER_FILE = "maestro.json"
MATCH_CUTOFF = 0.55
MAX_SUGGESTIONS = 5
WHATSAPP_NUM = "34603398960"

def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}")

def cargar_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log(f"✅ Cargado: {path} ({len(data)} entradas)")
        return data
    except Exception as e:
        log(f"⚠️ Error cargando {path}: {e}")
        return {}

def construir_indice(*dicts):
    indice = {}
    for data in dicts:
        for clave, contenido in (data or {}).items():
            if not isinstance(clave, str):
                continue
            can = clave.strip()
            if not can:
                continue
            low_can = can.lower()
            if low_can not in indice:
                indice[low_can] = can
            aliases = contenido.get("alias") or contenido.get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            for a in aliases:
                if isinstance(a, str):
                    la = a.strip().lower()
                    if la and la not in indice:
                        indice[la] = can
    return indice

def buscar_coincidencia(texto, indice_keys, cutoff=MATCH_CUTOFF):
    """Búsqueda mejorada: extrae palabras clave y busca por contención."""
    texto_original = texto.strip().lower()
    if not texto_original:
        return None
    
    # 1. Búsqueda exacta directa
    if texto_original in indice_keys:
        return indice_keys[texto_original]
    
    # 2. Extraer palabras clave (quitar stopwords)
    stopwords = {'el', 'la', 'los', 'las', 'un', 'una', 'me', 'mi', 'se', 'de', 'del', 'al', 'y', 'o', 'para', 'por', 'con', 'sin', 'en', 'es', 'está', 'esta', 'que', 'lo', 'la', 'le', 'les', 'nos', 'os', 'urgente', 'urgencia', 'ahora', 'ya', 'necesito', 'quiero', 'tengo', 'hay'}
    palabras = [p for p in texto_original.split() if p not in stopwords and len(p) > 2]
    
    # 3. Buscar por contención de palabras clave
    for clave_canon, clave_norm in indice_keys.items():
        # Verificar si las palabras clave del usuario están en la clave del JSON
        clave_palabras = set(clave_norm.lower().replace('_', ' ').split())
        if all(p in clave_palabras or any(p in cp for cp in clave_palabras) for p in palabras[:2]):
            return clave_canon
    
    # 4. Búsqueda difusa con difflib (fallback)
    posibles = list(indice_keys.keys())
    matches = difflib.get_close_matches(texto_original, posibles, n=3, cutoff=cutoff)
    
    # También probar con las palabras clave solas
    if palabras:
        keyword = '_'.join(palabras[:3])  # Primeras 3 palabras como clave
        matches_kw = difflib.get_close_matches(keyword, posibles, n=3, cutoff=cutoff-0.1)
        matches = matches + matches_kw
    
    if matches:
        return indice_keys[matches[0]]
    
    return None
    if texto in indice_keys:
        return indice_keys[texto]
    posibles = list(indice_keys.keys())
    matches = difflib.get_close_matches(texto, posibles, n=1, cutoff=cutoff)
    if matches:
        return indice_keys[matches[0]]
    return None

def detectar_urgencia(texto):
    texto = texto.lower()
    return any(p in texto for p in ['urgente', 'ya', 'ahora', 'emergencia', 'inmediato'])

def detectar_fin_de_semana():
    from datetime import datetime
    return datetime.now().weekday() >= 5  # Sábado=5, Domingo=6

def responder(pregunta, maestro, indice):
    pregunta_limpia = pregunta.strip().lower()
    
    # Buscar coincidencia
    clave_encontrada = buscar_coincidencia(pregunta_limpia, indice)
    
    if clave_encontrada and clave_encontrada in maestro:
        valor = maestro[clave_encontrada]
        pasos = valor.get('pasos') or valor.get('steps') or []
        
        # Detectar contexto
        urgencia = detectar_urgencia(pregunta)
        finde = detectar_fin_de_semana()
        
        # Generar respuesta con presupuesto
        respuesta = generar_respuesta_con_presupuesto(
            clave_encontrada, pasos, urgencia=urgencia, finde=finde
        )
        
        return respuesta, clave_encontrada
    
    return None, None

def main():
    log("🚀 Fontanero Virtual PRO DEFINITIVO - Iniciando...")
    
    # Cargar datos
    local_data = cargar_json(LOCAL_FILE)
    master_data = cargar_json(MASTER_FILE)
    
    # Construir índice
    indice = construir_indice(local_data, master_data)
    maestro = {**master_data, **local_data}  # Prioridad local
    
    print("\n" + "=" * 60)
    print("🔧 FONTANERO EDUARDO QUIROZ - TORREVIEJA")
    print("💬 Chatbot PRO con presupuestos estimativos")
    print("📱 WhatsApp: +34 603 39 89 60")
    print("=" * 60)
    print("Escribe tu problema o 'salir' para terminar.\n")
    
    while True:
        try:
            pregunta = input("👤 Tú: ").strip()
            if pregunta.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta pronto! Envía foto por WhatsApp si necesitas ayuda 📸")
                break
            
            if not pregunta:
                continue
            
            respuesta, clave = responder(pregunta, maestro, indice)
            
            if respuesta:
                print(f"🔧 Fontanero: {respuesta}\n")
            else:
                print(f"🔧 Fontanero: Lo siento, no entiendo la pregunta con precisión.")
                print(f"💡 Prueba con: 'grifo gotea', 'cisterna pierde', 'termo no calienta'...")
                print(f"📸 O envíame una foto por WhatsApp: https://wa.me/{WHATSAPP_NUM}\n")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta pronto!")
            break
        except Exception as e:
            log(f"❌ Error: {e}")
            print("⚠️ Algo salió mal. Intenta de nuevo o contacta por WhatsApp 📸\n")

if __name__ == "__main__":
    main()

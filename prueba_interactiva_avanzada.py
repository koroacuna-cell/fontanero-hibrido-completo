#!/usr/bin/env python3
import json
from difflib import SequenceMatcher

# ================================
#   CONFIGURACIÓN DEL SISTEMA
# ================================

ARCHIVO_BD = "bd_problemas.json"

UMBRAL_MINIMO = 0.60        # Si ninguna coincidencia supera este valor, se responderá "No entiendo"
UMBRAL_ADVERTENCIA = 0.75   # Si está entre mínimo y este valor, se marca con ⚠️
UMBRAL_VERDE = 0.90         # Coincidencias muy altas → ✔️

# ================================
#   FUNCIONES PRINCIPALES
# ================================

def cargar_base_problemas():
    """Carga la base de datos desde JSON."""
    try:
        with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: No se encontró bd_problemas.json")
        return {}

def calcular_similitud(a, b):
    """Calcula similitud entre cadenas."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def obtener_mejores_coincidencias(texto_usuario, base_problemas):
    """Devuelve el TOP 3 de mejores coincidencias."""
    puntuaciones = []

    for clave, datos in base_problemas.items():
        similitud = calcular_similitud(texto_usuario, clave)
        puntuaciones.append((clave, similitud, datos))

    puntuaciones.sort(key=lambda x: x[1], reverse=True)
    return puntuaciones[:3]

def mostrar_top_coincidencias(top):
    """Muestra coincidencias con iconos según la similitud."""
    print("\n=== TOP 3 coincidencias ===")

    for clave, similitud, _ in top:
        if similitud >= UMBRAL_VERDE:
            icono = "✔️"
        elif similitud >= UMBRAL_ADVERTENCIA:
            icono = "⚠️"
        else:
            icono = "❌"

        print(f"{icono} {clave} — similitud: {similitud:.3f}")

def responder(top):
    """Genera la respuesta final según la similitud encontrada."""
    if not top or not top[0]:
        print("\n=== RESPUESTA FINAL ===")
        print("❓ No entiendo bien el problema.")
        print("Por favor, escribe una descripción más clara o diferente.\n")
        print("------------------------------")
        return

    clave, similitud, datos = top[0]

    if similitud < UMBRAL_MINIMO:
        print("\n=== RESPUESTA FINAL ===")
        print("❓ No entiendo bien el problema.")
        print("Por favor, escribe una descripción más clara o diferente.\n")
        print("------------------------------")
        return

    print("\n=== RESPUESTA FINAL ===")
    respuestas = datos.get("respuesta")
    if isinstance(respuestas, list):
        for paso in respuestas:
            print("✔️ " + paso)
    elif isinstance(respuestas, str):
        print("✔️ " + respuestas)
    else:
        print("❓ No hay respuesta disponible para este problema.")
    print("------------------------------")

# ================================
#       PROGRAMA PRINCIPAL
# ================================

def main():
    base_problemas = cargar_base_problemas()
    if not base_problemas:
        return

    print("=== PRUEBA INTERACTIVA AVANZADA ===")

    while True:
        texto = input("\n💬 Describe tu problema (o 'salir'): ").strip()

        if texto.lower() == "salir":
            print("👋 Saliendo...")
            break

        if texto == "":
            print("⚠️ Escribe algo.")
            continue

        top = obtener_mejores_coincidencias(texto, base_problemas)

        mostrar_top_coincidencias(top)
        responder(top)


if __name__ == "__main__":
    main()

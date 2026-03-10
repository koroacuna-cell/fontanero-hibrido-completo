#!/usr/bin/env python3
import json
from difflib import SequenceMatcher
import unicodedata

# ================================
#   CONFIGURACIÓN DEL SISTEMA
# ================================
ARCHIVO_BD = "bd_problemas.json"

UMBRAL_MINIMO = 0.35        # Acepta coincidencias más flojas
UMBRAL_ADVERTENCIA = 0.75
UMBRAL_VERDE = 0.90

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

def normalizar_texto(texto):
    """Normaliza texto: minúsculas, sin acentos, espacios → guiones bajos."""
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.replace(' ', '_')
    return texto

def obtener_mejores_coincidencias(texto_usuario, base_problemas):
    """Devuelve el TOP 3 de mejores coincidencias usando texto normalizado."""
    texto_normalizado = normalizar_texto(texto_usuario)
    puntuaciones = []

    for clave, datos in base_problemas.items():
        clave_normalizada = normalizar_texto(clave)
        similitud = calcular_similitud(texto_normalizado, clave_normalizada)
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
    clave, similitud, datos = top[0]

    if similitud < UMBRAL_MINIMO:
        print("\n=== RESPUESTA FINAL ===")
        print("❓ No entiendo bien el problema.")
        print("Por favor, escribe una descripción más clara o diferente.\n")
        print("------------------------------")
        return

    print("\n=== RESPUESTA FINAL ===")
    respuesta = datos.get("respuesta")
    if isinstance(respuesta, list):
        for paso in respuesta:
            print("✔️ " + paso)
    elif isinstance(respuesta, str):
        print("✔️ " + respuesta)
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

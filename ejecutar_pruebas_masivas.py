#!/usr/bin/env python3
import sys

def leer_problemas():
    if not sys.stdin.isatty():  # Entrada viene de pipe/archivo
        lineas = sys.stdin.read().split("\n")
        return [l.strip() for l in lineas if l.strip()]
    
    # Entrada interactiva normal
    print("🤖 Fontanero Virtual activo. Escribe tus problemas separados por salto de línea, o 'salir' para terminar.")
    print("💬 Describe tu problema(s) (termina con una línea vacía):")
    problemas = []
    while True:
        linea = input().strip()
        if linea.lower() == "salir" or linea == "":
            break
        problemas.append(linea)
    return problemas

def procesar_problema(problema):
    # Diccionario simplificado, añade más entradas según tu maestro_local.json
    respuestas = {
        "grifo goteando": [
            "Cierra el paso de agua del lavabo o cocina.",
            "Revisa si el goteo viene del cartucho interior.",
            "Si puedes, manda una foto por WhatsApp 📸 para confirmar el tipo de grifo.",
            "El cambio de cartucho suele costar menos que cambiar el grifo entero."
        ],
        "ducha pierde agua": [
            "Localiza si la fuga viene de una junta, tubería o desagüe.",
            "Si puedes, manda una foto por WhatsApp 📸 para ver si es reparación o cambio.",
            "Si es en pared, toca alrededor para ver si está húmedo.",
            "Cierra el paso general si la fuga es fuerte."
        ],
        "cisterna pierde agua": [
            "Levanta la tapa y revisa si flota bien el mecanismo.",
            "Muchas veces se arregla cambiando la boya.",
            "Envíame foto del interior para decirte si vale reparar o toca cambiar."
        ],
        "lavadora no enciende": [
            "Envía fotos del panel o de la avería por WhatsApp 📸.",
            "Te indicaré cómo solucionarlo o si hace falta la intervención de un técnico."
        ],
        "tubería rota": [
            "Localiza la tubería dañada.",
            "Cierra el paso general de agua.",
            "Contacta con un técnico si es necesario."
        ]
    }
    clave = problema.lower().strip()
    return respuestas.get(clave, ["❌ Problema no encontrado. Envía foto por WhatsApp 📸."])

def main():
    problemas = leer_problemas()
    for i, p in enumerate(problemas, 1):
        resp = procesar_problema(p)
        print(f"=== Problema {i}: {p} ===")
        for r in resp:
            print(f"- {r}")
        print("-" * 30)

if __name__ == "__main__":
    main()

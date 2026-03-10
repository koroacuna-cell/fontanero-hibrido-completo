import json
import unicodedata

archivo_local = "maestro_local.json"

# Cargamos la base de datos de problemas
with open(archivo_local, "r", encoding="utf-8") as f:
    data = json.load(f)

def normalizar(texto):
    """Convierte texto a minúsculas y elimina acentos"""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def buscar_solucion(problema, numero):
    problema_norm = normalizar(problema)
    # Primero buscamos coincidencia exacta en etiquetas
    for entrada in data:
        etiqueta_norm = normalizar(entrada.get("etiqueta", ""))
        if problema_norm == etiqueta_norm:
            print(f"\n=== Problema {numero}: {entrada['etiqueta']} ===")
            print("🔧 Resultado:")
            for paso in entrada.get("respuesta", []):
                print("-", paso)
            print("-" * 30)
            return True
    # Coincidencia parcial por palabras
    for entrada in data:
        palabras = " ".join(entrada.get("palabras", []))
        palabras_norm = normalizar(palabras)
        if any(p in palabras_norm for p in problema_norm.split()):
            print(f"\n=== Problema {numero}: {entrada['etiqueta']} ===")
            print("🔧 Resultado:")
            for paso in entrada.get("respuesta", []):
                print("-", paso)
            print("-" * 30)
            return True
    # Si no hay coincidencia
    print(f"\n=== Problema {numero}: {problema} ===")
    print("❌ No he encontrado una solución para eso. Envía foto por WhatsApp 📸 y te ayudaré.")
    print("-" * 30)
    return False

def main():
    print("🤖 Fontanero Virtual activo. Escribe tus problemas separados por salto de línea, o 'salir' para terminar.")
    while True:
        problemas = []
        print("\n💬 Describe tus problema(s) (termina con una línea vacía):")
        while True:
            linea = input().strip()
            if linea.lower() in ["salir", "exit"]:
                print("¡Hasta luego!")
                return
            if linea == "":
                break
            problemas.append(linea)
        for i, problema in enumerate(problemas, start=1):
            buscar_solucion(problema, i)

if __name__ == "__main__":
    main()

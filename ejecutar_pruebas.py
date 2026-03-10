import json
import difflib

# Cargar maestro_local.json
with open("maestro_local.json", "r", encoding="utf-8") as f:
    maestro_local = json.load(f)

def buscar_respuesta(problema, maestro_local):
    problema_limpio = problema.lower().strip()

    # 1️⃣ Coincidencia exacta
    for entry in maestro_local:
        for palabra in entry["palabras"]:
            if problema_limpio == palabra.lower().strip():
                return entry["respuesta"]

    # 2️⃣ Coincidencia aproximada
    all_palabras = []
    entry_map = {}
    for entry in maestro_local:
        for palabra in entry["palabras"]:
            palabra_limpia = palabra.lower().strip()
            all_palabras.append(palabra_limpia)
            entry_map[palabra_limpia] = entry["respuesta"]

    matches = difflib.get_close_matches(problema_limpio, all_palabras, n=1, cutoff=0.6)
    if matches:
        return entry_map[matches[0]]

    # 3️⃣ Respuesta por defecto
    return ["❌ No he encontrado una solución para eso. Envía foto por WhatsApp 📸 y te ayudaré."]

# Bucle de pruebas individuales
print("🤖 Fontanero Virtual activo. Escribe tu problema o 'salir' para terminar.")
while True:
    problema = input("💬 Describe tu problema: ").strip()
    if problema.lower() == "salir":
        break
    respuesta = buscar_respuesta(problema, maestro_local)
    print("🔧 Resultado:")
    for r in respuesta:
        print("-", r)
    print("-" * 30)

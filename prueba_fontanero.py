import json

# Cargar maestro.json
with open("maestro.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Crear mapa rápido de alias a clave
alias_map = {}
for key, value in data.items():
    for a in value.get("alias", []):
        alias_map[a.lower()] = key

def buscar_clave(msg):
    msg_lower = msg.lower()
    if msg_lower in data:
        return msg_lower
    if msg_lower in alias_map:
        return alias_map[msg_lower]
    return None

print("=== Fontanero Virtual - Prueba interactiva ===")
print("Escribe 'salir' para terminar.\n")

while True:
    msg = input("Ingresa problema, grifo, tubería, termo, etc.: ")
    if msg.lower() == "salir":
        print("Fin de la prueba.")
        break
    
    clave = buscar_clave(msg)
    if clave:
        pasos = data[clave].get("pasos", [])
        print(f"\nPasos para '{clave}':")
        for i, p in enumerate(pasos, 1):
            print(f"{i}. {p}")
        print("\n---\n")
    else:
        print("No se encontró el problema. Intenta con otra descripción o alias.\n")
import json

# Cargamos el maestro_local.json
archivo = "maestro_local.json"
with open(archivo, "r", encoding="utf-8") as f:
    data = json.load(f)

# Creamos un diccionario rápido de búsqueda
diccionario = {entrada["etiqueta"]: entrada for entrada in data}

print("=== FONTANERO VIRTUAL DE PRUEBA ===")
print("Escribe 'salir' para terminar.\n")

while True:
    problema = input("Describe tu problema: ").strip().lower()
    if problema == "salir":
        print("¡Hasta luego!")
        break

    # Buscamos coincidencia simple por palabras
    encontrado = False
    for entrada in data:
        palabras = " ".join(entrada.get("palabras", [])).lower()
        if problema in palabras:
            print("\n🔧 Resultado para:", entrada["etiqueta"])
            for paso in entrada.get("respuesta", []):
                print("-", paso)
            print("-" * 30)
            encontrado = True
            break

    if not encontrado:
        print("❌ No he encontrado una solución para eso. Envía foto por WhatsApp 📸 y te ayudaré.")
        print("-" * 30)

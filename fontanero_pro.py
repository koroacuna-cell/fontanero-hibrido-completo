import json
import difflib

# ===============================
#   FONTANERO VIRTUAL — PRO v4
#   Usa maestro.json
# ===============================

def cargar_maestro():
    try:
        with open("maestro.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ERROR al cargar maestro.json: {e}")
        exit()

DATA = cargar_maestro()


# Construir índice (claves + alias)
def construir_indice(data):
    indice = {}
    for clave, contenido in data.items():
        indice[clave.lower()] = clave
        if "alias" in contenido:
            for a in contenido["alias"]:
                indice[a.lower()] = clave
    return indice

INDICE = construir_indice(DATA)


# Mejor coincidencia con difflib
def buscar_clave(texto):
    texto = texto.lower()
    opciones = list(INDICE.keys())
    match = difflib.get_close_matches(texto, opciones, n=1, cutoff=0.53)
    if match:
        return INDICE[match[0]]
    return None


# Mostrar pasos
def mostrar_respuesta(clave):
    pasos = DATA[clave]["pasos"]
    print(f"\n🔧 Problema detectado: **{clave}**")
    for i, p in enumerate(pasos, 1):
        print(f"{i}. {p}")
    print("---------------------------\n")


# BUCLE PRINCIPAL
print("=== FONTANERO VIRTUAL — PRO v4 ===")
print("Escribe 'salir' para terminar.\n")

while True:
    texto = input("Describe tu problema: ").strip()
    if texto.lower() == "salir":
        break

    clave = buscar_clave(texto)

    if clave:
        mostrar_respuesta(clave)
    else:
        print("❌ No encontré coincidencias. Intenta describirlo de otra forma.\n")

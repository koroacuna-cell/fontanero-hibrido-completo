import json
import difflib

# Cargar archivo maestro directamente como diccionario plano
def cargar_maestro():
    try:
        with open("maestro_fontanero.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ERROR al cargar maestro: {e}")
        exit()

DATA = cargar_maestro()

# Convertir claves y alias en un índice unificado
def construir_indice(data):
    indice = {}
    for clave, contenido in data.items():
        indice[clave] = clave  # clave principal
        if "alias" in contenido:
            for a in contenido["alias"]:
                indice[a.lower()] = clave
    return indice

INDICE = construir_indice(DATA)

# Buscar mejor coincidencia por difflib
def buscar_mejor_coincidencia(texto):
    texto = texto.lower()
    posibles = list(INDICE.keys())
    coincidencias = difflib.get_close_matches(texto, posibles, n=1, cutoff=0.55)
    if coincidencias:
        return INDICE[coincidencias[0]]
    return None

# Mostrar pasos
def mostrar_respuesta(clave):
    pasos = DATA[clave]["pasos"]
    print(f"\n🔧 Resultado para: **{clave}**\n")
    for i, p in enumerate(pasos, 1):
        print(f"{i}. {p}")
    print("-----------------------------\n")

# Bucle principal
print("=== FONTANERO VIRTUAL PRO — Versión 3 ===")
print("Escribe 'salir' para terminar.\n")

while True:
    texto = input("Describe tu problema: ").strip()
    if texto.lower() == "salir":
        break

    clave = buscar_mejor_coincidencia(texto)

    if clave:
        mostrar_respuesta(clave)
    else:
        print("❌ No encontré coincidencias. Intenta describirlo de otra forma.\n")

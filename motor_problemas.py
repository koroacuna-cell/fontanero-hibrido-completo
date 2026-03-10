import json
import os

# ----------------------------------------------
#     CARGA DEL JSON CON LISTA DE PROBLEMAS
# ----------------------------------------------
def cargar_problemas(ruta="problemas_v2.json"):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"❌ No se encontró el archivo JSON: {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

problemas = cargar_problemas()


# ----------------------------------------------
#     OBTENER SOLUCIÓN SEGÚN CATEGORÍA / PROBLEMA
# ----------------------------------------------
def obtener_solucion(categoria, problema):
    """
    Devuelve la solución exacta desde el JSON.
    """
    try:
        return problemas[categoria][problema]["solucion"]
    except KeyError:
        return "❌ No existe solución definida para este problema."


# ----------------------------------------------
#     MAPA SIMPLE DE PALABRAS CLAVE (DETECTOR)
# ----------------------------------------------
CATEGORIAS_CLAVE = {
    "cisterna": ["cisterna", "wc", "inodoro", "váter"],
    "ducha": ["ducha", "agua fría", "temperatura", "presión"],
    "grifo": ["grifo", "lavabo", "fuga", "cartucho"],
    "tuberia": ["tubería", "desagüe", "atascada", "gotea"],
    "calentador_caldera": ["calentador", "caldera", "no enciende"],
    "presion_general": ["presión", "flujo", "baja"],
    "fuga_general": ["fuga", "agua", "charco"],
    "bomba_agua": ["bomba"],
}

PROBLEMAS_CLAVE = {
    "goteando": ["gotea", "goteando", "fuga", "pierde"],
    "fria": ["fría", "agua fría", "no calienta"],
    "intermitente": ["intermitente", "cambia", "va y viene"],
    "presion_baja": ["baja presión", "flujo bajo", "poca agua"],
    "obstruida": ["atascada", "obstruida", "tapón"],
    "ruidosa": ["ruidosa", "ruido", "sonido extraño"],
    "no_enciende": ["no enciende", "no arranca"],
    "desmontada": ["desmontada", "desarmada"],
    "cartucho_dañado": ["cartucho", "no abre", "duro"],
    "sedimentada": ["cal", "suciedad", "sedimentos"],
}


# ----------------------------------------------
#     DETECCIÓN AUTOMÁTICA
# ----------------------------------------------
def detectar_categoria_y_problema(texto):
    """
    Escanea el texto del usuario y determina la mejor categoría y tipo de problema.
    """
    texto = texto.lower()

    categoria_detectada = None
    problema_detectado = None

    # Detectar categoría
    for categoria, claves in CATEGORIAS_CLAVE.items():
        if any(k in texto for k in claves):
            categoria_detectada = categoria
            break

    # Detectar problema
    for problema, claves in PROBLEMAS_CLAVE.items():
        if any(k in texto for k in claves):
            problema_detectado = problema
            break

    return categoria_detectada, problema_detectado


# ----------------------------------------------
#     MOTOR PRINCIPAL
# ----------------------------------------------
def resolver_problema(texto_usuario):
    categoria, problema = detectar_categoria_y_problema(texto_usuario)

    if categoria and problema:
        solucion = obtener_solucion(categoria, problema)
        return f"✔️ Categoría: {categoria}\n✔️ Problema: {problema}\n💡 Solución: {solucion}"

    if categoria and not problema:
        return f"✔️ Categoría detectada: {categoria}\n❓ Pero no se detectó un problema exacto."

    return "❌ No se pudo detectar el tipo de problema. Describe la situación con más detalle."


# ----------------------------------------------
#     MODO CONSOLA (LLAMADA INTERACTIVA)
# ----------------------------------------------
if __name__ == "__main__":
    print("🛠️ Motor de diagnóstico Fontanero — modo consola")
    while True:
        texto = input("💬 Describe el problema (o 'salir'): ").strip()
        if texto.lower() == "salir":
            break
        print(resolver_problema(texto))
        print("-" * 40)
import json

# Cargar el JSON de problemas
with open("problemas_v2.json", "r", encoding="utf-8") as f:
    problemas = json.load(f)

def obtener_solucion(categoria, problema):
    try:
        return problemas[categoria][problema]["solucion"]
    except KeyError:
        return "No se encontró solución para este problema."

def buscar_categoria_y_problema(texto_usuario):
    texto = texto_usuario.lower()
    categorias = {
        "cisterna": ["cisterna", "inodoro", "váter"],
        "ducha": ["ducha", "agua fría", "presión", "temperatura"],
        "grifo": ["grifo", "lavabo", "fuga", "cartucho"],
        "tuberia": ["tubería", "desagüe", "atascada", "gotea"],
        "calentador_caldera": ["calentador", "caldera", "no enciende", "temperatura"],
        "presion_general": ["presión", "baja", "flujo"],
        "fuga_general": ["fuga", "agua"],
        "bomba_agua": ["bomba"]
    }
    problemas_clave = {
        "lenta": ["lenta", "tarda", "llenado lento"],
        "ruidosa": ["ruidosa", "sonido extraño", "ruido"],
        "pierde_agua": ["pierde", "fuga", "gota"],
        "rellena_rapido": ["rapido", "llena rápido"],
        "fria": ["fría", "agua fría"],
        "intermitente": ["intermitente", "cambia", "va y viene"],
        "obstruida": ["obstruida", "atascada", "tapón"],
        "presion_baja": ["baja presión", "flujo bajo"],
        "temperatura_irregular": ["temperatura irregular", "cambia temperatura"],
        "base_fuga": ["fuga base", "gotea base"],
        "caliente_no_sale": ["caliente no sale", "agua caliente no sale"],
        "flujo_bajo": ["flujo bajo", "poco agua"],
        "gotea": ["gotea", "fuga"],
        "desmontado": ["desmontado", "no armado"],
        "cartucho_dañado": ["cartucho dañado", "cartucho roto"],
        "suelto": ["suelto", "movible"],
        "filtrando": ["filtrando", "pequeña fuga"],
        "goteando": ["goteando", "pierde agua"],
        "atascada": ["atascada", "bloqueada"],
        "desmontada": ["desmontada", "desarmada"],
        "sedimentada": ["sedimentada", "suciedad", "cal"],
        "desague_lento": ["desagüe lento", "agua no baja"],
        "no_sale_agua": ["no sale agua", "taponado"],
        "no_enciende": ["no enciende", "sin luz"],
        "no_calienta": ["no calienta", "agua fría"],
        "baja": ["baja presión", "flujo insuficiente"],
        "agua": ["fuga agua", "pierde agua"],
        "falla": ["falla", "no funciona"]
    }
    categoria_detectada = None
    problema_detectado = None
    for cat, palabras in categorias.items():
        if any(p in texto for p in palabras):
            categoria_detectada = cat
            break
    for prob, palabras in problemas_clave.items():
        if any(p in texto for p in palabras):
            problema_detectado = prob
            break
    return categoria_detectada, problema_detectado

def responder(texto_usuario):
    categoria, problema = buscar_categoria_y_problema(texto_usuario)
    if categoria and problema:
        solucion = obtener_solucion(categoria, problema)
        return f"✔️ Solución: {solucion}"
    elif categoria:
        return f"❓ Se encontró la categoría '{categoria}', pero no se detectó el problema exacto."
    else:
        return "❓ No se pudo identificar la categoría ni el problema. Por favor, describe de otra forma."

while True:
    texto = input("💬 Describe tu problema (o 'salir'): ").strip()
    if texto.lower() == "salir":
        break
    print(responder(texto))

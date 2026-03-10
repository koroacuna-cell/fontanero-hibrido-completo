import json

with open("problemas_v2.json", "r", encoding="utf-8") as f:
    problemas = json.load(f)

def obtener_solucion(categoria, problema):
    try:
        return problemas[categoria][problema]["solucion"]
    except KeyError:
        return None

def buscar_categoria_y_problema(texto_usuario):
    texto = texto_usuario.lower()

    categorias = {
        "cisterna": ["cisterna", "inodoro", "váter"],
        "ducha": ["ducha", "agua fría", "presión", "temperatura"],
        "grifo": ["grifo", "lavabo", "fuga", "cartucho"],
        "tuberia": ["tubería", "desagüe", "atascada", "gotea"],
        "calentador_caldera": ["calentador", "caldera"],
        "presion_general": ["presión", "baja"],
        "fuga_general": ["fuga"],
        "bomba_agua": ["bomba"]
    }

    problemas_clave = {
        "intermitente": ["intermitente", "cambia", "va y viene"],
        "lenta": ["lenta", "tarda"],
        "ruidosa": ["ruido", "ruidosa"],
        "presion_baja": ["baja presión", "flujo"],
        "fria": ["fría"],
        "obstruida": ["atascada", "obstruida"],
        "gotea": ["gotea", "fuga"],
        "no_enciende": ["no enciende"],
        "no_calienta": ["no calienta"],
        "temperatura_irregular": ["temperatura irregular"],
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
        sol = obtener_solucion(categoria, problema)
        if sol:
            return f"✔️ Solución: {sol}"

    return "❓ No pude identificar el problema exacto."

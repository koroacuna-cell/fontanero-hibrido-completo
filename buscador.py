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
        "fria": ["fría", "agua fría"],
        "intermitente": ["intermitente", "cambia", "va y viene"],
        "presion_baja": ["baja presión", "flujo bajo"],
        "temperatura_irregular": ["temperatura irregular", "cambia temperatura"],
        "sedimentada": ["sedimentada", "cal", "suciedad"],
        "no_enciende": ["no enciende"],
        "no_calienta": ["no calienta"],
        "gotea": ["gotea"],
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

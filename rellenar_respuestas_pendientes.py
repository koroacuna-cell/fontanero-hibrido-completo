import json
import shutil

archivo_local = "maestro_local.json"

# Crear copia de seguridad
shutil.copy2(archivo_local, archivo_local + ".bak_pendientes")
print(f"✅ Copia de seguridad creada: {archivo_local}.bak_pendientes")

# Cargar archivo
with open(archivo_local, "r", encoding="utf-8") as f:
    data = json.load(f)

# Respuestas sugeridas para entradas pendientes
respuestas_sugeridas = {
    "caldera_no_enciende": [
        "Comprueba si tiene alimentación eléctrica.",
        "Revisa el piloto o el sistema de encendido.",
        "Si es de gas, verifica la válvula y el suministro de gas.",
        "Si persiste, envía foto por WhatsApp 📸 y te indicaré la solución o si hace falta técnico."
    ],
    "tubería_rota": [
        "Cierra el paso general de agua.",
        "Localiza la zona afectada y revisa si es reparación o sustitución.",
        "Envía foto por WhatsApp 📸 si es necesario."
    ],
    "grifo_de_lavabo_gotea": [
        "Cierra el paso de agua del lavabo.",
        "Revisa cartucho o juntas del grifo.",
        "Envía foto por WhatsApp 📸 para confirmar tipo de grifo."
    ],
    "ducha_fría": [
        "Revisa el calentador y presión de agua.",
        "Comprueba válvulas mezcladoras.",
        "Envía foto por WhatsApp 📸 si no se soluciona."
    ]
}

# Rellenar solo entradas pendientes
for entrada in data:
    etiqueta = entrada.get("etiqueta")
    if entrada.get("respuesta") == ["Pendiente de definir respuesta. (Aún sin contenido)"] and etiqueta in respuestas_sugeridas:
        entrada["respuesta"] = respuestas_sugeridas[etiqueta]
        print(f"✅ Respuesta agregada para: {etiqueta}")

# Guardar archivo actualizado
with open(archivo_local, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ maestro_local.json actualizado con todas las respuestas pendientes completadas.")

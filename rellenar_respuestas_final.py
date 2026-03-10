import json
import shutil

archivo_local = "maestro_local.json"

# Copia de seguridad antes de cambios
shutil.copy2(archivo_local, archivo_local + ".bak_final_respuestas")
print(f"✅ Copia de seguridad creada: {archivo_local}.bak_final_respuestas")

# Cargamos archivo
with open(archivo_local, "r", encoding="utf-8") as f:
    data = json.load(f)

# Diccionario con las respuestas que faltan
respuestas_sugeridas = {
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

# Actualizamos solo entradas pendientes
for entrada in data:
    etiqueta = entrada.get("etiqueta")
    if entrada.get("respuesta") == ["Pendiente de definir respuesta"] or "Pendiente de definir respuesta" in entrada.get("respuesta", []):
        if etiqueta in respuestas_sugeridas:
            entrada["respuesta"] = respuestas_sugeridas[etiqueta]
            print(f"✅ Respuesta agregada para: {etiqueta}")

# Guardamos archivo actualizado
with open(archivo_local, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ maestro_local.json actualizado: todas las respuestas completadas.")

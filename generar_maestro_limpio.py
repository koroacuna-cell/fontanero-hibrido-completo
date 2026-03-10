import json

# Cargar maestro actual
with open("maestro_local.json", encoding="utf-8") as f:
    maestro = json.load(f)

# Diccionario para consolidar etiquetas
maestro_limpio = {}

for entry in maestro:
    etiqueta = entry["etiqueta"].lower()
    
    if etiqueta not in maestro_limpio:
        maestro_limpio[etiqueta] = {
            "etiqueta": entry["etiqueta"],
            "sinonimos": entry.get("sinonimos", []),
            "respuesta": entry.get("respuesta", [])
        }
    else:
        # Agregar sinónimos sin duplicados
        for s in entry.get("sinonimos", []):
            if s not in maestro_limpio[etiqueta]["sinonimos"]:
                maestro_limpio[etiqueta]["sinonimos"].append(s)
        # Agregar respuestas sin duplicados
        for r in entry.get("respuesta", []):
            if r not in maestro_limpio[etiqueta]["respuesta"]:
                maestro_limpio[etiqueta]["respuesta"].append(r)

# Guardar maestro limpio
with open("maestro_local_limpio.json", "w", encoding="utf-8") as f:
    json.dump(list(maestro_limpio.values()), f, ensure_ascii=False, indent=4)

print("✅ maestro_local_limpio.json generado correctamente")

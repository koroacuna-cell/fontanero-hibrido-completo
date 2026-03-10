import json
import shutil

archivo_local = "maestro_local.json"

# Crear copia de seguridad
shutil.copy2(archivo_local, archivo_local + ".bak_respuestas")
print(f"✅ Copia de seguridad creada: {archivo_local}.bak_respuestas")

# Cargar archivo
with open(archivo_local, "r", encoding="utf-8") as f:
    data = json.load(f)

# Revisar y arreglar respuestas
for entrada in data:
    resp = entrada.get("respuesta", [])
    # Si la respuesta es string, la convertimos a lista
    if isinstance(resp, str):
        entrada["respuesta"] = [resp]
    # Si es lista, verificamos que cada elemento sea string
    elif isinstance(resp, list):
        entrada["respuesta"] = [str(p) for p in resp]

# Guardar archivo limpio
with open(archivo_local, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ maestro_local.json actualizado: todas las respuestas son listas")

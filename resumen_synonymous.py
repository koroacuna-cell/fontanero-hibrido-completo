import json

# Cargar JSON limpio
with open("maestro_local_limpio.json", encoding="utf-8") as f:
    maestro = json.load(f)

# Construir diccionario de etiquetas con sus sinónimos
resumen = {}
for entry in maestro:
    etiqueta = entry["etiqueta"]
    sinco_list = [etiqueta] + entry.get("sinonimos", [])
    resumen[etiqueta] = sinco_list

# Imprimir resumen
print("=== RESUMEN DE COINCIDENCIAS POR ETIQUETA ===\n")
for etiqueta, sinco_list in resumen.items():
    print(f"🔧 {etiqueta}")
    for s in sinco_list:
        print(f" - {s}")
    print("-" * 50)
print("=== FIN DEL RESUMEN ===")
